# Background Trace: Multi‑Bin (Non‑Overlapping)

This note records the multi‑bin background trace figure that overlays
non‑overlapping sliding‑window traces for several bin sizes in a single plot.

## Script

- `align_background_vs_reference_code/plot_background_trace_multibin.py`

## Dataset

**Segment NPZ**
- `scan_angle_20_lumileds/angle_20_blank_20250922_170433/angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz`

## Command Used (current)

```bash
python align_background_vs_reference_code/plot_background_trace_multibin.py \
  --segment scan_angle_20_lumileds/angle_20_blank_20250922_170433/angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz \
  --window_ms 1 5 25 50 \
  --sensor_width 1280 --sensor_height 720 \
  --output_root align_background_vs_reference_code
```

Notes:
- The plot uses **non‑overlapping windows** by default (stride = window size).
- Lines are **normalised** for visual comparison.
- The figure uses **publication styling** (larger fonts, no grid).

## Output

- `align_background_vs_reference_code/publication_20260206_221154/background_trace_multibin_Scan_1_Forward_events.png`
