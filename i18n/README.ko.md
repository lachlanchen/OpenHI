[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# Self-Calibrated Neuromorphic Hyperspectral Imaging (OpenHI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#prerequisites)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#overview)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#repository-map)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#additional-tools)
[![Paper](https://img.shields.io/badge/Preprint-Optica%20Open-ff6b6b.svg)](https://doi.org/10.1364/opticaopen.30739151)
[![i18n](https://img.shields.io/badge/i18n-5%20ready%20%7C%206%20planned-22c55e.svg)](#internationalization)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#overview)

> [!NOTE]
> 이 체크아웃의 i18n 상태: `ar`, `es`, `fr`, `ja`, `ko`가 `i18n/`에 포함되어 있습니다. 추가 언어 링크는 향후 번역 확장을 위한 호환성 유지를 위해 남겨 두었습니다.

회절격자 같은 분산 조명을 사용하는 이벤트 카메라에서 스펙트럼을 재구성하기 위한 종합 파이프라인입니다. 시스템은 강도 변화 이벤트 $e = (x, y, t, p)$를 기록하며, 여기서 $p \in \{-1, +1\}$는 로그 강도 변화의 극성을 의미합니다. 또한 이벤트 스트림에서 스캔 타이밍 및 보정 메타데이터("auto info")를 자동 추론합니다.

## At a Glance

| Item | Details |
|---|---|
| Core idea | 이벤트 스트림 기반 자기 보정 하이퍼스펙트럼 미분 이미징 |
| Main stages | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> 시각화 스크립트 |
| Hardware docs in repo | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Desktop tools | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Canonical paper | [Optica Open preprint (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n in this checkout | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md` |

<p align="center">
  <img src="images/device_setup.png" alt="Device setup" width="24%">
  <img src="images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*왼쪽: 모터 구동 격자 조명 암과 수직 검출 스택을 갖춘 모듈형 투과 현미경. 오른쪽: 세그멘테이션, 보상, 재구성을 실시간으로 모니터링하는 데이터 수집 GUI.*

> [!TIP]
> Optica Open에 프리프린트로 공개된 논문 [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151)의 핵심 개발 키트(카메라, 튜브 렌즈, 광학 테이블 제외) 구매 링크:
> - https://lazying.art/openhi-kit.html
> - 30% 할인 프로모션 코드: `OPTICA`

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

조명이 시간에 따라 파장 방향으로 스윕되면, 이벤트 스트림은 분산 축을 따라 기저 스펙트럼의 시간 미분 정보를 담게 됩니다.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

이 파이프라인은 다음 3단계로 구성됩니다.

| Stage | Purpose | Primary script(s) |
|---|---|---|
| 1. Segment | 스캔 타이밍을 찾고 기록을 정방향/역방향 패스로 분리 | `segment_robust_fixed.py` |
| 2. Compensate | 스캔으로 인한 시간 기울기를 제거하기 위한 구간별 선형 time-warp 추정 | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualize | 학습된 경계를 오버레이하고 보상 전/후 시간 빈 프레임 비교 | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

또한 저장소에는 하드웨어 에셋, 데이터 수집 GUI 코드, `versions/` 아래 실험 아카이브 브랜치가 포함됩니다.

## Features

- RAW에서 스펙트럼까지 이어지는 엔드투엔드 이벤트 처리 워크플로.
- 자동/수동 스캔 주기 검출 및 정/역방향 세그멘테이션.
- 학습 가능/고정 파라미터 모드를 지원하는 멀티 윈도 보상.
- `NPZ`, `JSON`, `CSV` 형식의 파라미터 저장/불러오기.
- 빠른 학습 반복을 위한 멀티 스캔 병합 워크플로(`compensate_multiwindow_turbo.py`).
- 경계, 시간 빈 프레임, 누적 곡선, 가중 진단 시각화 스위트.
- 하드웨어 문서: BOM, PCB, 3D 부품, 펌웨어 노트.
- 이벤트/프레임 카메라 동기화 구성을 위한 데이터 취득 유틸리티.

| Category | Included capabilities |
|---|---|
| Signal processing | 세그멘테이션, 주기 검출, time-warp 보상 |
| Optimization | 학습 가능/고정 파라미터, 스무딩 제어, 청크 학습 |
| Outputs | 시각 오버레이, 누적 비교, 파장 매핑 진단 |
| Platform assets | 하드웨어 설계 파일, 펌웨어 노트, GUI 툴링, 히스토리 아카이브 |

## Repository Map

핵심 하드웨어 에셋은 빠르게 접근할 수 있도록 코드와 함께 같은 저장소에 배치되어 있습니다.

| Area | Path |
|---|---|
| 3D-printed parts | [`3D/`](3D/) |
| PCB layouts | [`PCB/`](PCB/) |
| Microcontroller firmware | [`firmware/`](firmware/) |
| Acquisition UI (desktop) | [`ImagingGUI/`](ImagingGUI/) |
| Experiment/data references | [`reference_spectrum_2835/`](reference_spectrum_2835/), [`reference_spectrum_lumileds/`](reference_spectrum_lumileds/), [`references/`](references/) |
| Alignment analysis | [`align_background_vs_reference_code/`](align_background_vs_reference_code/), [`align_data_vs_filter_code/`](align_data_vs_filter_code/) |

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

환경이 이미 준비되어 있고 데이터셋 폴더에 `*event*.raw` 파일이 있다면:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

특정 RAW 파일을 강제로 지정하려면:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

이 래퍼는 저장소 기본 스크립트 경로 및 CLI 플래그를 사용해 세그멘테이션, 보상 학습, 시각화를 실행합니다.

> [!TIP]
> 초기 검증에서는 먼저 데이터셋 디렉터리 하나에 대해 래퍼를 실행하고, 생성된 segment NPZ 및 시각화 결과를 확인한 뒤 `PIPELINE_*` 변수를 조정하세요.

## Prerequisites

- Python 3.9+ (`ImagingGUI/` 일부 GUI 도구는 Python 3.10+).
- 핵심 Python 패키지: `numpy`, `torch`, `matplotlib`.
- 선택 사항이지만 자주 사용: `opencv-python`, `pillow`, `cellpose`.
- RAW 이벤트 읽기 워크플로(`simple_raw_reader.py`, RAW 기반 세그멘테이션)를 위한 Metavision SDK / Python 바인딩.
- 더 빠른 최적화를 위해 CUDA 지원 PyTorch 권장.
- RAW 기록 파일 및/또는 세그멘트 NPZ 파일이 로컬에 준비되어 있어야 함.

## Installation

현재 저장소 루트에는 고정된 환경 파일이 없습니다. 권장 설정:

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

대용량 파일 위생 관리를 위해 Git hooks를 사용한다면:

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

`scripts/run_scan_pipeline.sh`에서 지원하는 환경 변수:

| Variable | Default | Purpose |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | 활성 이벤트 윈도 비율 |
| `PIPELINE_BIN_WIDTH` | `50000` | 학습 빈 폭 (마이크로초) |
| `PIPELINE_SENSOR_WIDTH` | `1280` | 시각화용 센서 너비 |
| `PIPELINE_SENSOR_HEIGHT` | `720` | 시각화용 센서 높이 |
| `PIPELINE_SAMPLE_RATE` | `0.10` | 플로팅용 이벤트 샘플링 비율 |
| `PIPELINE_TIME_BIN_US` | `1000` | 세그멘테이션 활동 빈 크기 |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | 후속 스크립트용 세그먼트 파일 패턴 |

## Internationalization

저장소는 언어 바 중복을 피하기 위해 각 README 상단에 단일 language-options 줄을 사용합니다.

현재 `i18n/`에 제공되는 번역 파일:

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`

| Language link in nav | File in `i18n/` | Status |
|---|---|---|

상단 내비게이션의 계획 언어 링크는 향후 호환성을 위해 의도적으로 유지합니다.

## Configuration

스크립트 전반에서 자주 사용하는 주요 CLI 제어 옵션:

### Segmentation (`segment_robust_fixed.py`)

- `--time_bin_us`: 활동 빈 크기(마이크로초).
- `--round_trip_period`: 수동 주기(기본값 `1688` bins).
- `--auto_calculate_period`: 자기상관 기반 주기 계산.
- `--activity_fraction`: 활성 이벤트 윈도 비율.
- `--manual_start_shift_ms`: 수동 스캔 시작 오프셋.

### Compensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (기본 `13`), `--temperature` (기본 `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- 메모리 제어용 `--chunk_size`.
- 학습 파라미터 재사용용 `--load_params`.

### Visualization

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, 센서 크기 인자.
- `visualize_cumulative_compare.py`: 센서 크기, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: polarity 스케일, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

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

이 레거시 명령은 호환성 컨텍스트를 위해 의도적으로 보존되어 있습니다. 가능하면 현재 체크아웃의 루트 스크립트를 사용하세요.

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

전체 링크/비고 포함 표는 [`BOM/core_module.md`](BOM/core_module.md)에서 확인하세요.

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

**Goal**: 원시 이벤트에서 스캔 타이밍을 추출하고 6개의 단방향 스캔(F, B, F, B, F, B)으로 분할.

**Mathematical Description**:

- **Activity signal** (events binned with $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Active window detection**: 이벤트의 $80\%$를 포함하는 최소 연속 구간 탐색.

- **Period estimation**: 자기상관 또는 수동 주기(기본값: $1688$ bins).

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

- `--segment_events`: 개별 스캔 세그먼트를 NPZ로 저장.
- `--round_trip_period 1688`: 수동 주기 사용(기본값).
- `--auto_calculate_period`: 수동 주기를 자기상관 결과로 대체.
- `--activity_fraction 0.80`: 활성 영역 이벤트 비율.
- `--max_iterations 2`: 정제 반복 횟수.

### 2. Compensation: `compensate_multiwindow_train_saved_params.py`

**Goal**: 멀티 윈도 구간 선형 보상을 사용해 스캔 유도 시간 전단을 제거하는 time-warp 파라미터 학습.

**Mathematical Description**:

- **Boundary surfaces**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Soft window memberships**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Interpolated slopes (optional)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Time warp**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Loss**: 시간 빈 프레임 분산 최소화 + 파라미터 스무딩 정규화.

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

- `--a_trainable` / `--a_fixed`: a 파라미터 학습 여부 제어(기본: 고정).
- `--b_trainable` / `--b_fixed`: b 파라미터 학습 여부 제어(기본: 학습).
- `--num_params 13`: 경계 파라미터 개수.
- `--temperature 5000`: 소프트 윈도 시그모이드 온도.
- `--smoothness_weight 0.001`: 정규화 가중치.
- `--load_params file.npz`: 저장된 파라미터 불러오기.
- `--chunk_size 250000`: 메모리 효율 처리 청크 크기.

### 3. Visualization: `visualize_boundaries_and_frames.py`

**Goal**: 학습된 파라미터를 표시하고 정성적 개선 결과를 제시.

**Features**:

- $x\text{–}t$ 및 $y\text{–}t$ 투영 위 파라미터 오버레이.
- 시간 빈 프레임 비교(원본 vs 보상).
- 슬라이딩 윈도 분석(50 ms 및 2 ms bins).
- 스펙트럼 시각화를 위한 파장 매핑.

**Usage**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Cumulative Comparison: `visualize_cumulative_compare.py`

**Goal**: 누적 2 ms 단계 평균과 슬라이딩 빈 평균 비교.

**Mathematical Description**:

- **Cumulative means**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Sliding means**: $[T-\Delta,\,T)$ 구간 이벤트 수를 $H \times W$로 나눈 값.

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

3D 스펙트럼 시각화를 포함한 스캔 보상 통합 GUI.

**Features**:

- 인터랙티브 파라미터 튜닝.
- 실시간 최적화 진행 표시.
- 3D 파장 매핑 시각화.
- 결과 및 파라미터 내보내기.

**Usage**:

```bash
python scan_compensation_gui_cloud.py
```

### Dual Camera System (current path)

이벤트 카메라와 프레임 카메라를 동기 기록하는 시스템:

- `ImagingGUI/DualCamera_separate_transform.py`

**Features**:

- 이벤트/프레임 동시 기록.
- 변환 포함 실시간 프리뷰.
- 항상 위 창 제어.
- 기록 중 파라미터 조정.

### Arduino Motor Control (legacy path reference retained)

기존 README에서 참조한 펌웨어 스케치 경로:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

현재 저장소 레이아웃의 펌웨어 노트 위치:

- `firmware/README.md`

이 경로 불일치는 의도적으로 보존했습니다. 다른 브랜치/로컬 체크아웃에 rotor 스케치 폴더가 있다면 기존 경로를 그대로 사용하세요.

이 스케치의 레거시 문서상 기능:

- 마이크로스테핑 기반 정밀 각도 제어.
- 가속/감속 프로파일.
- 리미트 스위치 통합.
- 자동 센터링.

## Turbo Multi-Scan Compensation

같은 스윕의 여러 단방향 스캔(Forward/Backward)이 있을 때 `compensate_multiwindow_turbo.py`로 병합한 뒤 검증된 학습기를 단일 결합 이벤트 스트림에 적용할 수 있습니다.

### What it does

- 단일 세그먼트, 명시적 목록, 또는 세그먼트 디렉터리 전체를 입력으로 허용.
- Backward 스캔은 병합 전에 polarity 반전 + 시간 역순 처리:
- polarity `p ∈ {0,1}`이면: `p := 1 − p`; 이후 스캔 내 시간을 역순화.
- polarity `p ∈ {−1,1}`이면: `p := −p`; 이후 스캔 내 시간을 역순화.
- 스캔을 연속 타임라인으로 이어 붙이고(스캔 사이 `1 μs` 간격), 내부적으로 `compensate_multiwindow_train_saved_params.py` 호출.

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

- `--segment`, `--segments`, `--segments-dir`: 입력 세트 선택.
- `--include {all|forward|backward}`: 스캔 방향 필터.
- `--sort {name|time}`: 파일명 자연 정렬 또는 NPZ `start_time` 정렬.
- `--bin-width <μs>`: 기본 학습기로 전달.
- `--load-params`: 저장 파라미터 재사용(재학습 없이 새 bin 폭 결과를 빠르게 생성).
- `--extra ...` 또는 `--` 뒤 플래그: 기본 학습기로 추가 옵션 전달.

### Speed scaling tip

스캔이 기준 대비 `N×` 빠르면 `--bin-width`를 동일 배수로 줄이세요(예: 기준 `50 ms` -> `10×` 빠름 -> `5 ms`: `--bin-width 5000`). 예를 들어 `5 ms`에서 한 번 학습하고, `--load-params`로 `10 ms` 결과를 재학습 없이 빠르게 생성할 수 있습니다.

## Parameter Management

시스템은 파라미터 저장/불러오기 기능을 폭넓게 지원합니다.

### Save Formats

- **NPZ**: 빠른 로딩을 위한 바이너리 형식.
- **JSON**: 메타데이터를 포함한 사람이 읽기 쉬운 형식.
- **CSV**: 수동 점검에 유용한 엑셀 호환 형식.

### Parameter Loading

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Parameter Files

파일명에는 파라미터 개수가 자동 반영됩니다. 예: `*_learned_params_n13.*`.

## Memory Optimization

시스템 전반에 청크 기반 처리를 사용합니다.

| Item | Detail |
|---|---|
| Chunk Size | 기본 `250000` events (설정 가능) |
| Memory Efficient | 대형 데이터셋을 GPU OOM 없이 처리 |
| Unified Variance | 학습을 위한 올바른 gradient 흐름 유지 |
| Progress Tracking | 실시간 처리 진행 업데이트 |

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

시스템은 시간 변화를 파장으로 매핑해 스펙트럼 시각화를 지원합니다.

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Default Range**: $380\text{–}680~\text{nm}$ (설정 가능).

## Tips and Best Practices

### Parameter Selection

- **Microstepping**: 부드러운 구동을 위해 `32×` 권장(Arduino).
- **Bin Width**: 최적화 시작은 `50 ms`, 분석은 `2 ms` 권장.
- **Temperature**: 더 매끄러운 경계를 위해 높은 값(`5000` 내외) 사용.
- **Smoothness**: `0.001`이 일반적으로 좋은 정규화.

### Memory Management

- **GPU Memory**: 적절한 청크 크기로 chunked processing 사용.
- **Event Count**: 안정적 학습을 위해 `> 10^6` events 권장.
- **Iterations**: 보통 `1000` 반복이면 충분.

### File Organization

- RAW 파일과 segments는 같은 디렉터리에 보관.
- 파라미터 파일은 명명 규칙으로 자동 탐지.
- 출력 정리를 위해 설명적인 파일명 접두사 사용.

## Development Notes

- `versions.md`에는 프로젝트의 역사적 단계와 마이그레이션 이유가 설명되어 있습니다.
- `.githooks/pre-commit`은 과대형/바이너리 커밋 및 비코드/비문서 파일 유형을 차단합니다.
- `scripts/setup_hooks.sh`는 `core.hooksPath`를 `.githooks`로 설정합니다.
- `archive_code_variants/`는 루트 툴링을 단순하게 유지하기 위해 이전 스크립트 변형을 보관합니다.

문서 드리프트(하위 호환 문맥 유지를 위해 의도적으로 보존):

- 일부 구문서는 `sync_image_system/` 또는 `dual_camera_gui.py`를 언급하지만, 현재 체크아웃에는 `ImagingGUI/DualCamera_separate_transform.py`와 SDK 디렉터리가 있습니다.
- `ImagingGUI/README.md`는 여전히 `pip install -r requirements.txt`를 참조하지만, 현재 체크아웃 루트에는 `requirements.txt`가 없습니다.
- `firmware/README.md`는 현재 체크아웃에 없는 여러 Arduino 스케치 하위 폴더를 참조합니다.
- `versions.md`는 현재 루트 스크립트명과 다른 레거시 스크립트명을 언급합니다.
- `i18n/`에는 현재 `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md`가 포함되어 있으며, 추가 언어 링크는 계획 대상으로 유지됩니다.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Parameter loading errors | Parameter count mismatch | Ensure `--num_params` matches the saved file |
| OOM / memory pressure | Chunk too large or bins too fine | Reduce `--chunk_size` and/or increase `--bin_width` |
| Weak compensation quality | Under-trained or poor segmentation | Increase `--iterations`, enable trainable params, verify segmentation |
| No segment files produced | RAW/SDK/flag issue | Confirm RAW path, Metavision setup, and `--segment_events` |
| Turbo wrapper args ignored | Incorrect forwarding syntax | Pass trainer args after `--` (or use `--extra`) |
| GUI issues | Tkinter/backend or SDK mismatch | Verify GUI backend and camera SDK availability |

- **Parameter loading errors**: `--num_params`가 로드한 파라미터 파일과 호환되는지 확인하세요.
- **OOM / memory pressure**: `--chunk_size`를 줄이고/또는 `--bin_width`를 늘리세요.
- **Weak compensation quality**: `--iterations`를 늘리고, 학습 가능 파라미터(`--a_trainable`, `--b_trainable`, 필요 시 `--boundary_trainable`)를 활성화하고, 세그멘테이션 품질을 점검하세요.
- **No segment files produced**: RAW 경로, Metavision reader 가용성, `--segment_events` 전달 여부를 확인하세요.
- **Turbo wrapper argument passing**: 학습기 인자는 `--` 뒤(또는 `--extra`)에 전달하세요.
- **GUI issues**: 플랫폼의 Tkinter 백엔드 및 카메라 SDK 가용성을 확인하세요.

## Roadmap

- 의존성/부트스트랩 재현성 개선(`requirements.txt` 또는 환경 lockfile).
- 문서 전반의 레거시 스크립트명/경로 참조 정리.
- 데이터셋 스키마 및 예상 NPZ 필드 규약 문서 보강.
- 소형 픽스처 데이터를 이용한 세그멘테이션/보상 회귀 테스트 추가.
- `align_*` 파이프라인의 출판 품질 분석 출력 통합 지속.
- 상단 언어 네비게이션 링크와 완전히 일치하도록 `i18n/`의 나머지 다국어 README 추가/갱신.

## Citation

이 저장소가 연구에 도움이 되었다면 Optica Open 프리프린트를 인용해 주세요.

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

- Optica Open 프리프린트 및 관련 프로젝트 확산 자료.
- `versions/` 및 아카이브 툴링으로 기록된 저장소 발전 과정의 하드웨어/소프트웨어 기여자들.
- GitHub Sponsors 및 연계 프로젝트 채널을 통한 커뮤니티 지원.

## License

이 프로젝트는 MIT License로 배포됩니다. 자세한 내용은 [`LICENSE`](LICENSE)를 참조하세요.

## Contributing

기여를 환영합니다.

- 기존 스크립트와 문서 스타일을 기준으로 작업해 주세요.
- 가능한 경우 저장소 경로를 사용하는 재현 가능한 CLI 예시를 유지해 주세요.
- 대용량 데이터셋/출력을 추가할 때는 `.githooks/pre-commit` 정책 준수를 확인해 주세요.

참고: 이 체크아웃에는 별도 `CONTRIBUTING.md`가 없습니다. 필요하면 이슈를 열거나 제안하는 기여 워크플로와 함께 PR을 제출해 주세요.

## Support / Sponsor

| Channel | Link | Use |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | 지속적인 프로젝트 지원 |
| Project site | https://lazying.art | 프로젝트 업데이트 및 생태계 링크 |
| Community chat | https://chat.lazying.art | 커뮤니티 토론 |
| Additional creator page | https://onlyideas.art | 관련 크리에이터/연구 콘텐츠 |
| Core kit purchase page | https://lazying.art/openhi-kit.html | OpenHI 워크플로용 하드웨어 스타터 키트 |
| Promotion code | `OPTICA` | 30% 할인(위 내용과 동일) |

---

### Notes

- 📌 이 README는 저장소 진화 과정에서 발생한 이름/레이아웃 드리프트를 반영해 레거시 경로 노트를 유지합니다.
- 🔒 오래된 참조가 불확실한 경우, 삭제보다 보존을 우선해 의도적으로 텍스트를 남겨 두었습니다.
