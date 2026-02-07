#!/usr/bin/env python3
"""Three-panel overlay with quantitative metrics and JSON output.

Generates the same three-panel figures (SPD vs events) as
compare_publication_three_panel.py, but also computes metrics and saves
all curves + metrics to JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import visualize_cumulative_weighted as vcw  # noqa: E402
from compare_reconstruction_to_gt import (  # noqa: E402
    detect_active_region,
    load_ground_truth,
    moving_average,
    normalise_curve,
)
from compare_publication_cumulative import (  # noqa: E402
    detect_visible_edges,
    ensure_output_dir,
    publication_style,
)


def build_cumulative_and_bins(
    segment_npz: Path,
    step_ms: float,
    bin_ms: float,
    pos_scale: float,
    auto_bounds: Tuple[float, float],
    plateau_frac: float,
    sensor_width: int,
    sensor_height: int,
) -> Tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray]:
    x, y, t, p = vcw.load_npz_events(str(segment_npz))
    t_min, t_max = float(np.min(t)), float(np.max(t))

    param_file = vcw.find_param_file_for_segment(str(segment_npz))
    if param_file is None:
        raise FileNotFoundError("No learned parameter NPZ found next to segment")
    params = vcw.load_parameters_from_npz(param_file)
    t_comp, *_ = vcw.compute_fast_compensated_times(x, y, t, params["a_params"], params["b_params"])

    # Polarity is stored as {0,1} in our NPZ; treat >0 as positive.
    pos_mask = p > 0
    neg_mask = ~pos_mask
    hw = float(sensor_width * sensor_height)

    step_us_cum = step_ms * 1000.0
    sums_pos_cum, edges_ms_cum = vcw.base_binned_sums_weighted(
        t_comp[pos_mask], np.ones(np.count_nonzero(pos_mask), dtype=np.float32), t_min, t_max, step_us_cum
    )
    sums_neg_cum, _ = vcw.base_binned_sums_weighted(
        t_comp[neg_mask], np.ones(np.count_nonzero(neg_mask), dtype=np.float32), t_min, t_max, step_us_cum
    )

    def build_cum(neg_scale: float) -> np.ndarray:
        step_sums = pos_scale * sums_pos_cum - neg_scale * sums_neg_cum
        return np.cumsum(step_sums) / hw

    def plateau_diff(neg_scale: float) -> float:
        series = np.exp(build_cum(neg_scale))
        k = len(series)
        if k <= 2:
            return 0.0
        n = max(5, int(plateau_frac * k))
        return float(np.mean(series[-n:]) - np.mean(series[:n]))

    neg_min, neg_max = auto_bounds
    f_min, f_max = plateau_diff(neg_min), plateau_diff(neg_max)
    if f_min * f_max < 0:
        for _ in range(40):
            mid = 0.5 * (neg_min + neg_max)
            f_mid = plateau_diff(mid)
            if abs(f_mid) < 1e-6:
                neg_min = neg_max = mid
                break
            if f_min * f_mid < 0:
                neg_max, f_max = mid, f_mid
            else:
                neg_min, f_min = mid, f_mid
        chosen_neg = 0.5 * (neg_min + neg_max)
    else:
        grid = np.linspace(neg_min, neg_max, 50)
        vals = np.array([abs(plateau_diff(g)) for g in grid])
        chosen_neg = float(grid[int(np.argmin(vals))])

    cum_linear = build_cum(chosen_neg)
    cum_exp = np.exp(cum_linear)
    time_ms_cum = edges_ms_cum - edges_ms_cum[0]

    step_us_bin = bin_ms * 1000.0
    sums_pos_bin, edges_ms_bin = vcw.base_binned_sums_weighted(
        t_comp[pos_mask], np.ones(np.count_nonzero(pos_mask), dtype=np.float32), t_min, t_max, step_us_bin
    )
    sums_neg_bin, _ = vcw.base_binned_sums_weighted(
        t_comp[neg_mask], np.ones(np.count_nonzero(neg_mask), dtype=np.float32), t_min, t_max, step_us_bin
    )
    net_bin = sums_pos_bin - sums_neg_bin

    time_ms_bin = edges_ms_bin - edges_ms_cum[0]
    return time_ms_cum, cum_exp, chosen_neg, time_ms_bin, net_bin


def load_gt_curves(files: Sequence[Path]) -> List[Tuple[str, np.ndarray, np.ndarray]]:
    curves: List[Tuple[str, np.ndarray, np.ndarray]] = []
    for txt in files:
        wl, val = load_ground_truth(txt)
        curves.append((txt.stem, wl, val))
    if not curves:
        raise FileNotFoundError("No ground-truth files supplied")
    return curves


def align_reconstruction_to_gt(
    time_ms: np.ndarray,
    series_exp: np.ndarray,
    gt_curves: Sequence[Tuple[str, np.ndarray, np.ndarray]],
) -> Tuple[np.ndarray, np.ndarray, float, float, np.ndarray, np.ndarray]:
    gt_start_nm, gt_end_nm = detect_visible_edges(gt_curves)

    name0, wl0_raw, val0_raw = gt_curves[0]
    mask0 = (wl0_raw >= 300.0) & (wl0_raw <= 900.0)
    wl0 = wl0_raw[mask0]
    val0 = val0_raw[mask0]
    smooth0 = moving_average(val0, max(21, len(val0) // 300))
    region0 = detect_active_region(smooth0)
    gt_norm = normalise_curve(smooth0, region0)

    smooth_rec = moving_average(series_exp, max(21, int(len(series_exp) // 200) | 1))
    region_rec = detect_active_region(smooth_rec)
    recon_norm = normalise_curve(series_exp, region_rec)
    t0 = float(time_ms[region_rec.start_idx])
    t1 = float(time_ms[region_rec.end_idx])
    if t1 <= t0:
        raise ValueError("Detected non-increasing active region in reconstruction")
    slope = (gt_end_nm - gt_start_nm) / (t1 - t0)
    intercept = gt_start_nm - slope * t0
    wl_recon = slope * time_ms + intercept

    return wl_recon, recon_norm, slope, intercept, wl0, gt_norm


def rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(len(x), dtype=float)
    return ranks


def compute_metrics(ref_wl: np.ndarray, ref: np.ndarray, pred_wl: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    wl_min = max(float(np.min(ref_wl)), float(np.min(pred_wl)))
    wl_max = min(float(np.max(ref_wl)), float(np.max(pred_wl)))
    if wl_max <= wl_min:
        return {"pearson_r": float("nan"), "spearman_r": float("nan"), "rmse": float("nan"), "nrmse": float("nan"), "mae": float("nan"), "r2": float("nan")}

    n = int(max(len(ref_wl), len(pred_wl), 200))
    grid = np.linspace(wl_min, wl_max, n)
    ref_i = np.interp(grid, ref_wl, ref)
    pred_i = np.interp(grid, pred_wl, pred)

    ref_mean = float(np.mean(ref_i))
    pred_mean = float(np.mean(pred_i))
    ref_std = float(np.std(ref_i))
    pred_std = float(np.std(pred_i))
    if ref_std > 0 and pred_std > 0:
        pearson = float(np.corrcoef(ref_i, pred_i)[0, 1])
    else:
        pearson = float("nan")

    ref_rank = rankdata(ref_i)
    pred_rank = rankdata(pred_i)
    if np.std(ref_rank) > 0 and np.std(pred_rank) > 0:
        spearman = float(np.corrcoef(ref_rank, pred_rank)[0, 1])
    else:
        spearman = float("nan")

    diff = pred_i - ref_i
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    denom = float(np.max(ref_i) - np.min(ref_i))
    nrmse = float(rmse / denom) if denom > 0 else float("nan")
    mae = float(np.mean(np.abs(diff)))

    ss_res = float(np.sum(diff ** 2))
    ss_tot = float(np.sum((ref_i - ref_mean) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")

    return {
        "pearson_r": pearson,
        "spearman_r": spearman,
        "rmse": rmse,
        "nrmse": nrmse,
        "mae": mae,
        "r2": r2,
    }


def build_events_norm(net_bin: np.ndarray) -> np.ndarray:
    if net_bin.size:
        smooth_events = moving_average(net_bin, max(5, len(net_bin) // 200 | 1))
        smooth_events = smooth_events - float(np.mean(smooth_events))
    else:
        smooth_events = net_bin
    if np.max(np.abs(smooth_events)) > 0:
        return smooth_events / np.max(np.abs(smooth_events))
    return smooth_events


def run_dataset(
    segment: Path,
    gt_files: Sequence[Path],
    suffix: str,
    args: argparse.Namespace,
) -> Tuple[Path, Path]:
    time_ms_cum, cum_exp, neg_scale, time_ms_bin, net_bin = build_cumulative_and_bins(
        segment,
        step_ms=args.step_ms,
        bin_ms=args.bin_ms,
        pos_scale=args.pos_scale,
        auto_bounds=(args.auto_neg_min, args.auto_neg_max),
        plateau_frac=args.plateau_frac,
        sensor_width=args.sensor_width,
        sensor_height=args.sensor_height,
    )

    gt_curves = load_gt_curves(gt_files)
    wl_recon, recon_norm, slope, intercept, wl_gt, gt_norm = align_reconstruction_to_gt(
        time_ms_cum, cum_exp, gt_curves
    )

    wl_bins = slope * time_ms_bin + intercept

    eps = 1e-3
    log_gt = np.log(np.clip(gt_norm, eps, None))
    log_recon = np.log(np.clip(recon_norm, eps, None))

    dlog_gt = np.gradient(log_gt, wl_gt)
    dlog_gt_norm = dlog_gt / np.max(np.abs(dlog_gt)) if np.max(np.abs(dlog_gt)) > 0 else dlog_gt

    events_norm = build_events_norm(net_bin)

    # Metrics
    metrics = {
        "cumulative": compute_metrics(wl_gt, gt_norm, wl_recon, recon_norm),
        "log": compute_metrics(wl_gt, log_gt, wl_recon, log_recon),
        "derivative_vs_events": compute_metrics(wl_gt, dlog_gt_norm, wl_bins, events_norm),
    }

    out_dir = ensure_output_dir(args.output_root)
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.6), sharex=True)
    ax1, ax2, ax3 = axes
    for ax in axes:
        ax.xaxis.labelpad = 2

    visible_min, visible_max = 380.0, 780.0
    xmin = max(args.xlim[0], visible_min)
    xmax = min(args.xlim[1], visible_max)

    ax1.axvspan(380, 780, color="0.92", zorder=0)
    ax1.plot(wl_gt, gt_norm, color="#1f77b4", label="SPD")
    ax1.plot(wl_recon, recon_norm, color="#2ca02c", label="Events")
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("Normalised intensity")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="upper right")

    ax2.axvspan(380, 780, color="0.92", zorder=0)
    ax2.plot(wl_gt, log_gt, color="#1f77b4", label="GT")
    ax2.plot(wl_recon, log_recon, color="#2ca02c", label="Recon")
    ax2.set_xlim(xmin, xmax)
    ax2.set_xlabel("Wavelength (nm)")
    ax2.set_ylabel("log intensity")
    ax2.grid(alpha=0.3)

    ax3.axvspan(380, 780, color="0.92", zorder=0)
    ax3.plot(wl_gt, dlog_gt_norm, color="#1f77b4")
    ax3.plot(wl_bins, events_norm, color="#2ca02c")
    ax3.set_xlim(xmin, xmax)
    ax3.set_xlabel("Wavelength (nm)")
    ax3.set_ylabel("d log(SPD)/dλ, Event Density")
    ax3.grid(alpha=0.3)

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))

    seg_name = segment.stem.replace("_events", "")
    suffix_tag = f"_{suffix}" if suffix else ""
    out_name = f"three_panel_{args.bin_ms:.0f}ms_{seg_name}{suffix_tag}_metrics.png"
    fig_path = out_dir / out_name
    fig.savefig(fig_path, dpi=300)

    data = {
        "segment_npz": str(segment),
        "gt_files": [str(p) for p in gt_files],
        "slope_nm_per_ms": float(slope),
        "intercept_nm": float(intercept),
        "neg_scale": float(neg_scale),
        "metrics": metrics,
        "wl_gt": wl_gt.tolist(),
        "gt_norm": gt_norm.tolist(),
        "wl_recon": wl_recon.tolist(),
        "recon_norm": recon_norm.tolist(),
        "wl_bins": wl_bins.tolist(),
        "events_norm": events_norm.tolist(),
        "log_gt": log_gt.tolist(),
        "log_recon": log_recon.tolist(),
        "dlog_gt_norm": dlog_gt_norm.tolist(),
    }
    json_path = fig_path.with_suffix(".json")
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Saved figure: {fig_path}")
    print(f"Saved JSON: {json_path}")
    return fig_path, json_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Three-panel overlay with metrics + JSON export")
    parser.add_argument("--segment", type=Path, default=None, help="Segmented NPZ to analyse")
    parser.add_argument("--gt_files", type=Path, nargs="+", default=None, help="Spectrometer TXT files")
    parser.add_argument("--suffix", type=str, default="", help="Suffix for output filename")
    parser.add_argument("--preset", type=str, default="both", choices=["both", "lumileds", "2835"])
    parser.add_argument("--step_ms", type=float, default=2.0)
    parser.add_argument("--bin_ms", type=float, default=5.0)
    parser.add_argument("--sensor_width", type=int, default=1280)
    parser.add_argument("--sensor_height", type=int, default=720)
    parser.add_argument("--pos_scale", type=float, default=1.0)
    parser.add_argument("--auto_neg_min", type=float, default=0.1)
    parser.add_argument("--auto_neg_max", type=float, default=3.0)
    parser.add_argument("--plateau_frac", type=float, default=0.05)
    parser.add_argument("--xlim", type=float, nargs=2, default=(300.0, 900.0))
    parser.add_argument("--output_root", type=Path, default=REPO_ROOT / "align_background_vs_reference_code")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    publication_style()

    presets = {
        "lumileds": {
            "segment": REPO_ROOT / "scan_angle_20_lumileds/angle_20_blank_20250922_170433/angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz",
            "gt_files": [
                REPO_ROOT / "reference_spectrum_lumileds/USB2F042671_16-04-56-391.txt",
                REPO_ROOT / "reference_spectrum_lumileds/USB2F042671_16-04-36-993.txt",
            ],
            "suffix": "lumileds",
        },
        "2835": {
            "segment": REPO_ROOT / "scan_angle_20_led_2835b/angle_20_blank_2835_20250925_184747/angle_20_blank_2835_event_20250925_184747_segments/Scan_1_Forward_events.npz",
            "gt_files": [
                REPO_ROOT / "reference_spectrum_2835/USB2F042671_16-05-20-488.txt",
                REPO_ROOT / "reference_spectrum_2835/USB2F042671_16-05-22-288.txt",
            ],
            "suffix": "2835",
        },
    }

    if args.segment and args.gt_files:
        run_dataset(args.segment, args.gt_files, args.suffix, args)
        return

    if args.preset == "both":
        for key in ("2835", "lumileds"):
            cfg = presets[key]
            run_dataset(cfg["segment"], cfg["gt_files"], cfg["suffix"], args)
    else:
        cfg = presets[args.preset]
        run_dataset(cfg["segment"], cfg["gt_files"], cfg["suffix"], args)


if __name__ == "__main__":
    main()
