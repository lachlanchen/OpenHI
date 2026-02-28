[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# التصوير الطيفي فائق الدقة العصبي ذاتي المعايرة (OpenHI)

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
> حالة i18n في هذا الإصدار المحلي: الملفات `ar`, `es`, `fr`, `ja`, `ko` موجودة تحت `i18n/`. تم الإبقاء على روابط اللغات الإضافية للتوافق مع خطة الترجمة المستقبلية.

منظومة متكاملة لإعادة بناء الأطياف من كاميرات الأحداث تحت إضاءة مشتتة (مثل محزوز الحيود). يسجّل النظام أحداث تغيّر الشدة بالشكل $e = (x, y, t, p)$ حيث يشير $p \in \{-1, +1\}$ إلى قطبية تغيّر لوغاريتم الشدة، ويستنتج تلقائيًا توقيت المسح وبيانات المعايرة الوصفية ("auto info") مباشرةً من تيار الأحداث.

## At a Glance

| Item | Details |
|---|---|
| Core idea | تصوير طيفي اشتقاقي ذاتي المعايرة من تيارات الأحداث |
| Main stages | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> visualization scripts |
| Hardware docs in repo | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Desktop tools | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Canonical paper | [Optica Open preprint (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n in this checkout | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md` |

<p align="center">
  <img src="images/device_setup.png" alt="Device setup" width="24%">
  <img src="images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*يسارًا: مجهر نفاذية معياري مع ذراع إضاءة بمحزوز متحرك آليًا ومكدس كشف عمودي. يمينًا: واجهة جمع البيانات المستخدمة لمراقبة التقسيم والتعويض وإعادة البناء لحظيًا.*

> [!TIP]
> يمكنك شراء حزمة التطوير الأساسية (باستثناء الكاميرا، وعدسة الأنبوب، والطاولة البصرية) الخاصة بورقة [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151) المنشورة كنسخة تمهيدية على Optica Open:
> - https://lazying.art/openhi-kit.html
> - رمز خصم 30%: `OPTICA`

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

عندما تمسح الإضاءة عبر الأطوال الموجية بمرور الزمن، يشفّر تيار الأحداث مشتقةً زمنية للطيف الأساسي على محور التشتت.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

يوفّر هذا المسار ثلاث مراحل رئيسية:

| Stage | Purpose | Primary script(s) |
|---|---|---|
| 1. Segment | إيجاد توقيت المسح وتقسيم التسجيلات إلى مسارات أمامية/خلفية | `segment_robust_fixed.py` |
| 2. Compensate | تقدير تشوّه زمني خطي-قطعي لإزالة الميل الزمني الناتج عن المسح | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualize | تراكب الحدود المتعلَّمة ومقارنة الإطارات المجمّعة زمنيًا قبل/بعد التعويض | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

يتضمن المستودع أيضًا أصول العتاد، وكود واجهة جمع البيانات، وفروع تجارب مؤرشفة ضمن `versions/`.

## Features

- سير عمل كامل لمعالجة الأحداث من RAW إلى الطيف.
- كشف فترة المسح تلقائيًا/يدويًا مع التقسيم إلى أمامي وخلفي.
- تعويض متعدد النوافذ مع أوضاع معاملات قابلة للتدريب أو ثابتة.
- حفظ/تحميل المعاملات بصيغ `NPZ`, `JSON`, `CSV`.
- سير دمج متعدد المسحات لتسريع تكرارات التدريب (`compensate_multiwindow_turbo.py`).
- حزمة تصوّر للحدود، والإطارات المجمعة، والمنحنيات التراكمية، والتشخيصات الموزونة.
- توثيق العتاد: BOM وPCB وقطع ثلاثية الأبعاد وملاحظات firmware.
- أدوات اقتناء للأنظمة المتزامنة بين كاميرا الأحداث وكاميرا الإطارات.

| Category | Included capabilities |
|---|---|
| Signal processing | التقسيم، كشف الفترة، تعويض التشوّه الزمني |
| Optimization | معاملات قابلة للتدريب/ثابتة، ضوابط النعومة، تدريب مُجزّأ |
| Outputs | تراكبات مرئية، مقارنات تراكمية، تشخيصات مع تعيين طيفي |
| Platform assets | ملفات تصميم العتاد، ملاحظات firmware، أدوات GUI، أرشيفات تاريخية |

## Repository Map

تُحفظ الأصول العتادية الأساسية بجانب الكود لسهولة الوصول السريع:

| Area | Path |
|---|---|
| أجزاء مطبوعة ثلاثية الأبعاد | [`3D/`](3D/) |
| مخططات PCB | [`PCB/`](PCB/) |
| Firmware المتحكم الدقيق | [`firmware/`](firmware/) |
| واجهة الاقتناء (سطح المكتب) | [`ImagingGUI/`](ImagingGUI/) |
| مراجع التجارب/البيانات | [`reference_spectrum_2835/`](reference_spectrum_2835/), [`reference_spectrum_lumileds/`](reference_spectrum_lumileds/), [`references/`](references/) |
| تحليل المحاذاة | [`align_background_vs_reference_code/`](align_background_vs_reference_code/), [`align_data_vs_filter_code/`](align_data_vs_filter_code/) |

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

إذا كانت البيئة جاهزة بالفعل وكان مجلد بياناتك يحتوي ملف `*event*.raw`:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

لفرض ملف RAW محدد:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

يشغّل هذا المغلّف التقسيم، وتدريب التعويض، والتصوّر باستخدام مسارات السكربتات وخيارات CLI الافتراضية في المستودع.

> [!TIP]
> للتحقق الأولي، شغّل المغلّف على مجلد بيانات واحد ثم افحص ملف segment NPZ والمخرجات المرئية الناتجة قبل ضبط متغيرات `PIPELINE_*`.

## Prerequisites

- Python 3.9+ (وPython 3.10+ لبعض أدوات GUI ضمن `ImagingGUI/`).
- حزم Python الأساسية: `numpy`, `torch`, `matplotlib`.
- اختياري لكنه شائع: `opencv-python`, `pillow`, `cellpose`.
- Metavision SDK / Python bindings لقراءة RAW المعتمدة على الأحداث (`simple_raw_reader.py` والتقسيم من RAW).
- يُنصح بـ PyTorch مع CUDA لتسريع التحسين.
- توفر تسجيلات RAW و/أو ملفات NPZ المقسّمة محليًا.

## Installation

لا يوجد حاليًا ملف بيئة مقفل عند جذر المستودع. الإعداد المقترح:

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

إذا كنت تستخدم Git hooks لضبط الملفات الكبيرة:

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

متغيرات البيئة التي يدعمها `scripts/run_scan_pipeline.sh`:

| Variable | Default | Purpose |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | نسبة نافذة الأحداث النشطة |
| `PIPELINE_BIN_WIDTH` | `50000` | عرض حاوية التدريب بالميكروثانية |
| `PIPELINE_SENSOR_WIDTH` | `1280` | عرض الحساس للتصوّر |
| `PIPELINE_SENSOR_HEIGHT` | `720` | ارتفاع الحساس للتصوّر |
| `PIPELINE_SAMPLE_RATE` | `0.10` | نسبة أخذ العينات من الأحداث للرسم |
| `PIPELINE_TIME_BIN_US` | `1000` | حجم حاوية النشاط للتقسيم |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | نمط ملف المقطع للسكربتات اللاحقة |

## Internationalization

يستخدم المستودع سطرًا واحدًا لخيارات اللغة أعلى كل README لتجنّب تكرار شريط اللغات.

ملفات الترجمة المتوفرة حاليًا داخل `i18n/`:

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`

| Language link in nav | File in `i18n/` | Status |
|---|---|---|

تم الإبقاء عمدًا على روابط اللغات المخطط لها في شريط التنقل العلوي للتوافق المستقبلي.

## Configuration

أهم خيارات CLI المستخدمة عبر السكربتات:

### Segmentation (`segment_robust_fixed.py`)

- `--time_bin_us`: حجم حاوية النشاط بالميكروثانية.
- `--round_trip_period`: فترة يدوية (الافتراضي `1688` حاوية).
- `--auto_calculate_period`: تقدير الفترة عبر الارتباط الذاتي.
- `--activity_fraction`: نسبة نافذة الأحداث النشطة.
- `--manual_start_shift_ms`: إزاحة يدوية لبداية المسح.

### Compensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (الافتراضي `13`), `--temperature` (الافتراضي `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` للتحكم بالذاكرة.
- `--load_params` لإعادة استخدام المعاملات المتعلَّمة.

### Visualization

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, ومعاملات حجم الحساس.
- `visualize_cumulative_compare.py`: حجم الحساس، `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: مقاييس القطبية، `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

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

هذه الأوامر القديمة محفوظة عمدًا كسياق توافق؛ في هذا الإصدار استخدم سكربتات الجذر الحالية متى أمكن.

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

راجع [`BOM/core_module.md`](BOM/core_module.md) للاطلاع على الجدول الكامل مع الروابط والملاحظات.

### Table S2. Acquisition Time and Cost Comparison Between the Proposed Event-Driven System and a Reference Hyperspectral Camera

| Parameter | Ours | Reference camera |
|---|---|---|
| Acquisition time | ∼585 ms per scan | 300 s per scan |
| Data volume | 18.5 MB | 138 MB |
| Approx. price | ∼3000 USD | 14 000 USD |

### Table S3. Bill of Materials for the Core Scanning Illumination Module
(باستثناء كاميرا الأحداث وبصريات التحقق 4f الاختيارية)

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

**الهدف**: استخراج توقيت المسح من أحداث RAW وتقطيعها إلى 6 مسحات أحادية الاتجاه (F, B, F, B, F, B).

**الوصف الرياضي**:

- **إشارة النشاط** (تجميع الأحداث بحاويات زمنية $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **كشف النافذة النشطة**: إيجاد أصغر نافذة متجاورة تحتوي على $80\%$ من الأحداث.

- **تقدير الفترة**: ارتباط ذاتي أو فترة يدوية (الافتراضي: $1688$ حاوية).

- **الارتباط العكسي** (بنية التوقيت):
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  حيث
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**Usage**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Arguments**:

- `--segment_events`: حفظ مقاطع المسح الفردية كملفات NPZ.
- `--round_trip_period 1688`: استخدام فترة يدوية (الافتراضي).
- `--auto_calculate_period`: تجاوز الفترة اليدوية بالارتباط الذاتي.
- `--activity_fraction 0.80`: نسبة الأحداث للمنطقة النشطة.
- `--max_iterations 2`: عدد تكرارات التحسين.

### 2. Compensation: `compensate_multiwindow_train_saved_params.py`

**الهدف**: تعلّم معاملات تشوّه زمني لإزالة القص الزمني الناتج عن المسح باستخدام تعويض خطي-قطعي متعدد النوافذ.

**الوصف الرياضي**:

- **سطوح الحدود**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **انتماءات النوافذ الناعمة**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **ميول مستوفاة (اختياري)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **التشويه الزمني**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **دالة الخسارة**: تصغير التباين للإطارات المجمعة زمنيًا مع انتظام نعومة على المعاملات.

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

- `--a_trainable` / `--a_fixed`: التحكم في تدريب معاملات a (الافتراضي: ثابتة).
- `--b_trainable` / `--b_fixed`: التحكم في تدريب معاملات b (الافتراضي: قابلة للتدريب).
- `--num_params 13`: عدد معاملات الحدود.
- `--temperature 5000`: حرارة sigmoid للنوافذ الناعمة.
- `--smoothness_weight 0.001`: وزن الانتظام.
- `--load_params file.npz`: تحميل معاملات محفوظة.
- `--chunk_size 250000`: حجم دفعة معالجة فعّال للذاكرة.

### 3. Visualization: `visualize_boundaries_and_frames.py`

**الهدف**: عرض المعاملات المتعلَّمة وإبراز التحسينات النوعية.

**Features**:

- تراكب المعاملات على إسقاطات $x\text{–}t$ و$y\text{–}t$.
- مقارنة الإطارات المجمعة زمنيًا (الأصلية مقابل المعوَّضة).
- تحليل نافذة منزلقة (حاويات 50 ms و2 ms).
- تعيين أطوال موجية للتصوّر الطيفي.

**Usage**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Cumulative Comparison: `visualize_cumulative_compare.py`

**الهدف**: مقارنة المتوسطات التراكمية بخطوة 2 ms مع متوسطات الحاويات المنزلقة.

**الوصف الرياضي**:

- **المتوسطات التراكمية**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **المتوسطات المنزلقة**: عدد الأحداث في $[T-\Delta,\,T)$ مقسومًا على $H \times W$.

- **العلاقة** (مشتقة بالفروق المحدودة):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Usage**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Additional Tools

### GUI Application: `scan_compensation_gui_cloud.py`

واجهة GUI كاملة لتعويض المسح مع تصوّر طيفي ثلاثي الأبعاد.

**Features**:

- ضبط تفاعلي للمعاملات.
- تقدم التحسين في الزمن الحقيقي.
- تصوّر ثلاثي الأبعاد مع تعيين الطول الموجي.
- تصدير النتائج والمعاملات.

**Usage**:

```bash
python scan_compensation_gui_cloud.py
```

### Dual Camera System (current path)

نظام تسجيل متزامن لكاميرا الأحداث وكاميرا الإطارات:

- `ImagingGUI/DualCamera_separate_transform.py`

**Features**:

- تسجيل متزامن للأحداث والإطارات.
- معاينة فورية مع تحويلات.
- أدوات نوافذ دائمة الظهور.
- ضبط المعاملات أثناء التسجيل.

### Arduino Motor Control (legacy path reference retained)

أشار README الأصلي إلى مسار firmware sketch التالي:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

تخطيط المستودع الحالي يتضمن ملاحظات firmware هنا:

- `firmware/README.md`

عدم تطابق المسارات هذا محفوظ عمدًا؛ إذا كانت مجلدات rotor sketch لديك في فرع آخر أو نسخة محلية أخرى، فاستمر باستخدام تلك المسارات.

القدرات الموثقة تاريخيًا لهذا sketch تشمل:

- تحكم دقيق بالزاوية مع microstepping.
- ملفات تسارع/تباطؤ.
- تكامل limit switch.
- وظيفة التمركز التلقائي.

## Turbo Multi-Scan Compensation

عند توفر مسحات أحادية الاتجاه متعددة (Forward/Backward) لنفس sweep، يمكنك دمجها وتشغيل المدرب المُجرّب على تيار أحداث مدمج واحد باستخدام `compensate_multiwindow_turbo.py`.

### What it does

- يقبل مقطعًا واحدًا، أو قائمة صريحة، أو مجلد مقاطع كامل.
- لمسحات Backward، يقلب القطبية ويعكس الزمن قبل الدمج:
- إذا كانت القطبية `p ∈ {0,1}`: `p := 1 − p`; ثم اعكس الزمن داخل المسح.
- إذا كانت القطبية `p ∈ {−1,1}`: `p := −p`; ثم اعكس الزمن داخل المسح.
- يضم المسحات على خط زمني مستمر (بفاصل `1 μs` بين المسحات) ويستدعي `compensate_multiwindow_train_saved_params.py` داخليًا.

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

- `--segment`, `--segments`, `--segments-dir`: اختيار مجموعة الإدخال.
- `--include {all|forward|backward}`: التصفية حسب اتجاه المسح.
- `--sort {name|time}`: ترتيب طبيعي للأسماء أو ترتيب `start_time` من NPZ.
- `--bin-width <μs>`: يُمرَّر إلى المدرب الأساسي.
- `--load-params`: إعادة استخدام معاملات محفوظة (تجاوز التدريب وإعادة إنتاج المخرجات سريعًا عند عروض حاويات جديدة).
- `--extra ...` بعد `--`: أي رايات إضافية تُمرَّر إلى المدرب الأساسي.

### Speed scaling tip

إذا كان المسح أسرع بمقدار `N×` من الأساس، خفّض `--bin-width` بالنسبة نفسها (مثلًا الأساس `50 ms` -> أسرع `10×` -> `5 ms`: `--bin-width 5000`). يمكنك التدريب مرة واحدة (مثلًا `5 ms`) ثم استخدام `--load-params` لإعادة توليد النتائج بسرعة عند `10 ms` دون إعادة تدريب.

## Parameter Management

يدعم النظام وظائف شاملة لحفظ/تحميل المعاملات.

### Save Formats

- **NPZ**: صيغة ثنائية للتحميل السريع.
- **JSON**: صيغة مقروءة للبشر مع بيانات وصفية.
- **CSV**: متوافقة مع Excel للفحص اليدوي.

### Parameter Loading

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Parameter Files

تُسمّى الملفات تلقائيًا بعدد المعاملات، مثل: `*_learned_params_n13.*`.

## Memory Optimization

يستخدم النظام المعالجة المُجزأة (chunked processing) عبر المسار كاملًا:

| Item | Detail |
|---|---|
| Chunk Size | الافتراضي `250000` حدث (قابل للتعديل) |
| Memory Efficient | يعالج مجموعات بيانات كبيرة دون فيضان ذاكرة GPU |
| Unified Variance | يحافظ على تدفق تدرج صحيح أثناء التعلم |
| Progress Tracking | تحديثات معالجة لحظية |

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

يدعم النظام التصوّر الطيفي عبر تعيين التطور الزمني إلى الطول الموجي:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**النطاق الافتراضي**: $380\text{–}680~\text{nm}$ (قابل للتعديل).

## Tips and Best Practices

### Parameter Selection

- **Microstepping**: استخدم `32×` لحركة أكثر سلاسة (Arduino).
- **Bin Width**: ابدأ بـ `50 ms` للتحسين، و`2 ms` للتحليل.
- **Temperature**: قيم أعلى (حوالي `5000`) لحدود أنعم.
- **Smoothness**: `0.001` يوفّر انتظامًا جيدًا.

### Memory Management

- **GPU Memory**: استخدم المعالجة المُجزأة مع حجم chunk مناسب.
- **Event Count**: يُنصح بأكثر من `10^6` حدث لتعلم مستقر.
- **Iterations**: عادةً تكفي `1000` تكرار.

### File Organization

- احتفظ بملفات RAW والمقاطع في الدليل نفسه.
- ملفات المعاملات تُكتشف تلقائيًا عبر نمط التسمية.
- استخدم بادئات أسماء ملفات وصفية لتنظيم المخرجات.

## Development Notes

- يصف `versions.md` المراحل التاريخية للمشروع وأسباب الهجرة بين الإصدارات.
- يمنع `.githooks/pre-commit` الالتزامات كبيرة الحجم/الثنائية وأنواع الملفات غير البرمجية/غير التوثيقية.
- يقوم `scripts/setup_hooks.sh` بضبط `core.hooksPath` إلى `.githooks`.
- يحتوي `archive_code_variants/` على نسخ سكربتات أقدم لإبقاء أدوات الجذر مركّزة.

انحرافات توثيق معروفة (محفوظة عمدًا لسياق التوافق العكسي):

- بعض الوثائق القديمة تذكر `sync_image_system/` أو `dual_camera_gui.py`; الإصدار الحالي يحتوي `ImagingGUI/DualCamera_separate_transform.py` وأدلة SDK.
- `ImagingGUI/README.md` لا يزال يشير إلى `pip install -r requirements.txt`، لكن لا يوجد `requirements.txt` في جذر هذا الإصدار.
- يشير `firmware/README.md` إلى عدة مجلدات Arduino sketch غير موجودة في هذا الإصدار.
- يذكر `versions.md` أسماء سكربتات قديمة تختلف عن أسماء سكربتات الجذر الحالية.
- `i18n/` موجود ويحتوي حاليًا `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md`; وروابط اللغات الإضافية محفوظة كأهداف مخططة.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Parameter loading errors | Parameter count mismatch | Ensure `--num_params` matches the saved file |
| OOM / memory pressure | Chunk too large or bins too fine | Reduce `--chunk_size` and/or increase `--bin_width` |
| Weak compensation quality | Under-trained or poor segmentation | Increase `--iterations`, enable trainable params, verify segmentation |
| No segment files produced | RAW/SDK/flag issue | Confirm RAW path, Metavision setup, and `--segment_events` |
| Turbo wrapper args ignored | Incorrect forwarding syntax | Pass trainer args after `--` (or use `--extra`) |
| GUI issues | Tkinter/backend or SDK mismatch | Verify GUI backend and camera SDK availability |

- **أخطاء تحميل المعاملات**: تأكد أن `--num_params` متوافق مع ملف المعاملات المحمّل.
- **OOM / ضغط ذاكرة**: خفّض `--chunk_size` و/أو زد `--bin_width`.
- **ضعف جودة التعويض**: زد `--iterations`، وفعّل المعاملات القابلة للتدريب (`--a_trainable`, `--b_trainable`, واختياريًا `--boundary_trainable`) وتحقق من جودة التقسيم.
- **عدم إنتاج ملفات المقاطع**: تأكد من مسار RAW، وتوفّر Metavision، وتمرير `--segment_events`.
- **تجاهل وسائط Turbo wrapper**: مرّر وسائط المدرب بعد `--` (أو استخدم `--extra`).
- **مشكلات GUI**: تحقق من دعم Tkinter/backend وتوفّر SDK الكاميرا على منصتك.

## Roadmap

- تحسين قابلية إعادة إنتاج الاعتماديات/الإقلاع (`requirements.txt` أو ملف قفل بيئة).
- توحيد أسماء السكربتات القديمة ومراجع المسارات عبر التوثيق.
- توسيع توثيق مخططات البيانات المتوقعة واتفاقيات حقول NPZ.
- إضافة اختبارات نمط regression للتقسيم/التعويض على بيانات fixtures صغيرة.
- الاستمرار في دمج مخرجات تحليل بجودة نشر من مسارات `align_*`.
- إضافة/تحديث بقية ملفات README متعددة اللغات داخل `i18n/` لتطابق روابط التنقل اللغوي أعلى الصفحة بالكامل.

## Citation

إذا كان هذا المستودع مفيدًا في بحثك، يُرجى الاستشهاد بالنسخة التمهيدية على Optica Open:

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

- النسخة التمهيدية على Optica Open وما يرتبط بها من مواد نشر المشروع.
- مساهمو العتاد والبرمجيات عبر تطور المستودع كما هو موثق في `versions/` والأدوات المؤرشفة.
- دعم المجتمع عبر GitHub Sponsors وقنوات المشروع المرتبطة.

## License

يُنشر هذا المشروع تحت رخصة MIT. راجع [`LICENSE`](LICENSE) للتفاصيل.

## Contributing

المساهمات مرحب بها.

- ابدأ من السكربتات الحالية وأسلوب التوثيق القائم.
- حافظ على إمكانية إعادة تنفيذ أمثلة سطر الأوامر باستخدام مسارات المستودع متى أمكن.
- إذا أضفت مجموعات بيانات/مخرجات كبيرة، فتأكد من الالتزام بسياسات `.githooks/pre-commit`.

ملاحظة: لا يوجد ملف `CONTRIBUTING.md` مخصص في هذا الإصدار. عند الحاجة، افتح issue أو أرسل PR مع سير المساهمة الذي تقترحه.

## Support / Sponsor

| Channel | Link | Use |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | دعم المشروع المستمر |
| Project site | https://lazying.art | تحديثات المشروع وروابط المنظومة |
| Community chat | https://chat.lazying.art | نقاشات المجتمع |
| Additional creator page | https://onlyideas.art | محتوى بحثي/إبداعي ذي صلة |
| Core kit purchase page | https://lazying.art/openhi-kit.html | حزمة عتاد بداية لمسار OpenHI |
| Promotion code | `OPTICA` | خصم 30% (كما هو موثق أعلاه) |

---

### Notes

- 📌 يحافظ هذا README على ملاحظات المسارات القديمة عندما سبّب تطور المستودع اختلافات في التسمية أو البنية.
- 🔒 عند عدم اليقين حول المراجع الأقدم، يُحفَظ النص عمدًا بدلًا من حذفه.
