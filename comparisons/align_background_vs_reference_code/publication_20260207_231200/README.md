# Three‑Panel Metrics (Shift‑Invariant)

This folder contains the **three‑panel SPD vs. events** overlays plus quantitative metrics
for two illumination sources (Lumileds + 2835). In addition to standard metrics,
we also report **shift‑invariant metrics** based on max correlation over a
wavelength‑shift sweep.

## Script

- `align_background_vs_reference_code/compare_publication_three_panel_metrics.py`

## Command Used

```bash
/home/lachlan/miniconda3/envs/nhi/bin/python \
  align_background_vs_reference_code/compare_publication_three_panel_metrics.py \
  --preset both \
  --out_dir align_background_vs_reference_code/publication_20260207_231200
```

## Inputs

**Lumileds**
- Segment NPZ: `scan_angle_20_lumileds/angle_20_blank_20250922_170433/angle_20_blank_event_20250922_170433_segments/Scan_1_Forward_events.npz`
- GT SPD: `reference_spectrum_lumileds/USB2F042671_16-04-56-391.txt`
- GT SPD (secondary): `reference_spectrum_lumileds/USB2F042671_16-04-36-993.txt`

**2835**
- Segment NPZ: `scan_angle_20_led_2835b/angle_20_blank_2835_20250925_184747/angle_20_blank_2835_event_20250925_184747_segments/Scan_1_Forward_events.npz`
- GT SPD: `reference_spectrum_2835/USB2F042671_16-05-20-488.txt`
- GT SPD (secondary): `reference_spectrum_2835/USB2F042671_16-05-22-288.txt`

## Outputs

### Figures
- `three_panel_5ms_Scan_1_Forward_2835_metrics.png`
- `three_panel_5ms_Scan_1_Forward_lumileds_metrics.png`

### JSON
- `three_panel_5ms_Scan_1_Forward_2835_metrics.json`
- `three_panel_5ms_Scan_1_Forward_lumileds_metrics.json`
- `three_panel_metrics_combined.json` (full curves + metrics)
- `three_panel_metrics_summary.json` (metrics only, compact)

## Metrics Reported

### Standard metrics
- **Pearson r**
- **Spearman ρ**
- **RMSE**
- **nRMSE** (RMSE normalized by GT range)
- **MAE**
- **R²**

### Shift‑invariant metrics
For each panel, we also compute the **best wavelength shift** that maximizes
correlation between the curves and report the resulting metrics:
- **best_shift_nm** (nm)
- **max_corr**
- **rmse_after_shift**
- **nrmse_after_shift**

Panels evaluated:
1. **Cumulative**: SPD vs exp‑cumsum (events)
2. **Log**: log(SPD) vs log(reconstruction)
3. **Derivative vs Events**: d log(SPD)/dλ vs event rate

## Notes

- Shift‑invariant metrics are computed by sweeping shifts over ±120 nm
  with 1 nm steps and taking the max correlation.
- This helps evaluate similarity **even if curves are globally shifted**.
