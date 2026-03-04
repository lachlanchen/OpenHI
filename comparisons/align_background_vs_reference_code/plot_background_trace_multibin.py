#!/usr/bin/env python3
"""Plot non-overlapping window background traces for multiple bin sizes.

Example:
  python comparisons/align_background_vs_reference_code/plot_background_trace_multibin.py \
    --segment scan_angle_20_lumileds/angle_20_blank_20250922_170433/angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz \
    --window_ms 1 5 25 50 \
    --stride_ms 1 \
    --output_root comparisons/align_background_vs_reference_code
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import visualize_cumulative_weighted as vcw  # noqa: E402
from comparisons.align_background_vs_reference_code.compare_reconstruction_to_gt import moving_average  # noqa: E402


def sliding_window_sum(
    times: np.ndarray,
    weights: np.ndarray,
    window_us: float,
    stride_us: float,
    t_min: float,
    t_max: float,
) -> Tuple[np.ndarray, np.ndarray]:
    if times.size == 0:
        return np.array([], dtype=np.float64), np.array([], dtype=np.float64)

    order = np.argsort(times, kind="mergesort")
    times_sorted = times[order]
    weights_sorted = weights[order]

    if window_us <= 0 or stride_us <= 0:
        raise ValueError("window_us and stride_us must be positive")
    if t_max <= t_min:
        return np.array([], dtype=np.float64), np.array([], dtype=np.float64)

    total_span = t_max - t_min
    if total_span <= window_us:
        starts = np.array([t_min], dtype=np.float64)
    else:
        count = int(np.floor((total_span - window_us) / stride_us)) + 1
        starts = t_min + stride_us * np.arange(count, dtype=np.float64)
        last_start = t_max - window_us
        if starts.size == 0 or starts[-1] < last_start - 1e-6:
            starts = np.append(starts, last_start)

    ends = starts + window_us
    prefix = np.concatenate([[0.0], np.cumsum(weights_sorted, dtype=np.float64)])
    right = np.searchsorted(times_sorted, ends, side="right")
    left = np.searchsorted(times_sorted, starts, side="left")
    sums = prefix[right] - prefix[left]
    return starts, sums


def build_window_series(
    t_comp: np.ndarray,
    p: np.ndarray,
    window_ms: float,
    stride_ms: float,
    pos_scale: float,
    sensor_area: float,
) -> Tuple[np.ndarray, np.ndarray]:
    window_us = window_ms * 1000.0
    stride_us = stride_ms * 1000.0
    t_min = float(np.min(t_comp))
    t_max = float(np.max(t_comp))

    pos_mask = p >= 0
    neg_mask = ~pos_mask

    starts_pos, counts_pos = sliding_window_sum(
        t_comp[pos_mask],
        np.ones(np.count_nonzero(pos_mask), dtype=np.float64),
        window_us,
        stride_us,
        t_min,
        t_max,
    )
    starts_neg, counts_neg = sliding_window_sum(
        t_comp[neg_mask],
        np.ones(np.count_nonzero(neg_mask), dtype=np.float64),
        window_us,
        stride_us,
        t_min,
        t_max,
    )

    starts = starts_pos if starts_pos.size else starts_neg
    pos_vals = counts_pos if counts_pos.size else np.zeros_like(counts_neg)
    neg_vals = counts_neg if counts_neg.size else np.zeros_like(counts_pos)

    net = pos_scale * pos_vals - neg_vals
    per_pixel = net / sensor_area
    centers_ms = (starts + 0.5 * window_us - starts[0]) / 1000.0
    return centers_ms, per_pixel


def ensure_output_dir(root: Path) -> Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = root / f"publication_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def parse_args() -> argparse.Namespace:
    default_segment = (
        REPO_ROOT
        / "scan_angle_20_lumileds/angle_20_blank_20250922_170433/"
        "angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz"
    )
    ap = argparse.ArgumentParser(description="Plot non-overlapping background traces for multiple windows")
    ap.add_argument("--segment", type=Path, default=default_segment, help="Segment NPZ to analyse")
    ap.add_argument("--window_ms", type=float, nargs="+", default=[1, 2.5, 5, 25, 50], help="Window sizes in ms")
    ap.add_argument("--stride_ms", type=float, default=None, help="Stride in ms (default: equals window)")
    ap.add_argument("--sensor_width", type=int, default=1280)
    ap.add_argument("--sensor_height", type=int, default=720)
    ap.add_argument("--pos_scale", type=float, default=1.0)
    ap.add_argument("--smooth_div", type=float, default=200.0, help="Smoothing divisor (higher = less smoothing)")
    ap.add_argument("--output_root", type=Path, default=REPO_ROOT / "comparisons/align_background_vs_reference_code")
    ap.add_argument("--font-scale", type=float, default=1.2, help="Font scale for publication styling")
    ap.add_argument("--show", action="store_true", help="Show plot")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    segment = args.segment.resolve()
    if not segment.exists():
        raise FileNotFoundError(segment)

    x, y, t, p = vcw.load_npz_events(str(segment))
    param_file = vcw.find_param_file_for_segment(str(segment))
    if param_file is None:
        raise FileNotFoundError("No learned parameter NPZ found next to segment")
    params = vcw.load_parameters_from_npz(param_file)
    t_comp, *_ = vcw.compute_fast_compensated_times(x, y, t, params["a_params"], params["b_params"])

    sensor_area = float(args.sensor_width * args.sensor_height)

    out_dir = ensure_output_dir(args.output_root)
    if args.font_scale and not np.isclose(args.font_scale, 1.0):
        scale = float(args.font_scale)
        base = float(plt.rcParams["font.size"])
        scaled = base * scale
        plt.rcParams.update(
            {
                "font.size": scaled,
                "axes.titlesize": scaled,
                "axes.labelsize": scaled,
                "xtick.labelsize": scaled,
                "ytick.labelsize": scaled,
                "legend.fontsize": scaled * 0.9,
                "lines.linewidth": 2.5,
            }
        )

    fig, ax = plt.subplots(figsize=(12.0, 4.6))

    for window_ms in args.window_ms:
        stride_ms = float(args.stride_ms) if args.stride_ms is not None else float(window_ms)
        centers_ms, series = build_window_series(
            t_comp,
            p,
            window_ms=float(window_ms),
            stride_ms=stride_ms,
            pos_scale=float(args.pos_scale),
            sensor_area=sensor_area,
        )
        if series.size == 0:
            continue
        smooth_span = max(5, int(len(series) / float(args.smooth_div)))
        smooth = moving_average(series, smooth_span)
        if np.max(np.abs(smooth)) > 0:
            smooth = smooth / np.max(np.abs(smooth))
        ax.plot(centers_ms, smooth, label=f"{window_ms:g} ms")

    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Normalised net event rate")
    ax.set_title("Background trace (non-overlapping windows)")
    ax.grid(False)
    ax.legend(loc="upper right")

    out_name = f"background_trace_multibin_{segment.stem}.png"
    fig_path = out_dir / out_name
    fig.tight_layout()
    fig.savefig(fig_path, dpi=300)
    pdf_path = fig_path.with_suffix(".pdf")
    fig.savefig(pdf_path)

    if args.show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)

    print(f"Saved plot: {fig_path}")
    print(f"Saved PDF: {pdf_path}")


if __name__ == "__main__":
    main()
