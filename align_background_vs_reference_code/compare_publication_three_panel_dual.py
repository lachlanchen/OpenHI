#!/usr/bin/env python3
"""Three-panel overlay with two reconstructions (blank + sample) vs GT.

Panels (left → right):
1) Cumulative exp-intensity (GT vs blank vs sample)
2) Log-intensity (GT vs blank vs sample)
3) Spectral derivative vs events (GT vs blank vs sample)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Tuple

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
from compare_publication_three_panel import build_cumulative_and_bins  # noqa: E402


def build_cumulative_and_bins_with_params(
    segment_npz: Path,
    step_ms: float,
    bin_ms: float,
    pos_scale: float,
    auto_bounds: Tuple[float, float],
    plateau_frac: float,
    sensor_width: int,
    sensor_height: int,
    param_file: Path,
) -> Tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray]:
    x, y, t, p = vcw.load_npz_events(str(segment_npz))
    t_min, t_max = float(np.min(t)), float(np.max(t))
    params = vcw.load_parameters_from_npz(param_file)
    t_comp, *_ = vcw.compute_fast_compensated_times(x, y, t, params["a_params"], params["b_params"])

    pos_mask = p >= 0
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


def parse_args() -> argparse.Namespace:
    default_blank = (
        REPO_ROOT
        / "scan_angle_20_lumileds/angle_20_blank_20250922_170433/"
        "angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz"
    )
    default_sample = (
        REPO_ROOT
        / "scan_angle_20_lumileds/angle_20_sanqin_20250922_170630/"
        "angle_20_sanqin_event_20250922_170630_segments/Scan_1_Forward_events.npz"
    )
    parser = argparse.ArgumentParser(description="Dual three-panel overlay (blank + sample + GT)")
    parser.add_argument("--segment-blank", type=Path, default=default_blank, help="Blank segment NPZ")
    parser.add_argument("--segment-sample", type=Path, default=default_sample, help="Sample segment NPZ")
    parser.add_argument("--label-blank", type=str, default="Blank", help="Legend label for blank")
    parser.add_argument("--label-sample", type=str, default="Sample", help="Legend label for sample")
    parser.add_argument(
        "--gt_files",
        type=Path,
        nargs="+",
        required=True,
        help="One or more spectrometer TXT files (first is used for shape/derivative)",
    )
    parser.add_argument("--step_ms", type=float, default=2.0, help="Cumulative step size in milliseconds")
    parser.add_argument("--bin_ms", type=float, default=5.0, help="Event bin width for derivative panel (ms)")
    parser.add_argument("--sensor_width", type=int, default=1280)
    parser.add_argument("--sensor_height", type=int, default=720)
    parser.add_argument("--pos_scale", type=float, default=1.0)
    parser.add_argument("--auto_neg_min", type=float, default=0.1)
    parser.add_argument("--auto_neg_max", type=float, default=3.0)
    parser.add_argument("--plateau_frac", type=float, default=0.05)
    parser.add_argument("--sample-shift-nm", type=float, default=0.0, help="Manual shift for sample curve (nm)")
    parser.add_argument("--auto-shift-sample-left-edge", action="store_true",
                        help="Shift sample so its left edge matches GT left edge")
    parser.add_argument("--auto-shift-sample-corr", action="store_true",
                        help="Shift sample to maximise correlation with GT derivative")
    parser.add_argument("--shift-range", type=float, default=120.0, help="Search range (+/- nm) for auto shift")
    parser.add_argument("--shift-step", type=float, default=1.0, help="Search step (nm) for auto shift")
    parser.add_argument("--params-npz", type=Path, default=None, help="Optional parameter NPZ for compensation")
    parser.add_argument("--xlim", type=float, nargs=2, default=(300.0, 900.0))
    parser.add_argument("--suffix", type=str, default="", help="Suffix appended to output filename")
    parser.add_argument("--output_root", type=Path, default=REPO_ROOT / "align_bg_vs_gt_code")
    parser.add_argument("--show", action="store_true", help="Display figure interactively")
    return parser.parse_args()


def normalise_series(series: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
    smooth = moving_average(series, max(21, int(len(series) // 200) | 1))
    region = detect_active_region(smooth)
    norm = normalise_curve(series, region)
    return norm, (region.start_idx, region.end_idx)


def normalise_events(net_bin: np.ndarray) -> np.ndarray:
    if net_bin.size:
        smooth_events = moving_average(net_bin, max(5, len(net_bin) // 200 | 1))
        smooth_events = smooth_events - float(np.mean(smooth_events))
    else:
        smooth_events = net_bin
    if np.max(np.abs(smooth_events)) > 0:
        return smooth_events / np.max(np.abs(smooth_events))
    return smooth_events


def load_gt(gt_files):
    curves = []
    for txt in gt_files:
        wl, val = load_ground_truth(txt)
        curves.append((txt.stem, wl, val))
    if not curves:
        raise FileNotFoundError("No ground-truth files supplied")
    return curves


def compute_left_edge_idx(series: np.ndarray) -> int:
    smooth = moving_average(series, max(21, int(len(series) // 200) | 1))
    region = detect_active_region(smooth)
    return int(region.start_idx)


def auto_shift_by_correlation(
    wl_gt: np.ndarray,
    dlog_gt: np.ndarray,
    wl_sample: np.ndarray,
    dlog_sample: np.ndarray,
    shift_range: float,
    shift_step: float,
) -> Tuple[float, float]:
    wl_min = max(float(np.min(wl_gt)), float(np.min(wl_sample)))
    wl_max = min(float(np.max(wl_gt)), float(np.max(wl_sample)))
    if wl_max <= wl_min:
        return 0.0, 0.0

    grid = np.arange(wl_min, wl_max + shift_step, shift_step)
    gt = np.interp(grid, wl_gt, dlog_gt)

    gt = gt - float(np.mean(gt))
    gt_norm = np.linalg.norm(gt)
    if gt_norm <= 0:
        return 0.0, 0.0

    shifts = np.arange(-shift_range, shift_range + shift_step, shift_step)
    best_shift = 0.0
    best_corr = -np.inf
    for s in shifts:
        samp = np.interp(grid, wl_sample + s, dlog_sample)
        samp = samp - float(np.mean(samp))
        denom = np.linalg.norm(samp) * gt_norm
        if denom <= 0:
            continue
        corr = float(np.dot(gt, samp) / denom)
        if corr > best_corr:
            best_corr = corr
            best_shift = float(s)
    return best_shift, best_corr


def main() -> None:
    args = parse_args()
    publication_style()

    gt_curves = load_gt(args.gt_files)
    gt_start_nm, gt_end_nm = detect_visible_edges(gt_curves)
    wl_gt_raw, val_gt_raw = gt_curves[0][1], gt_curves[0][2]
    mask0 = (wl_gt_raw >= 300.0) & (wl_gt_raw <= 900.0)
    wl_gt = wl_gt_raw[mask0]
    val_gt = val_gt_raw[mask0]
    smooth_gt = moving_average(val_gt, max(21, len(val_gt) // 300))
    region_gt = detect_active_region(smooth_gt)
    gt_norm = normalise_curve(smooth_gt, region_gt)

    blank_param = vcw.find_param_file_for_segment(str(args.segment_blank))
    if blank_param is None:
        raise FileNotFoundError("No learned parameter NPZ found next to blank segment")
    param_file = args.params_npz if args.params_npz else blank_param
    if param_file is None or not Path(param_file).exists():
        raise FileNotFoundError(f"Parameter NPZ not found: {param_file}")

    blank = build_cumulative_and_bins_with_params(
        args.segment_blank,
        step_ms=args.step_ms,
        bin_ms=args.bin_ms,
        pos_scale=args.pos_scale,
        auto_bounds=(args.auto_neg_min, args.auto_neg_max),
        plateau_frac=args.plateau_frac,
        sensor_width=args.sensor_width,
        sensor_height=args.sensor_height,
        param_file=Path(param_file),
    )
    sample = build_cumulative_and_bins_with_params(
        args.segment_sample,
        step_ms=args.step_ms,
        bin_ms=args.bin_ms,
        pos_scale=args.pos_scale,
        auto_bounds=(args.auto_neg_min, args.auto_neg_max),
        plateau_frac=args.plateau_frac,
        sensor_width=args.sensor_width,
        sensor_height=args.sensor_height,
        param_file=Path(param_file),
    )

    time_ms_blank, cum_blank, neg_blank, time_ms_bin_blank, net_bin_blank = blank
    time_ms_sample, cum_sample, neg_sample, time_ms_bin_sample, net_bin_sample = sample

    # Use blank to define wavelength mapping
    smooth_blank = moving_average(cum_blank, max(21, int(len(cum_blank) // 200) | 1))
    region_blank = detect_active_region(smooth_blank)
    t0 = float(time_ms_blank[region_blank.start_idx])
    t1 = float(time_ms_blank[region_blank.end_idx])
    if t1 <= t0:
        raise ValueError("Detected non-increasing active region in blank reconstruction")
    slope = (gt_end_nm - gt_start_nm) / (t1 - t0)
    intercept = gt_start_nm - slope * t0

    wl_blank = slope * time_ms_blank + intercept
    wl_sample = slope * time_ms_sample + intercept
    wl_bins_blank = slope * time_ms_bin_blank + intercept
    wl_bins_sample = slope * time_ms_bin_sample + intercept

    blank_norm, blank_region = normalise_series(cum_blank)
    sample_norm, sample_region = normalise_series(cum_sample)

    eps = 1e-3
    log_gt = np.log(np.clip(gt_norm, eps, None))
    dlog_gt = np.gradient(log_gt, wl_gt)
    dlog_gt_norm = dlog_gt / np.max(np.abs(dlog_gt)) if np.max(np.abs(dlog_gt)) > 0 else dlog_gt
    log_blank = np.log(np.clip(blank_norm, eps, None))
    log_sample = np.log(np.clip(sample_norm, eps, None))

    dlog_sample = np.gradient(log_sample, wl_sample)
    if np.max(np.abs(dlog_sample)) > 0:
        dlog_sample = dlog_sample / np.max(np.abs(dlog_sample))

    sample_shift_nm = float(args.sample_shift_nm)
    corr_shift = 0.0
    corr_val = 0.0
    if args.auto_shift_sample_left_edge:
        idx = compute_left_edge_idx(cum_sample)
        sample_left_nm = float(wl_sample[idx])
        sample_shift_nm += float(gt_start_nm - sample_left_nm)
    if args.auto_shift_sample_corr:
        corr_shift, corr_val = auto_shift_by_correlation(
            wl_gt, dlog_gt_norm, wl_sample, dlog_sample, args.shift_range, args.shift_step
        )
        sample_shift_nm += corr_shift

    if not np.isclose(sample_shift_nm, 0.0):
        wl_sample = wl_sample + sample_shift_nm
        wl_bins_sample = wl_bins_sample + sample_shift_nm

    events_blank = normalise_events(net_bin_blank)
    events_sample = normalise_events(net_bin_sample)

    out_dir = ensure_output_dir(args.output_root)
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.6), sharex=True)
    ax1, ax2, ax3 = axes
    for ax in axes:
        ax.xaxis.labelpad = 2

    visible_min, visible_max = 380.0, 780.0
    xmin = max(args.xlim[0], visible_min)
    xmax = min(args.xlim[1], visible_max)

    ax1.axvspan(380, 780, color="0.92", zorder=0)
    ax1.plot(wl_gt, gt_norm, color="#1f77b4", label="SPD")
    ax1.plot(wl_blank, blank_norm, color="#2ca02c", label=args.label_blank)
    ax1.plot(wl_sample, sample_norm, color="#ff7f0e", label=args.label_sample)
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("Normalised intensity")
    ax1.grid(alpha=0.3)

    ax2.axvspan(380, 780, color="0.92", zorder=0)
    ax2.plot(wl_gt, log_gt, color="#1f77b4", label="GT")
    ax2.plot(wl_blank, log_blank, color="#2ca02c", label=args.label_blank)
    ax2.plot(wl_sample, log_sample, color="#ff7f0e", label=args.label_sample)
    ax2.set_xlim(xmin, xmax)
    ax2.set_xlabel("Wavelength (nm)")
    ax2.set_ylabel("log intensity")
    ax2.grid(alpha=0.3)

    ax3.axvspan(380, 780, color="0.92", zorder=0)
    ax3.plot(wl_gt, dlog_gt_norm, color="#1f77b4")
    ax3.plot(wl_bins_blank, events_blank, color="#2ca02c")
    ax3.plot(wl_bins_sample, events_sample, color="#ff7f0e")
    ax3.set_xlim(xmin, xmax)
    ax3.set_xlabel("Wavelength (nm)")
    ax3.set_ylabel("d log(SPD)/dλ, Event Density")
    ax3.grid(alpha=0.3)
    handles, labels = ax1.get_legend_handles_labels()
    ax3.legend(handles, labels, loc="upper right", bbox_to_anchor=(1.0, 1.0))

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))

    blank_name = args.segment_blank.stem.replace("_events", "")
    sample_name = args.segment_sample.stem.replace("_events", "")
    suffix = f"_{args.suffix}" if args.suffix else ""
    out_name = f"three_panel_dual_{args.bin_ms:.0f}ms_{blank_name}_{sample_name}{suffix}.png"
    fig_path = out_dir / out_name
    fig.savefig(fig_path, dpi=300)
    pdf_path = fig_path.with_suffix(".pdf")
    fig.savefig(pdf_path)

    mapping = {
        "segment_blank": str(args.segment_blank),
        "segment_sample": str(args.segment_sample),
        "gt_files": [str(p) for p in args.gt_files],
        "slope_nm_per_ms": float(slope),
        "intercept_nm": float(intercept),
        "blank_neg_scale": float(neg_blank),
        "sample_neg_scale": float(neg_sample),
        "sample_shift_nm": float(sample_shift_nm),
        "sample_shift_corr": {"shift_nm": float(corr_shift), "corr": float(corr_val)},
        "blank_active_window_ms": [float(time_ms_blank[region_blank.start_idx]), float(time_ms_blank[region_blank.end_idx])],
        "sample_active_window_ms": [float(time_ms_sample[sample_region[0]]), float(time_ms_sample[sample_region[1]])],
    }
    mapping_path = fig_path.with_name(f"{fig_path.stem}_mapping.json")
    mapping_path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    if args.show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)

    print(f"Saved dual three-panel overlay to: {fig_path}")
    print(f"Saved dual three-panel PDF to: {pdf_path}")
    print(f"Saved mapping JSON to: {mapping_path}")


if __name__ == "__main__":
    main()
