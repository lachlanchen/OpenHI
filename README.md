# Self-Calibrated Neuromorphic Hyperspectral Imaging

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#prerequisites)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#overview)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#repository-map)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#additional-tools)

A comprehensive pipeline for reconstructing spectra from event cameras with dispersed light illumination (e.g., diffraction grating). The system records intensity change events $e = (x, y, t, p)$ where $p \in \{-1, +1\}$ indicates polarity of log-intensity change, and automatically infers scan timing and calibration metadata ("auto info") directly from the event stream.

<p align="center">
  <img src="images/device_setup.png" alt="Device setup" width="24%">
  <img src="images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*Left: modular transmission microscope with a motorised grating illumination arm and vertical detection stack. Right: data-acquisition GUI used to monitor segmentation, compensation, and reconstructions in real time.*

Purchase the core development kit (excluding camera, tube lens, and optical table) for the paper [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151) preprinted on Optica Open:
- https://lazying.art/openhi-kit.html
- Promotion code for 30% off: `OPTICA`

## Contents

- [Overview](#overview)
- [Features](#features)
- [Repository Map](#repository-map)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Bill of Materials (Core Module)](#bill-of-materials-core-module)
- [Core Scripts](#core-scripts)
- [Additional Tools](#additional-tools)
- [Turbo Multi-Scan Compensation](#turbo-multi-scan-compensation)
- [Parameter Management](#parameter-management)
- [Memory Optimization](#memory-optimization)
- [Output Structure](#output-structure)
- [Configuration Examples](#configuration-examples)
- [Wavelength Mapping](#wavelength-mapping)
- [Tips and Best Practices](#tips-and-best-practices)
- [Development Notes](#development-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Citation](#citation)
- [License](#license)
- [Contributing](#contributing)
- [Support / Sponsor](#support--sponsor)

## Overview

When illumination sweeps across wavelengths over time, the event stream encodes a temporal derivative of the underlying spectrum along the dispersion axis.

This pipeline provides three main stages:

| Stage | Purpose | Primary script(s) |
|---|---|---|
| 1. Segment | Find scan timing and split recordings into forward/backward passes | `segment_robust_fixed.py` |
| 2. Compensate | Estimate piecewise-linear time-warp to remove scan-induced temporal tilt | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualize | Overlay learned boundaries and compare original vs. compensated time-binned frames | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

The repository also includes hardware assets, acquisition GUI code, and archival experiment branches under `versions/`.

## Features

- End-to-end RAW-to-spectrum event processing workflow.
- Auto/manual scan period detection and forward/backward segmentation.
- Multi-window compensation with trainable/fixed parameter modes.
- Parameter save/load in `NPZ`, `JSON`, and `CSV`.
- Multi-scan merge workflow for faster training iterations (`compensate_multiwindow_turbo.py`).
- Visualization suite for boundaries, binned frames, cumulative curves, and weighted diagnostics.
- Hardware documentation: BOM, PCB, 3D parts, firmware notes.
- Acquisition utilities for synchronized event/frame camera setups.

## Repository Map

Key hardware assets are kept alongside the code for quick access:

| Area | Path |
|---|---|
| 3D-printed parts | [`3D/`](3D/) |
| PCB layouts | [`PCB/`](PCB/) |
| Microcontroller firmware | [`firmware/`](firmware/) |
| Acquisition UI (desktop) | [`ImagingGUI/`](ImagingGUI/) |

## Project Structure

```text
OpenHI/
├── README.md
├── QUICKSTART.md
├── LICENSE
├── versions.md
├── 3D/
├── BOM/
├── PCB/
├── firmware/
├── ImagingGUI/
├── scripts/
├── segment_robust_fixed.py
├── compensate_multiwindow_train_saved_params.py
├── compensate_multiwindow_turbo.py
├── compensate_multiwindow*.py
├── visualize_boundaries_and_frames.py
├── visualize_cumulative_compare.py
├── visualize_cumulative_weighted.py
├── scan_compensation_gui_cloud.py
├── show_envi_spectrum_gui.py
├── simple_raw_reader.py
├── align_background_vs_reference_code/
├── align_data_vs_filter_code/
├── alignment_configs/
├── archive_code_variants/
├── outputs_root/
├── reference_filters/
├── reference_spectrum_2835/
├── reference_spectrum_lumileds/
├── references/
└── versions/
```

## Prerequisites

- Python 3.9+ (Python 3.10+ for some GUI tooling).
- Core Python packages: `numpy`, `torch`, `matplotlib`.
- Optional but common: `opencv-python`, `pillow`, `cellpose`.
- Metavision SDK / Python bindings for RAW event reading workflows (`simple_raw_reader.py`, segmentation from RAW).
- CUDA-enabled PyTorch is recommended for faster optimization.
- RAW recordings and/or segmented NPZ files available locally.

## Installation

No locked environment file is currently provided at repository root. Suggested setup:

```bash
# create and activate a virtual environment or conda env
python -m venv .venv
source .venv/bin/activate

# install core dependencies
pip install numpy matplotlib torch

# optional tools often used in this repository
pip install opencv-python pillow
# pip install cellpose
```

If using Git hooks for large-file hygiene:

```bash
bash scripts/setup_hooks.sh
```

## Usage

### Basic Workflow (current root scripts)

```bash
# 1. Segment RAW into 6 scans (Forward/Backward)
python segment_robust_fixed.py \
  data/recording.raw \
  --segment_events \
  --output_dir data/segments/

# 2. Train multi-window compensation
python compensate_multiwindow_train_saved_params.py \
  data/segments/Scan_1_Forward_events.npz \
  --bin_width 50000 \
  --visualize --plot_params --a_trainable \
  --iterations 1000

# 3. Visualize results with boundaries
python visualize_boundaries_and_frames.py \
  data/segments/Scan_1_Forward_events.npz

# 4. Compare cumulative vs multi-bin means
python visualize_cumulative_compare.py \
  data/segments/Scan_1_Forward_events.npz \
  --sensor_width 1280 --sensor_height 720
```

### One-command convenience wrapper

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

Environment knobs supported by `scripts/run_scan_pipeline.sh`:

| Variable | Default | Purpose |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Active event window fraction |
| `PIPELINE_BIN_WIDTH` | `50000` | Training bin width in microseconds |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Sensor width for visualization |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Sensor height for visualization |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Event sampling fraction for plotting |
| `PIPELINE_TIME_BIN_US` | `1000` | Segmentation activity-bin size |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Segment file pattern for downstream scripts |

## Configuration

Important CLI controls used across scripts:

### Segmentation (`segment_robust_fixed.py`)

- `--time_bin_us`: activity bin size in microseconds.
- `--round_trip_period`: manual period (default `1688` bins).
- `--auto_calculate_period`: period via autocorrelation.
- `--activity_fraction`: active event window fraction.
- `--manual_start_shift_ms`: manual scan start offset.

### Compensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (default `13`), `--temperature` (default `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` for memory control.
- `--load_params` to reuse learned parameters.

### Visualization

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, sensor size args.
- `visualize_cumulative_compare.py`: sensor size, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: polarity scales, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

## Examples

### Quick start dataset-style commands (from `QUICKSTART.md`)

```bash
python segment_robust_fixed.py \
  led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556.raw \
  --segment_events \
  --output_dir led_12v_no_acc_glass/glass/

python compensate_multiwindow_train_saved_params.py \
  led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556_segments/Scan_1_Forward_events.npz \
  --bin_width 50000 \
  --visualize --plot_params --a_trainable \
  --iterations 1000 \
  --b_default 0 \
  --smoothness_weight 0.001

python visualize_boundaries_and_frames.py \
  led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556_segments/Scan_1_Forward_events.npz
```

### Turbo multi-scan training

```bash
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/your_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params
```

### Reuse learned parameters (skip retraining)

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

## Bill of Materials (Core Module)

See [`BOM/core_module.md`](BOM/core_module.md) for the full table with links and notes.

### Table S2. Acquisition Time and Cost Comparison Between the Proposed Event-Driven System and a Reference Hyperspectral Camera

| Parameter | Ours | Reference camera |
|---|---|---|
| Acquisition time | ∼585 ms per scan | 300 s per scan |
| Data volume | 18.5 MB | 138 MB |
| Approx. price | ∼3000 USD | 14 000 USD |

### Table S3. Bill of Materials for the Core Scanning Illumination Module
(Excluding event camera and optional 4f validation optics)

| Component | Notes | Cost (USD) | Taobao Link |
|---|---|---:|---|
| Motion control | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| Optics (grating) | Diffraction grating (education grade) | 3.47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPRouNw |
| Illumination | 2835 LED (6 CNY / 10 pcs; 0.6 CNY used) | 0.08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| Reflector | Folding mirror | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| Electronics | LED PCB (CNY/board; min order 5 pcs) | 1.67 |  |
| Limit switches | Optional, 2 × 8.07 CNY | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| 3D printing | One-third PLA filament spool (covers all printed parts) | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| Lens | Plano-convex lens (25.4 mm, 350–700 nm AR) |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| Total | core module | **33.99** |  |

## Core Scripts

### 1. Segmentation: `segment_robust_fixed.py`

**Goal**: Extract scan timing from raw events and slice into 6 one-way scans (F, B, F, B, F, B).

**Mathematical Description**:

- **Activity signal** (events binned with $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Active window detection**: find the smallest contiguous window containing $80\%$ of events.

- **Period estimation**: autocorrelation or manual period (default: $1688$ bins).

- **Reverse-correlation** (timing structure):
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  with
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**Usage**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Arguments**:

- `--segment_events`: Save individual scan segments as NPZ files.
- `--round_trip_period 1688`: Use manual period (default).
- `--auto_calculate_period`: Override manual period with autocorrelation.
- `--activity_fraction 0.80`: Fraction of events for active region.
- `--max_iterations 2`: Refinement iterations.

### 2. Compensation: `compensate_multiwindow_train_saved_params.py`

**Goal**: Learn time-warp parameters to remove scan-induced temporal shear using multi-window piecewise-linear compensation.

**Mathematical Description**:

- **Boundary surfaces**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Soft window memberships**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Interpolated slopes (optional)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Time warp**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Loss**: variance minimization of time-binned frames with smoothness regularization on parameters.

**Usage**:

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**Key Arguments**:

- `--a_trainable` / `--a_fixed`: Control a-parameter training (default: fixed).
- `--b_trainable` / `--b_fixed`: Control b-parameter training (default: trainable).
- `--num_params 13`: Number of boundary parameters.
- `--temperature 5000`: Sigmoid temperature for soft windows.
- `--smoothness_weight 0.001`: Regularization weight.
- `--load_params file.npz`: Load saved parameters.
- `--chunk_size 250000`: Memory-efficient processing chunk size.

### 3. Visualization: `visualize_boundaries_and_frames.py`

**Goal**: Display learned parameters and show qualitative improvements.

**Features**:

- Parameter overlays on $x\text{–}t$ and $y\text{–}t$ projections.
- Time-binned frame comparisons (original vs. compensated).
- Sliding window analysis (50 ms and 2 ms bins).
- Wavelength mapping for spectral visualization.

**Usage**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Cumulative Comparison: `visualize_cumulative_compare.py`

**Goal**: Compare cumulative 2 ms-step means with sliding bin means.

**Mathematical Description**:

- **Cumulative means**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Sliding means**: event counts in $[T-\Delta,\,T)$ divided by $H \times W$.

- **Relationship** (finite-difference derivative):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Usage**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Additional Tools

### GUI Application: `scan_compensation_gui_cloud.py`

Complete GUI for scan compensation with 3D spectral visualization.

**Features**:

- Interactive parameter tuning.
- Real-time optimization progress.
- 3D wavelength-mapped visualization.
- Export results and parameters.

**Usage**:

```bash
python scan_compensation_gui_cloud.py
```

### Dual Camera System (current path)

Synchronized recording system for event and frame cameras:

- `ImagingGUI/DualCamera_separate_transform.py`

**Features**:

- Simultaneous event and frame recording.
- Real-time preview with transformations.
- Always-on-top window controls.
- Parameter adjustment during recording.

### Arduino Motor Control (legacy path reference retained)

The original README referenced this firmware sketch path:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

Current repository layout includes firmware notes at:

- `firmware/README.md`

This path mismatch is preserved here intentionally; if you have the rotor sketch folders in another branch/local checkout, keep using those paths.

Legacy documented capabilities of this sketch include:

- Precise angle control with microstepping.
- Acceleration/deceleration profiles.
- Limit switch integration.
- Auto-centering functionality.

## Turbo Multi-Scan Compensation

When you have multiple one-way scans (Forward/Backward) of the same sweep, you can merge them and run the proven trainer on a single combined event stream using `compensate_multiwindow_turbo.py`.

### What it does

- Accepts one segment, an explicit list, or a whole segments directory.
- For Backward scans, flips polarity and reverses time before merging:
- If polarity `p ∈ {0,1}`: `p := 1 − p`; then reverse time within the scan.
- If polarity `p ∈ {−1,1}`: `p := −p`; then reverse time within the scan.
- Concatenates scans on a continuous timeline (with a `1 μs` gap between scans) and calls `compensate_multiwindow_train_saved_params.py` under the hood.

### Usage

```bash
# Merge all scans (Forward+Backward) from a segments folder and train at 5 ms
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/.../_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params

# Reuse learned params and just render at 10 ms (fast, no training)
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/.../_segments \
  --include all --sort time \
  --bin-width 10000 \
  --load-params path/to/learned_params.npz \
  -- --visualize --plot_params

# Only Forward scans
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/.../_segments \
  --include forward --sort time \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000
```

### Options

- `--segment`, `--segments`, `--segments-dir`: choose your input set.
- `--include {all|forward|backward}`: filter by scan direction.
- `--sort {name|time}`: natural filename order or NPZ `start_time` order.
- `--bin-width <μs>`: forwarded to the base trainer.
- `--load-params`: reuse saved parameters (skip training and regenerate outputs quickly at new bin widths).
- `--extra ...` after `--`: any additional flags are forwarded to the base trainer.

### Speed scaling tip

If your scan is `N×` faster than baseline, reduce `--bin-width` by the same factor (e.g., baseline `50 ms` -> `10×` faster -> `5 ms`: `--bin-width 5000`). You can train once (e.g., `5 ms`), then use `--load-params` to quickly regenerate results at `10 ms` without retraining.

## Parameter Management

The system supports comprehensive parameter save/load functionality.

### Save Formats

- **NPZ**: Binary format for fast loading.
- **JSON**: Human-readable with metadata.
- **CSV**: Excel-compatible for manual inspection.

### Parameter Loading

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Parameter Files

Files are automatically named with parameter count, such as: `*_learned_params_n13.*`.

## Memory Optimization

The system uses chunked processing throughout:

| Item | Detail |
|---|---|
| Chunk Size | Default `250000` events (configurable) |
| Memory Efficient | Processes large datasets without GPU overflow |
| Unified Variance | Maintains proper gradient flow for learning |
| Progress Tracking | Real-time processing updates |

## Output Structure

```text
project/
├── data/
│   ├── recording.raw                    # Original RAW file
│   ├── recording_segments/              # Segmented scans
│   │   ├── Scan_1_Forward_events.npz
│   │   ├── Scan_2_Backward_events.npz
│   │   └── ...
│   ├── learned_params_n13.npz          # Trained parameters
│   ├── learned_params_n13.json
│   ├── learned_params_n13.csv
│   └── visualization_20240115_143022/  # Results
│       ├── events_with_params.png
│       ├── sliding_frames_*.npz
│       ├── frame_means_wavelength.png
│       └── time_binned_frames/         # Individual frames
```

## Configuration Examples

### High-Precision Compensation

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### Fast Processing

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### Memory Constrained

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## Wavelength Mapping

The system supports spectral visualization by mapping temporal evolution to wavelength:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Default Range**: $380\text{–}680~\text{nm}$ (configurable).

## Tips and Best Practices

### Parameter Selection

- **Microstepping**: Use `32×` for smooth motion (Arduino).
- **Bin Width**: Start with `50 ms` for optimization, `2 ms` for analysis.
- **Temperature**: Higher values (around `5000`) for smoother boundaries.
- **Smoothness**: `0.001` provides good regularization.

### Memory Management

- **GPU Memory**: Use chunked processing with appropriate chunk size.
- **Event Count**: `> 10^6` events recommended for stable learning.
- **Iterations**: `1000` iterations usually sufficient.

### File Organization

- Keep RAW files and segments in the same directory.
- Parameter files are auto-detected by naming convention.
- Use descriptive filename prefixes for organized output.

## Development Notes

- `versions.md` describes historical project eras and migration rationale.
- `.githooks/pre-commit` blocks oversized/binary commits and non-code/doc file types.
- `scripts/setup_hooks.sh` sets `core.hooksPath` to `.githooks`.
- `archive_code_variants/` stores older script variants to keep root-level tooling focused.

Known documentation drift (preserved intentionally for backward compatibility context):

- Some older docs mention `sync_image_system/` or `dual_camera_gui.py`; current checkout contains `ImagingGUI/DualCamera_separate_transform.py` and SDK directories.
- `firmware/README.md` references several Arduino sketch subfolders that are not present in this checkout.
- `versions.md` mentions dataset symlinks and some legacy script names that are not present in current root.

## Troubleshooting

- **Parameter loading errors**: Ensure `--num_params` is compatible with the loaded parameter file.
- **OOM / memory pressure**: Reduce `--chunk_size` and/or increase `--bin_width`.
- **Weak compensation quality**: Increase `--iterations`, enable trainable parameters (`--a_trainable`, `--b_trainable`, optionally `--boundary_trainable`), and verify segmentation quality.
- **No segment files produced**: Confirm RAW path, Metavision reader availability, and that `--segment_events` was passed.
- **Turbo wrapper argument passing**: Put trainer args after `--` (or use `--extra`).
- **GUI issues**: Verify Tkinter backend support and camera SDK availability on your platform.

## Roadmap

- Improve dependency/bootstrap reproducibility (`requirements.txt` or environment lockfile).
- Consolidate legacy script names and path references across docs.
- Expand documented dataset schemas and expected NPZ field conventions.
- Add regression-style tests for segmentation/compensation on small fixture data.
- Continue integrating publication-quality analysis outputs from `align_*` pipelines.

## Citation

If this repository is useful in your research, please cite the Optica Open preprint:

```bibtex
@article{chen2025selfcalibrated,
  title   = {Self-calibrated neuromorphic hyperspectral derivative imaging},
  author  = {Chen, Rongzhou and Wang, Chutian and Li, Yuxing and Cao, Yuqing and Zhu, Shuo and Lam, Edmund},
  year    = {2025},
  journal = {Optica Open},
  note    = {Preprint},
  doi     = {10.1364/opticaopen.30739151}
}
```

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE) for details.

## Contributing

Contributions are welcome.

- Start with existing scripts and documentation style.
- Keep command-line examples reproducible with repository paths where possible.
- If you add large datasets/outputs, ensure `.githooks/pre-commit` policies are respected.

Note: a dedicated `CONTRIBUTING.md` is not present in this checkout. If needed, open an issue or submit a PR with the contribution workflow you propose.

## Support / Sponsor

| Channel | Link |
|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen |
| Project site | https://lazying.art |
| Community chat | https://chat.lazying.art |
| Additional creator page | https://onlyideas.art |
| Core kit purchase page | https://lazying.art/openhi-kit.html |
| Promotion code | `OPTICA` |

---

### Notes

- 📌 This README keeps legacy-path notes where repository evolution introduced naming/layout drift.
- 🔒 If uncertain about older references, the text is preserved intentionally rather than removed.
