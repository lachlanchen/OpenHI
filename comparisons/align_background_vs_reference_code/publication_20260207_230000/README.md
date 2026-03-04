# Three‑Panel Metrics (Lumileds + 2835)

This folder contains the **three‑panel SPD vs. events** overlays plus quantitative metrics
for two illumination sources:

- **Lumileds LED**
- **SMD 2835 LED**

## Script

- `align_background_vs_reference_code/compare_publication_three_panel_metrics.py`

## Command Used

```bash
/home/lachlan/miniconda3/envs/nhi/bin/python \
  align_background_vs_reference_code/compare_publication_three_panel_metrics.py \
  --preset both \
  --out_dir align_background_vs_reference_code/publication_20260207_230000
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

For each panel, we report:
- **Pearson r**
- **Spearman ρ**
- **RMSE**
- **nRMSE** (RMSE normalized by GT range)
- **MAE**
- **R²**

Panels evaluated:
1. **Cumulative**: SPD vs exp‑cumsum (events)
2. **Log**: log(SPD) vs log(reconstruction)
3. **Derivative vs Events**: d log(SPD)/dλ vs event rate

## Notes

- The metrics are computed after mapping the event timeline to wavelength with the
  same λ(t) fit used in the original three‑panel plots.
- The full curves are stored in the per‑LED JSONs and combined JSON for reproducibility.
