[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# Tạo ảnh siêu phổ neuromorphic tự hiệu chuẩn (OpenHI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#prerequisites)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#overview)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#repository-map)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#additional-tools)
[![Paper](https://img.shields.io/badge/Preprint-Optica%20Open-ff6b6b.svg)](https://doi.org/10.1364/opticaopen.30739151)
[![i18n](https://img.shields.io/badge/i18n-6%20ready%20%7C%205%20planned-22c55e.svg)](#internationalization)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#overview)

> [!NOTE]
> Trạng thái i18n trong bản checkout này: `ar`, `es`, `fr`, `ja`, `ko`, `vi` hiện có trong `i18n/`. Các liên kết ngôn ngữ bổ sung vẫn được giữ để tương thích với kế hoạch mở rộng bản dịch.

Pipeline toàn diện để tái dựng phổ từ camera sự kiện với chiếu sáng tán sắc (ví dụ: lưới nhiễu xạ). Hệ thống ghi lại các sự kiện thay đổi cường độ $e = (x, y, t, p)$, trong đó $p \in \{-1, +1\}$ biểu thị cực tính của biến thiên log-cường độ, đồng thời tự suy luận thời điểm quét và metadata hiệu chuẩn ("auto info") trực tiếp từ luồng sự kiện.

## At a Glance

| Mục | Chi tiết |
|---|---|
| Ý tưởng cốt lõi | Ảnh đạo hàm siêu phổ tự hiệu chuẩn từ luồng sự kiện |
| Các giai đoạn chính | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> các script trực quan hóa |
| Tài liệu phần cứng trong repo | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Công cụ desktop | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Bài báo chuẩn | [Optica Open preprint (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n trong checkout này | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md`, `README.vi.md` |

<p align="center">
  <img src="../images/device_setup.png" alt="Device setup" width="24%">
  <img src="../images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*Bên trái: kính hiển vi truyền qua dạng mô-đun với tay chiếu sáng lưới nhiễu xạ điều khiển bằng động cơ và cụm phát hiện theo trục đứng. Bên phải: GUI thu thập dữ liệu dùng để theo dõi phân đoạn, bù và tái dựng theo thời gian thực.*

> [!TIP]
> Mua bộ kit phát triển cốt lõi (không gồm camera, tube lens và optical table) cho bài [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151) đã preprint trên Optica Open:
> - https://lazying.art/openhi-kit.html
> - Mã ưu đãi giảm 30%: `OPTICA`

## Contents

- [At a Glance 📌](#at-a-glance)
- [Overview 🔭](#overview)
- [Features ✨](#features)
- [Repository Map 🗺️](#repository-map)
- [Project Structure 📁](#project-structure)
- [Quick Start (5-Min Path) ⚡](#quick-start-5-min-path)
- [Prerequisites 🧰](#prerequisites)
- [Installation ⚙️](#installation)
- [Usage 🚀](#usage)
- [Internationalization 🌍](#internationalization)
- [Configuration 🎛️](#configuration)
- [Examples 🧪](#examples)
- [Bill of Materials (Core Module) 🧾](#bill-of-materials-core-module)
- [Core Scripts 🧠](#core-scripts)
- [Additional Tools 🛠️](#additional-tools)
- [Turbo Multi-Scan Compensation ⚡](#turbo-multi-scan-compensation)
- [Parameter Management 💾](#parameter-management)
- [Memory Optimization 🧱](#memory-optimization)
- [Output Structure 📦](#output-structure)
- [Configuration Examples 🧩](#configuration-examples)
- [Wavelength Mapping 🌈](#wavelength-mapping)
- [Tips and Best Practices ✅](#tips-and-best-practices)
- [Development Notes 🧭](#development-notes)
- [Troubleshooting 🩺](#troubleshooting)
- [Roadmap 🛣️](#roadmap)
- [Citation 📎](#citation)
- [Acknowledgements 🙏](#acknowledgements)
- [License 📄](#license)
- [Contributing 🤝](#contributing)
- [Support / Sponsor 💖](#support--sponsor)

## Overview

Khi chiếu sáng quét qua các bước sóng theo thời gian, luồng sự kiện sẽ mã hóa đạo hàm theo thời gian của phổ nền theo trục tán sắc.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

Pipeline này cung cấp 3 giai đoạn chính:

| Giai đoạn | Mục đích | Script chính |
|---|---|---|
| 1. Segment | Tìm thời điểm quét và tách bản ghi thành các lượt thuận/ngược | `segment_robust_fixed.py` |
| 2. Compensate | Ước lượng time-warp từng đoạn tuyến tính để loại bỏ độ nghiêng thời gian do quét | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualize | Chồng ranh giới đã học và so sánh frame gốc với frame đã bù theo thời gian | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

Repository cũng gồm tài nguyên phần cứng, mã GUI thu thập dữ liệu và các nhánh thí nghiệm lưu trữ trong `versions/`.

## Features

- Quy trình xử lý sự kiện end-to-end từ RAW đến phổ.
- Phát hiện chu kỳ quét tự động/thủ công và phân đoạn thuận-ngược.
- Bù đa cửa sổ với chế độ tham số trainable/fixed.
- Lưu/tải tham số ở định dạng `NPZ`, `JSON` và `CSV`.
- Quy trình gộp nhiều lượt quét để lặp huấn luyện nhanh hơn (`compensate_multiwindow_turbo.py`).
- Bộ trực quan hóa cho ranh giới, frame chia bin, đường tích lũy và chẩn đoán có trọng số.
- Tài liệu phần cứng: BOM, PCB, linh kiện 3D, ghi chú firmware.
- Tiện ích thu thập cho hệ camera sự kiện/frame đồng bộ.

| Danh mục | Năng lực có sẵn |
|---|---|
| Xử lý tín hiệu | Segmentation, phát hiện chu kỳ, bù time-warp |
| Tối ưu hóa | Tham số trainable/fixed, điều khiển độ mượt, huấn luyện theo chunk |
| Đầu ra | Overlay trực quan, so sánh tích lũy, chẩn đoán ánh xạ bước sóng |
| Tài nguyên nền tảng | File thiết kế phần cứng, ghi chú firmware, công cụ GUI, kho lưu trữ lịch sử |

## Repository Map

Các tài nguyên phần cứng chính được đặt cạnh mã nguồn để truy cập nhanh:

| Khu vực | Đường dẫn |
|---|---|
| Linh kiện in 3D | [`3D/`](../3D/) |
| Bố cục PCB | [`PCB/`](../PCB/) |
| Firmware vi điều khiển | [`firmware/`](../firmware/) |
| UI thu thập (desktop) | [`ImagingGUI/`](../ImagingGUI/) |
| Tham chiếu thí nghiệm/dữ liệu | [`reference_spectrum_2835/`](../reference_spectrum_2835/), [`reference_spectrum_lumileds/`](../reference_spectrum_lumileds/), [`references/`](../references/) |
| Phân tích căn chỉnh | [`align_background_vs_reference_code/`](../align_background_vs_reference_code/), [`align_data_vs_filter_code/`](../align_data_vs_filter_code/) |

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
├── i18n/
└── versions/
```

## Quick Start (5-Min Path)

Nếu môi trường của bạn đã sẵn sàng và thư mục dataset có file `*event*.raw`:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

Để ép dùng một file RAW cụ thể:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

Wrapper này chạy segmentation, huấn luyện compensation và visualization bằng các đường dẫn script mặc định và cờ CLI mặc định của repo.

> [!TIP]
> Khi kiểm tra lần đầu, hãy chạy wrapper trên một thư mục dataset, rồi xem file NPZ phân đoạn và các đầu ra trực quan trước khi chỉnh các biến `PIPELINE_*`.

## Prerequisites

- Python 3.9+ (Python 3.10+ cho một số công cụ GUI trong `ImagingGUI/`).
- Gói Python lõi: `numpy`, `torch`, `matplotlib`.
- Tùy chọn nhưng thường dùng: `opencv-python`, `pillow`, `cellpose`.
- Metavision SDK / Python bindings cho luồng đọc RAW event (`simple_raw_reader.py`, segmentation từ RAW).
- Khuyến nghị PyTorch hỗ trợ CUDA để tối ưu nhanh hơn.
- Có sẵn bản ghi RAW và/hoặc file NPZ đã phân đoạn cục bộ.

## Installation

Hiện chưa có file môi trường khóa phiên bản ở thư mục gốc repo. Thiết lập đề xuất:

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

Nếu dùng Git hooks để kiểm soát file lớn:

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

Các biến môi trường được `scripts/run_scan_pipeline.sh` hỗ trợ:

| Variable | Default | Purpose |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Tỷ lệ cửa sổ sự kiện hoạt động |
| `PIPELINE_BIN_WIDTH` | `50000` | Độ rộng bin huấn luyện tính bằng microsecond |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Chiều rộng cảm biến cho trực quan hóa |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Chiều cao cảm biến cho trực quan hóa |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Tỷ lệ lấy mẫu sự kiện cho biểu đồ |
| `PIPELINE_TIME_BIN_US` | `1000` | Kích thước activity-bin khi segmentation |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Mẫu file segment cho script phía sau |

## Internationalization

Repository dùng một dòng tùy chọn ngôn ngữ duy nhất ở đầu mỗi README để tránh trùng lặp thanh chuyển ngôn ngữ.

Các file dịch hiện có trong `i18n/`:

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`
- `README.vi.md`

| Liên kết ngôn ngữ trên thanh điều hướng | File trong `i18n/` | Trạng thái |
|---|---|---|

Các liên kết ngôn ngữ theo kế hoạch được giữ có chủ đích ở thanh điều hướng đầu trang để đảm bảo tương thích mở rộng sau này.

## Configuration

Các điều khiển CLI quan trọng dùng xuyên suốt các script:

### Segmentation (`segment_robust_fixed.py`)

- `--time_bin_us`: kích thước activity bin theo microsecond.
- `--round_trip_period`: chu kỳ thủ công (mặc định `1688` bins).
- `--auto_calculate_period`: tính chu kỳ bằng autocorrelation.
- `--activity_fraction`: tỷ lệ cửa sổ sự kiện hoạt động.
- `--manual_start_shift_ms`: độ lệch thời điểm bắt đầu quét thủ công.

### Compensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (mặc định `13`), `--temperature` (mặc định `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` để kiểm soát bộ nhớ.
- `--load_params` để tái sử dụng tham số đã học.

### Visualization

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, các tham số kích thước cảm biến.
- `visualize_cumulative_compare.py`: kích thước cảm biến, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: thang cực tính, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

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

### Legacy helper commands retained from historical workflows

```bash
python scanning_alignment_visualization_save.py \
  led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556_segments/Scan_1_Forward_events.npz \
  --output_dir led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556_segments/FIXED_visualization

python scanning_alignment_visualization_cumulative_compare.py \
  led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556_segments/Scan_1_Forward_events.npz \
  --sensor_width 1280 --sensor_height 720 \
  --output_dir led_12v_no_acc_glass/glass/sync_recording_12v_led_no_acc_blank_event_20250804_232556_segments/cumulative_vs_bin2ms \
  --sample_label "led_12v_no_acc_glass Scan_1_Forward"
```

Các lệnh legacy này được giữ lại có chủ đích để cung cấp ngữ cảnh tương thích; trong checkout hiện tại, hãy ưu tiên các script gốc ở root khi có thể.

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

Xem [`BOM/core_module.md`](../BOM/core_module.md) để có bảng đầy đủ kèm liên kết và ghi chú.

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

**Mục tiêu**: Trích xuất thời điểm quét từ raw events và cắt thành 6 lượt quét một chiều (F, B, F, B, F, B).

**Mô tả toán học**:

- **Tín hiệu hoạt động** (events được chia bin với $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Phát hiện cửa sổ hoạt động**: tìm cửa sổ liên tục nhỏ nhất chứa $80\%$ số events.

- **Ước lượng chu kỳ**: autocorrelation hoặc chu kỳ thủ công (mặc định: $1688$ bins).

- **Tương quan ngược** (cấu trúc thời điểm):
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  với
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**Usage**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Arguments**:

- `--segment_events`: Lưu từng segment quét riêng dưới dạng file NPZ.
- `--round_trip_period 1688`: Dùng chu kỳ thủ công (mặc định).
- `--auto_calculate_period`: Ghi đè chu kỳ thủ công bằng autocorrelation.
- `--activity_fraction 0.80`: Tỷ lệ events cho vùng hoạt động.
- `--max_iterations 2`: Số vòng lặp tinh chỉnh.

### 2. Compensation: `compensate_multiwindow_train_saved_params.py`

**Mục tiêu**: Học tham số time-warp để loại bỏ biến dạng shear theo thời gian do quét, bằng bù từng đoạn tuyến tính đa cửa sổ.

**Mô tả toán học**:

- **Mặt ranh giới**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Độ thuộc cửa sổ mềm**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Nội suy độ dốc (tùy chọn)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Biến đổi thời gian**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Hàm mất mát**: tối thiểu hóa phương sai của các frame chia bin theo thời gian, kèm regularization độ mượt trên tham số.

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

- `--a_trainable` / `--a_fixed`: Điều khiển huấn luyện tham số a (mặc định: fixed).
- `--b_trainable` / `--b_fixed`: Điều khiển huấn luyện tham số b (mặc định: trainable).
- `--num_params 13`: Số tham số ranh giới.
- `--temperature 5000`: Nhiệt độ sigmoid cho cửa sổ mềm.
- `--smoothness_weight 0.001`: Trọng số regularization.
- `--load_params file.npz`: Nạp tham số đã lưu.
- `--chunk_size 250000`: Kích thước chunk xử lý tiết kiệm bộ nhớ.

### 3. Visualization: `visualize_boundaries_and_frames.py`

**Mục tiêu**: Hiển thị các tham số đã học và cho thấy cải thiện định tính.

**Features**:

- Overlay tham số trên các hình chiếu $x\text{–}t$ và $y\text{–}t$.
- So sánh frame chia bin theo thời gian (gốc vs đã bù).
- Phân tích cửa sổ trượt (50 ms và 2 ms bins).
- Ánh xạ bước sóng cho trực quan hóa phổ.

**Usage**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Cumulative Comparison: `visualize_cumulative_compare.py`

**Mục tiêu**: So sánh trung bình tích lũy bước 2 ms với trung bình bin trượt.

**Mô tả toán học**:

- **Trung bình tích lũy**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Trung bình trượt**: số đếm events trong $[T-\Delta,\,T)$ chia cho $H \times W$.

- **Quan hệ** (đạo hàm sai phân hữu hạn):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Usage**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Additional Tools

### GUI Application: `scan_compensation_gui_cloud.py`

Ứng dụng GUI đầy đủ cho bù quét với trực quan hóa phổ 3D.

**Features**:

- Tinh chỉnh tham số tương tác.
- Tiến trình tối ưu thời gian thực.
- Trực quan hóa ánh xạ bước sóng 3D.
- Xuất kết quả và tham số.

**Usage**:

```bash
python scan_compensation_gui_cloud.py
```

### Dual Camera System (current path)

Hệ thống ghi đồng bộ cho camera sự kiện và camera frame:

- `ImagingGUI/DualCamera_separate_transform.py`

**Features**:

- Ghi đồng thời camera sự kiện và camera frame.
- Xem trước thời gian thực kèm biến đổi.
- Điều khiển cửa sổ luôn nằm trên cùng.
- Điều chỉnh tham số trong quá trình ghi.

### Arduino Motor Control (legacy path reference retained)

README gốc từng tham chiếu đường dẫn firmware sketch này:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

Bố cục repository hiện tại chứa ghi chú firmware tại:

- `firmware/README.md`

Sự không khớp đường dẫn này được giữ lại có chủ đích; nếu bạn có các thư mục rotor sketch ở nhánh khác hoặc checkout cục bộ khác, hãy tiếp tục dùng những đường dẫn đó.

Các năng lực legacy đã được ghi nhận của sketch này bao gồm:

- Điều khiển góc chính xác với microstepping.
- Cấu hình tăng/giảm tốc.
- Tích hợp công tắc hành trình.
- Tự động căn tâm.

## Turbo Multi-Scan Compensation

Khi bạn có nhiều lượt quét một chiều (Forward/Backward) của cùng một sweep, bạn có thể gộp chúng và chạy bộ huấn luyện đã kiểm chứng trên một luồng sự kiện kết hợp duy nhất bằng `compensate_multiwindow_turbo.py`.

### What it does

- Chấp nhận một segment, danh sách segment tường minh, hoặc cả thư mục segments.
- Với các lượt Backward, đảo cực tính và đảo thời gian trước khi gộp:
- Nếu cực tính `p ∈ {0,1}`: `p := 1 − p`; sau đó đảo thời gian trong lượt quét.
- Nếu cực tính `p ∈ {−1,1}`: `p := −p`; sau đó đảo thời gian trong lượt quét.
- Nối các lượt quét trên một trục thời gian liên tục (khoảng hở `1 μs` giữa các lượt quét) và gọi `compensate_multiwindow_train_saved_params.py` bên dưới.

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

- `--segment`, `--segments`, `--segments-dir`: chọn tập đầu vào.
- `--include {all|forward|backward}`: lọc theo hướng quét.
- `--sort {name|time}`: thứ tự tên file tự nhiên hoặc thứ tự `start_time` trong NPZ.
- `--bin-width <μs>`: truyền xuống bộ huấn luyện gốc.
- `--load-params`: tái sử dụng tham số đã lưu (bỏ qua huấn luyện và tái tạo đầu ra nhanh ở bin-width mới).
- `--extra ...` sau `--`: mọi cờ bổ sung sẽ được chuyển tiếp tới bộ huấn luyện gốc.

### Speed scaling tip

Nếu lượt quét của bạn nhanh hơn baseline `N×`, hãy giảm `--bin-width` theo cùng hệ số (ví dụ baseline `50 ms` -> nhanh hơn `10×` -> `5 ms`: `--bin-width 5000`). Bạn có thể train một lần (ví dụ `5 ms`), rồi dùng `--load-params` để tái tạo nhanh kết quả ở `10 ms` mà không cần train lại.

## Parameter Management

Hệ thống hỗ trợ đầy đủ chức năng lưu/tải tham số.

### Save Formats

- **NPZ**: Định dạng nhị phân để nạp nhanh.
- **JSON**: Dễ đọc cho con người, kèm metadata.
- **CSV**: Tương thích Excel để kiểm tra thủ công.

### Parameter Loading

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Parameter Files

Tên file được đặt tự động theo số tham số, ví dụ: `*_learned_params_n13.*`.

## Memory Optimization

Hệ thống dùng xử lý theo chunk xuyên suốt:

| Item | Detail |
|---|---|
| Chunk Size | Mặc định `250000` events (có thể cấu hình) |
| Memory Efficient | Xử lý dataset lớn mà không làm tràn bộ nhớ GPU |
| Unified Variance | Duy trì luồng gradient đúng cho quá trình học |
| Progress Tracking | Cập nhật tiến độ xử lý theo thời gian thực |

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

Hệ thống hỗ trợ trực quan hóa phổ bằng cách ánh xạ diễn tiến theo thời gian sang bước sóng:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Dải mặc định**: $380\text{–}680~\text{nm}$ (có thể cấu hình).

## Tips and Best Practices

### Parameter Selection

- **Microstepping**: Dùng `32×` để chuyển động mượt (Arduino).
- **Bin Width**: Bắt đầu với `50 ms` cho tối ưu, `2 ms` cho phân tích.
- **Temperature**: Giá trị cao (quanh `5000`) cho ranh giới mượt hơn.
- **Smoothness**: `0.001` cho regularization tốt.

### Memory Management

- **GPU Memory**: Dùng xử lý theo chunk với kích thước chunk phù hợp.
- **Event Count**: Khuyến nghị `> 10^6` events để học ổn định.
- **Iterations**: Thường `1000` vòng lặp là đủ.

### File Organization

- Giữ file RAW và segments trong cùng thư mục.
- File tham số được tự phát hiện theo quy ước đặt tên.
- Dùng tiền tố tên file mô tả rõ ràng để quản lý đầu ra.

## Development Notes

- `versions.md` mô tả các giai đoạn lịch sử của dự án và lý do chuyển đổi.
- `.githooks/pre-commit` chặn commit quá lớn/nhị phân và loại file không thuộc code/tài liệu.
- `scripts/setup_hooks.sh` đặt `core.hooksPath` thành `.githooks`.
- `archive_code_variants/` lưu các biến thể script cũ để công cụ cấp root tập trung hơn.

Sai lệch tài liệu đã biết (được giữ lại có chủ đích để tương thích ngược):

- Một số tài liệu cũ đề cập `sync_image_system/` hoặc `dual_camera_gui.py`; checkout hiện tại chứa `ImagingGUI/DualCamera_separate_transform.py` và các thư mục SDK.
- `ImagingGUI/README.md` vẫn đề cập `pip install -r requirements.txt`, nhưng checkout hiện tại không có `requirements.txt` ở root.
- `firmware/README.md` đề cập một số thư mục con Arduino sketch không có trong checkout hiện tại.
- `versions.md` nhắc đến tên script legacy khác với tên script root hiện tại.
- `i18n/` tồn tại và hiện có `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md`, và `README.vi.md`; các liên kết ngôn ngữ bổ sung được giữ làm mục tiêu kế hoạch.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Parameter loading errors | Parameter count mismatch | Ensure `--num_params` matches the saved file |
| OOM / memory pressure | Chunk too large or bins too fine | Reduce `--chunk_size` and/or increase `--bin_width` |
| Weak compensation quality | Under-trained or poor segmentation | Increase `--iterations`, enable trainable params, verify segmentation |
| No segment files produced | RAW/SDK/flag issue | Confirm RAW path, Metavision setup, and `--segment_events` |
| Turbo wrapper args ignored | Incorrect forwarding syntax | Pass trainer args after `--` (or use `--extra`) |
| GUI issues | Tkinter/backend or SDK mismatch | Verify GUI backend and camera SDK availability |

- **Parameter loading errors**: Đảm bảo `--num_params` tương thích với file tham số được nạp.
- **OOM / memory pressure**: Giảm `--chunk_size` và/hoặc tăng `--bin_width`.
- **Weak compensation quality**: Tăng `--iterations`, bật tham số trainable (`--a_trainable`, `--b_trainable`, có thể thêm `--boundary_trainable`), và kiểm tra chất lượng segmentation.
- **No segment files produced**: Xác nhận đường dẫn RAW, khả dụng Metavision reader, và đảm bảo đã truyền `--segment_events`.
- **Turbo wrapper argument passing**: Đặt tham số trainer sau `--` (hoặc dùng `--extra`).
- **GUI issues**: Kiểm tra hỗ trợ Tkinter backend và khả dụng camera SDK trên nền tảng của bạn.

## Roadmap

- Cải thiện khả năng tái lập dependency/bootstrap (`requirements.txt` hoặc file lock môi trường).
- Hợp nhất tên script legacy và tham chiếu đường dẫn trên toàn bộ tài liệu.
- Mở rộng mô tả schema dataset và quy ước field NPZ kỳ vọng.
- Bổ sung test dạng regression cho segmentation/compensation trên dữ liệu mẫu nhỏ.
- Tiếp tục tích hợp các đầu ra phân tích chất lượng công bố từ pipeline `align_*`.
- Bổ sung/cập nhật các README đa ngôn ngữ còn lại trong `i18n/` để khớp đầy đủ thanh điều hướng ngôn ngữ ở đầu trang.

## Citation

Nếu repository này hữu ích cho nghiên cứu của bạn, vui lòng trích dẫn preprint Optica Open:

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

## Acknowledgements

- Preprint Optica Open và các tài liệu phổ biến dự án liên quan.
- Những người đóng góp phần cứng và phần mềm xuyên suốt quá trình phát triển repository, được ghi nhận trong `versions/` và các công cụ lưu trữ.
- Sự hỗ trợ từ cộng đồng thông qua GitHub Sponsors và các kênh dự án liên quan.

## License

Dự án này phát hành theo giấy phép MIT. Xem [`LICENSE`](../LICENSE) để biết chi tiết.

## Contributing

Đóng góp luôn được chào đón.

- Bắt đầu từ các script và phong cách tài liệu hiện có.
- Giữ ví dụ dòng lệnh có thể tái lập với đường dẫn trong repository khi có thể.
- Nếu bạn thêm dataset/đầu ra lớn, hãy đảm bảo tuân thủ chính sách `.githooks/pre-commit`.

Lưu ý: checkout hiện tại chưa có `CONTRIBUTING.md` riêng. Nếu cần, hãy mở issue hoặc gửi PR kèm quy trình đóng góp mà bạn đề xuất.

## Support / Sponsor

| Channel | Link | Use |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | Hỗ trợ dự án dài hạn |
| Project site | https://lazying.art | Cập nhật dự án và liên kết hệ sinh thái |
| Community chat | https://chat.lazying.art | Thảo luận cộng đồng |
| Additional creator page | https://onlyideas.art | Nội dung nhà sáng tạo/nghiên cứu liên quan |
| Core kit purchase page | https://lazying.art/openhi-kit.html | Bộ kit phần cứng khởi đầu cho quy trình OpenHI |
| Promotion code | `OPTICA` | Giảm 30% (như đã nêu ở trên) |

---

### Notes

- 📌 README này giữ lại các ghi chú đường dẫn legacy ở nơi layout/tên gọi thay đổi theo quá trình phát triển repository.
- 🔒 Nếu chưa chắc về các tham chiếu cũ, nội dung sẽ được giữ lại có chủ đích thay vì xóa bỏ.
