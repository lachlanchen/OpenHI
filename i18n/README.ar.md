[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

# التصوير الطيفي فائق الدقة العصبي ذاتي المعايرة (OpenHI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#prerequisites)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#overview)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#repository-map)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#additional-tools)
[![Paper](https://img.shields.io/badge/Paper-Optica-ff6b6b.svg)](https://doi.org/10.1364/OPTICA.585766)
[![i18n](https://img.shields.io/badge/i18n-10%20translated%20%7C%20English%20base-22c55e.svg)](#internationalization)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#overview)
[![Quick Start](https://img.shields.io/badge/QuickStart-5%20min%20path-16a34a.svg)](#quick-start-5-min-path)
[![BOM](https://img.shields.io/badge/BOM-Core%20module%20available-f59e0b.svg)](#bill-of-materials-core-module)
[![Quickstart Doc](https://img.shields.io/badge/Guide-QUICKSTART.md-334155.svg)](../QUICKSTART.md)

> [!NOTE]
> حالة i18n في هذا الإصدار المحلي: جميع ملفات الترجمة المرتبطة موجودة ضمن `i18n/` (`ar`, `de`, `es`, `fr`, `ja`, `ko`, `ru`, `vi`, `zh-Hans`, `zh-Hant`) مع اعتماد الإنجليزية كملف README مرجعي أساسي.

مسار عمل شامل لإعادة بناء الأطياف من كاميرات الأحداث تحت إضاءة ضوئية مشتتة (مثل محزوز حيود). يسجّل النظام أحداث تغيّر الشدة بالشكل $e = (x, y, t, p)$ حيث $p \in \{-1, +1\}$ يعبّر عن قطبية تغيّر لوغاريتم الشدة، كما يستنتج تلقائيًا توقيت المسح وبيانات المعايرة الوصفية ("auto info") مباشرةً من تيار الأحداث.

> [!IMPORTANT]
> هذا README هو المصدر التقني المرجعي في جذر المستودع. يجب أن تعكس الملفات المحلية تحت `i18n/` تطور الأقسام/العناوين، مع سطر واحد فقط لخيارات اللغة في الأعلى (من دون تكرار شريط اللغات).

<p align="center">
  <img src="../images/device_setup.png" alt="Device setup" width="24%">
  <img src="../images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*يسارًا: مجهر نفاذية معياري مع ذراع إضاءة بمحزوز متحرك آليًا ومكدس كشف عمودي. يمينًا: واجهة جمع بيانات لمراقبة التقسيم والتعويض وإعادة البناء في الزمن الحقيقي.*


## Quick Access

| الحاجة | الانتقال السريع |
|---|---|
| بدء التشغيل خلال ~5 دقائق | [Quick Start (5-Min Path) ⚡](#quick-start-5-min-path) |
| تشغيل الغلاف الكامل للمسار | [`scripts/run_scan_pipeline.sh`](../scripts/run_scan_pipeline.sh) |
| فهم تدفق السكربتات | [Overview 🔭](#overview)، [Core Scripts 🧠](#core-scripts) |
| ضبط المعاملات | [Configuration 🎛️](#configuration)، [Configuration Examples 🧩](#configuration-examples) |
| استخدام أدوات GUI | [Additional Tools 🛠️](#additional-tools) |
| توثيق العتاد (BOM/PCB/3D/Firmware) | [Repository Map 🗺️](#repository-map) |
| قواعد صيانة التعدد اللغوي | [Internationalization 🌍](#internationalization) |
| روابط الدعم/الرعاية | [Support / Sponsor 💖](#support--sponsor) |

## At a Glance

| العنصر | التفاصيل |
|---|---|
| الفكرة الأساسية | تصوير طيفي اشتقاقي ذاتي المعايرة من تيارات الأحداث |
| المراحل الرئيسية | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> سكربتات التصوّر |
| توثيق العتاد داخل المستودع | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| أدوات سطح المكتب | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| الورقة المرجعية | [مقالة Optica (DOI: 10.1364/OPTICA.585766)](https://doi.org/10.1364/OPTICA.585766) |
| i18n في هذا الإصدار | `README.ar.md`, `README.de.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md`, `README.ru.md`, `README.vi.md`, `README.zh-Hans.md`, `README.zh-Hant.md` |

### Compatibility Snapshot

| المجال | الواقع الحالي في المستودع |
|---|---|
| خط أساس Python | يوصى بـ `3.9+` (وبعض أدوات `ImagingGUI/` تشير إلى `3.10+`) |
| مشغّل المسار الرئيسي | `scripts/run_scan_pipeline.sh` |
| سكربت التدريب الأساسي | `compensate_multiwindow_train_saved_params.py` |
| أصول العتاد | موجودة ضمن `3D/`, `PCB/`, `BOM/`, `firmware/` |
| التوثيق متعدد اللغات | يحتوي `i18n/` على ملفات اللغات العشر المرتبطة |



> [!TIP]
> اشترِ حزمة التطوير الأساسية (من دون الكاميرا، وعدسة الأنبوب، والطاولة البصرية) الخاصة بورقة [Self-calibrated neuromorphic hyperspectral derivative imaging](https://doi.org/10.1364/OPTICA.585766) المنشورة في Optica:
> - https://lazying.art/openhi-kit.html
> - رمز ترويجي بخصم 30%: `OPTICA`

## Contents

- [Quick Access ⚡](#quick-access)
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

> [!IMPORTANT]
> سياسة مصدر المحتوى المرجعي في هذا المستودع: أبقِ `README.md` الإنجليزي في الجذر كمرجع تقني، واعمَل على عكس تطور الأقسام والعناوين في كل ملفات `i18n/README.*.md` مع سطر واحد فقط لخيارات اللغة في الأعلى.

## Overview

عندما تتحرك الإضاءة عبر الأطوال الموجية بمرور الزمن، يشفّر تيار الأحداث مشتقة زمنية من الطيف الكامن على محور التشتت.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

### Pipeline Legend

| الأيقونة | المعنى |
|---|---|
| 🧩 | التقسيم / فصل المسحات |
| 🧠 | التعويض / تعلم المعاملات |
| 🖼️ | تشخيصات مرئية / فحص المخرجات |
| 🌈 | تعيين الأطوال الموجية / التصيير الطيفي |

يوفّر هذا المسار ثلاث مراحل رئيسية:

| المرحلة | الغرض | السكربتات الأساسية |
|---|---|---|
| 1. Segment | اكتشاف توقيت المسح وتقسيم التسجيلات إلى مرور أمامي/خلفي | `segment_robust_fixed.py` |
| 2. Compensate | تقدير تشوّه زمني خطيّ-قطعي لإزالة الميل الزمني الناتج عن المسح | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualize | تراكب الحدود المتعلّمة ومقارنة الإطارات المجمّعة زمنيًا قبل/بعد التعويض | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

يتضمن المستودع أيضًا أصول العتاد، وكود واجهة جمع البيانات، وفروع تجارب مؤرشفة تحت `versions/`.

### Scope and Assumptions

- هذا المستودع موجّه للبحث ويتضمن سكربتات نشطة إضافةً إلى تجارب/نتائج مؤرشفة.
- أوامر هذا README تفترض التنفيذ من جذر المستودع ما لم يُذكر خلاف ذلك.
- بعض المسارات الاختيارية تعتمد على SDK خارجية (Metavision، وحزم SDK لموردي الكاميرات) وبيانات محلية غير مضمّنة في هذا المستودع.
- إذا أشار أمر إلى مسار تاريخي غير موجود، ففضّل سكربتات الجذر المحدّثة المدرجة هنا، مع الإبقاء على الملاحظات القديمة للتوافق الخلفي.

## Features

- سير عمل متكامل لمعالجة الأحداث من RAW إلى طيف.
- كشف فترة المسح تلقائيًا/يدويًا مع التقسيم إلى مرور أمامي وخلفي.
- تعويض متعدد النوافذ مع أوضاع معاملات قابلة للتدريب أو ثابتة.
- حفظ/تحميل المعاملات بصيغ `NPZ`, `JSON`, `CSV`.
- سير دمج متعدد المسحات لتسريع تكرارات التدريب (`compensate_multiwindow_turbo.py`).
- مجموعة تصوّر للحدود والإطارات المجمّعة والمنحنيات التراكمية والتشخيصات الموزونة.
- توثيق عتاد: BOM وPCB وقطع 3D وملاحظات firmware.
- أدوات اقتناء لإعدادات كاميرا أحداث/إطارات متزامنة.

| الفئة | القدرات المتضمنة |
|---|---|
| معالجة الإشارة | التقسيم، كشف الفترة، تعويض التشوّه الزمني |
| التحسين | معاملات قابلة للتدريب/ثابتة، ضوابط النعومة، تدريب مجزّأ |
| المخرجات | تراكبات مرئية، مقارنات تراكمية، تشخيصات مع تعيين للأطوال الموجية |
| أصول المنصة | ملفات تصميم العتاد، ملاحظات firmware، أدوات GUI، أرشيفات تاريخية |

## Repository Map

تُحفَظ أصول العتاد الرئيسية بجانب الشيفرة لتسهيل الوصول السريع:

| المجال | المسار |
|---|---|
| أجزاء مطبوعة ثلاثيًا | [`3D/`](../3D/) |
| مخططات PCB | [`PCB/`](../PCB/) |
| firmware المتحكم الدقيق | [`firmware/`](../firmware/) |
| واجهة جمع البيانات (سطح المكتب) | [`ImagingGUI/`](../ImagingGUI/) |
| مراجع تجريبية/بيانات | [`comparisons/reference_spectrum_2835/`](../comparisons/reference_spectrum_2835/), [`comparisons/reference_spectrum_lumileds/`](../comparisons/reference_spectrum_lumileds/), [`references/`](../references/) |
| تحليل المحاذاة | [`comparisons/align_background_vs_reference_code/`](../comparisons/align_background_vs_reference_code/), [`comparisons/alignment_configs/`](../comparisons/alignment_configs/) |

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
├── comparisons/align_background_vs_reference_code/
├── align_data_vs_filter_code/
├── comparisons/alignment_configs/
├── versions/05_archive_code_variants/
├── comparisons/outputs_root/
├── comparisons/reference_filters/
├── comparisons/reference_spectrum_2835/
├── comparisons/reference_spectrum_lumileds/
├── references/
├── i18n/
└── versions/
```

## Quick Start (5-Min Path)

إذا كانت بيئتك مجهزة مسبقًا وكان مجلد البيانات يحتوي على ملف `*event*.raw`:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

لفرض ملف RAW محدد:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

يشغّل هذا الغلاف التقسيم، وتدريب التعويض، والتصوّر باستخدام مسارات السكربتات الافتراضية في المستودع وخيارات CLI الافتراضية.

> [!TIP]
> للتحقق الأولي، شغّل الغلاف على مجلد بيانات واحد، ثم راجع ملف NPZ الناتج عن التقسيم ومخرجات التصوّر قبل ضبط متغيرات `PIPELINE_*`.

## Prerequisites

- Python 3.9+ (و Python 3.10+ لبعض أدوات GUI داخل `ImagingGUI/`).
- الحزم الأساسية: `numpy`, `torch`, `matplotlib`.
- حزم اختيارية شائعة: `opencv-python`, `pillow`, `cellpose`, `spectral`.
- حزمة اختيارية حسب المنصة: `pywin32` (عادةً لوِرش SDK الكاميرا على Windows).
- Metavision SDK / Python bindings لمسارات قراءة RAW (`simple_raw_reader.py` والتقسيم من RAW).
- يُنصح بـ PyTorch مدعوم CUDA لتسريع التحسين.
- توفر تسجيلات RAW و/أو ملفات NPZ المقسّمة محليًا.

## Installation

لا يوجد ملف بيئة مُقفل في جذر المستودع حاليًا. إعداد مقترح:

```bash
# create and activate a virtual environment or conda env
python -m venv .venv
source .venv/bin/activate

# install core dependencies
pip install numpy matplotlib torch

# optional tools often used in this repository
pip install opencv-python pillow
# pip install cellpose
# pip install spectral pywin32
```

إذا كنت تستخدم Git hooks لضبط الملفات الكبيرة:

```bash
bash scripts/setup_hooks.sh
```

مستحسن (اختياري) لفحوصات قابلية إعادة الإنتاج:

```bash
python -c "import numpy, torch, matplotlib; print('core deps ok')"
python -c "import torch; print('cuda:', torch.cuda.is_available())"
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

### Command-to-Output Reference

| الخطوة | نقطة تشغيل الأمر | المخرج الأساسي |
|---|---|---|
| Segment scans | `segment_robust_fixed.py` | `*_segments/Scan_*_{Forward,Backward}_events.npz` |
| Train compensation | `compensate_multiwindow_train_saved_params.py` | `*learned_params_n*.{npz,json,csv}` + تشخيصات مرئية |
| Boundary/frame diagnostics | `visualize_boundaries_and_frames.py` | مجلد تصوّر مختوم بالطابع الزمني مع تراكبات وتجميعات |
| Cumulative diagnostics | `visualize_cumulative_compare.py`, `visualize_cumulative_weighted.py` | مخططات تراكمية/إحصائية لفحص جودة المسح |
| Full convenience run | `scripts/run_scan_pipeline.sh` | تقسيم + تدريب + تصوّر من طرف إلى طرف |

### One-command convenience wrapper

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

### Minimal Smoke Test (no training changes)

استخدم هذا عندما تريد التحقق سريعًا من ترابط السكربتات على ملف segment NPZ موجود قبل تشغيل تحسين طويل:

```bash
# quick visualization pass
python visualize_boundaries_and_frames.py /path/to/Scan_1_Forward_events.npz \
  --sample_rate 0.05 --sensor_width 1280 --sensor_height 720

# quick cumulative diagnostics
python visualize_cumulative_compare.py /path/to/Scan_1_Forward_events.npz \
  --sensor_width 1280 --sensor_height 720
```

متغيرات البيئة التي يدعمها `scripts/run_scan_pipeline.sh`:

| المتغير | الافتراضي | الغرض |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | نسبة نافذة الأحداث النشطة |
| `PIPELINE_BIN_WIDTH` | `50000` | عرض bin للتدريب بالميكروثانية |
| `PIPELINE_SENSOR_WIDTH` | `1280` | عرض الحساس للتصوّر |
| `PIPELINE_SENSOR_HEIGHT` | `720` | ارتفاع الحساس للتصوّر |
| `PIPELINE_SAMPLE_RATE` | `0.10` | نسبة أخذ عينات الأحداث للرسم |
| `PIPELINE_TIME_BIN_US` | `1000` | حجم bin النشاط للتقسيم |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | نمط ملف segment للسكربتات اللاحقة |

### Figure-oriented wrapper (publication workflow)

```bash
scripts/prepare_figure04.sh /path/to/dataset_dir [raw_file]
```

يشغّل هذا الغلاف التقسيم، والتشخيصات، والتعويض، والرسم بإعدادات مناسبة لمسار إعداد الأشكال العلمية.

> [!NOTE]
> في هذا الإصدار المحلي، يشير `scripts/prepare_figure04.sh` إلى `publication_code/figure02_scan_segmentation.py`، لكن مجلد `publication_code/` غير موجود. احتفظ بهذا المسار إذا كان فرعك المحلي يحتوي هذا المجلد؛ وإلا فالأفضل استخدام `scripts/run_scan_pipeline.sh`.

## Internationalization

يستخدم المستودع سطرًا واحدًا فقط لخيارات اللغة أعلى كل README لتجنّب تكرار شريط اللغات.

الملفات المترجمة المتاحة حاليًا داخل `i18n/`:

- `README.ar.md`
- `README.de.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`
- `README.ru.md`
- `README.vi.md`
- `README.zh-Hans.md`
- `README.zh-Hant.md`

### Language Coverage Matrix

| اللغة/المنطقة | الملف | التغطية |
|---|---|---|
| العربية | `README.ar.md` | ✅ موجود |
| الألمانية | `README.de.md` | ✅ موجود |
| الإسبانية | `README.es.md` | ✅ موجود |
| الفرنسية | `README.fr.md` | ✅ موجود |
| اليابانية | `README.ja.md` | ✅ موجود |
| الكورية | `README.ko.md` | ✅ موجود |
| الروسية | `README.ru.md` | ✅ موجود |
| الفيتنامية | `README.vi.md` | ✅ موجود |
| الصينية (المبسطة) | `README.zh-Hans.md` | ✅ موجود |
| الصينية (التقليدية) | `README.zh-Hant.md` | ✅ موجود |

| رابط اللغة في الشريط | الملف في `i18n/` | الحالة |
|---|---|---|
| العربية | `README.ar.md` | متوفر |
| Deutsch | `README.de.md` | متوفر |
| Español | `README.es.md` | متوفر |
| Français | `README.fr.md` | متوفر |
| 日本語 | `README.ja.md` | متوفر |
| 한국어 | `README.ko.md` | متوفر |
| Русский | `README.ru.md` | متوفر |
| Tiếng Việt | `README.vi.md` | متوفر |
| 中文 (简体) | `README.zh-Hans.md` | متوفر |
| 中文（繁體） | `README.zh-Hant.md` | متوفر |

يجب أن تحافظ جميع نسخ README على سطر واحد فقط لخيارات اللغة في الأعلى (من دون شريط لغات مكرر)، بما يتوافق مع `.auto-readme-work/*/language-nav-*.md`.

> [!NOTE]
> قاعدة صيانة التعدد اللغوي للتعديلات القادمة: بعد أي تعديل في أقسام الملف الجذر، حدّث كل ملف لغة واحدًا تلو الآخر، واحرص على عدم تكرار شريط اللغات في أي README محلي.

### Multilingual Update Checklist

1. حدّث ملف الجذر `README.md` أولًا.
2. تأكد من وجود `i18n/` وملفات اللغات المطلوبة.
3. حدّث كل ملف `i18n/README.<lang>.md` واحدًا تلو الآخر (من دون نسخ مجمّع لمحتوى قديم).
4. حافظ على سطر واحد فقط لخيارات اللغة في أعلى كل نسخة README.
5. تحقّق من عدم وجود أشرطة لغات مكررة في الجذر أو الملفات المحلية.

## Configuration

أهم خيارات CLI المستخدمة عبر السكربتات:

### Segmentation (`segment_robust_fixed.py`)

- `--time_bin_us`: حجم bin النشاط بالميكروثانية.
- `--round_trip_period`: فترة يدوية (الافتراضي `1688` bins).
- `--auto_calculate_period`: حساب الفترة عبر autocorrelation.
- `--activity_fraction`: نسبة نافذة الأحداث النشطة.
- `--manual_start_shift_ms`: إزاحة يدوية لبداية المسح.

### Compensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (الافتراضي `13`)، `--temperature` (الافتراضي `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` للتحكم بالذاكرة.
- `--load_params` لإعادة استخدام معاملات متعلّمة.

### Visualization

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, وخيارات حجم الحساس.
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

تم الإبقاء على هذه الأوامر القديمة عمدًا لتوفير سياق التوافق؛ في هذا الإصدار المحلي استخدم سكربتات الجذر الحالية كلما أمكن.

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

راجع [`BOM/core_module.md`](../BOM/core_module.md) للاطلاع على الجدول الكامل مع الروابط والملاحظات.

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

**الهدف**: استخراج توقيت المسح من الأحداث الخام وتقطيعها إلى 6 مسحات أحادية الاتجاه (F, B, F, B, F, B).

**الوصف الرياضي**:

- **إشارة النشاط** (تجميع الأحداث ضمن bins بحجم $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **اكتشاف النافذة النشطة**: إيجاد أصغر نافذة متصلة تحتوي على $80\%$ من الأحداث.

- **تقدير الفترة**: autocorrelation أو فترة يدوية (الافتراضي: $1688$ bins).

- **الارتباط العكسي** (بنية التوقيت):
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  حيث
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**الاستخدام**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**المعاملات**:

- `--segment_events`: حفظ مقاطع المسح الفردية كملفات NPZ.
- `--round_trip_period 1688`: استخدام فترة يدوية (افتراضي).
- `--auto_calculate_period`: تجاوز الفترة اليدوية بحساب autocorrelation.
- `--activity_fraction 0.80`: نسبة الأحداث لمنطقة النشاط.
- `--max_iterations 2`: عدد تكرارات التحسين.

### 2. Compensation: `compensate_multiwindow_train_saved_params.py`

**الهدف**: تعلّم معاملات التشوّه الزمني لإزالة القص الزمني الناتج عن المسح عبر تعويض خطي-قطعي متعدد النوافذ.

**الوصف الرياضي**:

- **أسطح الحدود**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **انتماءات نوافذ ناعمة**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **ميول مستوفاة (اختياري)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **التشوّه الزمني**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **دالة الخسارة**: تقليل تباين الإطارات المجمعة زمنيًا مع تنظيم نعومة على المعاملات.

**الاستخدام**:

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**أهم المعاملات**:

- `--a_trainable` / `--a_fixed`: التحكم في تدريب a (الافتراضي: ثابت).
- `--b_trainable` / `--b_fixed`: التحكم في تدريب b (الافتراضي: قابل للتدريب).
- `--num_params 13`: عدد معاملات الحدود.
- `--temperature 5000`: درجة حرارة sigmoid للنوافذ الناعمة.
- `--smoothness_weight 0.001`: وزن التنظيم.
- `--load_params file.npz`: تحميل معاملات محفوظة.
- `--chunk_size 250000`: حجم تجزئة لمعالجة موفرة للذاكرة.

### 3. Visualization: `visualize_boundaries_and_frames.py`

**الهدف**: عرض المعاملات المتعلّمة وإظهار التحسن النوعي.

**الميزات**:

- تراكب المعاملات على إسقاطات $x\text{–}t$ و $y\text{–}t$.
- مقارنة الإطارات المجمعة زمنيًا (أصلي مقابل مُعوَّض).
- تحليل نافذة منزلقة (50 ms و 2 ms bins).
- تعيين أطوال موجية للتصوّر الطيفي.

**الاستخدام**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Cumulative Comparison: `visualize_cumulative_compare.py`

**الهدف**: مقارنة المتوسطات التراكمية بخطوة 2 ms مع متوسطات النوافذ المنزلقة.

**الوصف الرياضي**:

- **المتوسطات التراكمية**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **المتوسطات المنزلقة**: عدد الأحداث في $[T-\Delta,\,T)$ مقسومًا على $H \times W$.

- **العلاقة** (مشتقة فروق منتهية):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**الاستخدام**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Additional Tools

### GUI Application: `scan_compensation_gui_cloud.py`

واجهة GUI كاملة لتعويض المسح مع تصوّر طيفي ثلاثي الأبعاد.

**الميزات**:

- ضبط تفاعلي للمعاملات.
- متابعة تقدم التحسين في الزمن الحقيقي.
- تصوّر ثلاثي الأبعاد مع تعيين الأطوال الموجية.
- تصدير النتائج والمعاملات.

**الاستخدام**:

```bash
python scan_compensation_gui_cloud.py
```

### Dual Camera System (current path)

نظام تسجيل متزامن لكاميرا الأحداث وكاميرا الإطارات:

- `ImagingGUI/DualCamera_separate_transform.py`

**الميزات**:

- تسجيل متزامن للأحداث والإطارات.
- معاينة فورية مع التحويلات.
- عناصر تحكم نافذة always-on-top.
- ضبط المعاملات أثناء التسجيل.

### Hyperspectral ENVI utilities

سكربتات داخل المستودع لعرض ENVI cube، واستخراج ROI، وتجهيزات التصوّر:

- `show_envi_spectrum_gui.py`
- `scripts/hs_to_rgb.py`
- `scripts/envi_export_frames.py`
- `scripts/envi_crop_by_roi.py`
- `scripts/hs_gradient_wavelength.py`
- `scripts/cellpose_roi.py`
- `scripts/cellpose_simple_mask.py`
- `scripts/roi_template_match.py`

نقطة تشغيل نموذجية:

```bash
python show_envi_spectrum_gui.py
```

### Arduino Motor Control (legacy path reference retained)

كان README الأصلي يشير إلى مسار firmware التالي:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

التخطيط الحالي للمستودع يتضمن ملاحظات firmware هنا:

- `firmware/README.md`

هذا الاختلاف في المسارات محفوظ عمدًا؛ إذا كانت مجلدات rotor sketch لديك في فرع/نسخة محلية أخرى، فاستمر باستخدام تلك المسارات.

قدرات sketch الموثقة تاريخيًا (والمحفوظة هنا للتوافق):

- تحكم دقيق بالزاوية مع microstepping.
- ملفات تسارع/تباطؤ.
- تكامل limit switch.
- وظيفة تمركز تلقائي.

## Turbo Multi-Scan Compensation

عند توفر عدة مسحات أحادية الاتجاه (Forward/Backward) للمسح نفسه، يمكنك دمجها وتشغيل المدرب المُثبت على تيار أحداث مدمج واحد باستخدام `compensate_multiwindow_turbo.py`.

### What it does

- يقبل segment واحدًا، أو قائمة صريحة، أو مجلد segments كامل.
- في المسحات Backward، يقلب القطبية ويعكس الزمن قبل الدمج:
- إذا كانت القطبية `p ∈ {0,1}`: تصبح `p := 1 − p`، ثم يُعكس الزمن داخل المسح.
- إذا كانت القطبية `p ∈ {−1,1}`: تصبح `p := −p`، ثم يُعكس الزمن داخل المسح.
- يضمّ المسحات على خط زمني مستمر (بفاصل `1 μs` بين المسحات) ويستدعي `compensate_multiwindow_train_saved_params.py` داخليًا.

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
- `--include {all|forward|backward}`: تصفية حسب اتجاه المسح.
- `--sort {name|time}`: ترتيب طبيعي بالأسماء أو وفق `start_time` داخل NPZ.
- `--bin-width <μs>`: يُمرَّر إلى المدرب الأساسي.
- `--load-params`: إعادة استخدام معاملات محفوظة (تخطي التدريب وإعادة توليد المخرجات سريعًا بعروض bin جديدة).
- `--extra ...` بعد `--`: أي خيارات إضافية تُمرَّر إلى المدرب الأساسي.

### Speed scaling tip

إذا كانت المسحة أسرع بمقدار `N×` من خط الأساس، فخفّض `--bin-width` بنفس النسبة (مثلًا: خط أساس `50 ms` -> أسرع `10×` -> `5 ms`: استخدم `--bin-width 5000`). يمكنك التدريب مرة واحدة (مثلًا عند `5 ms`)، ثم استخدام `--load-params` لإعادة توليد النتائج بسرعة عند `10 ms` دون إعادة تدريب.

## Parameter Management

يدعم النظام آلية شاملة لحفظ/تحميل المعاملات.

### Save Formats

- **NPZ**: صيغة ثنائية للتحميل السريع.
- **JSON**: صيغة مقروءة مع metadata.
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

تُسمى الملفات تلقائيًا وفق عدد المعاملات، مثل: `*_learned_params_n13.*`.

## Memory Optimization

يستخدم النظام معالجة مجزأة في جميع المراحل:

| العنصر | التفاصيل |
|---|---|
| Chunk Size | الافتراضي `250000` حدث (قابل للضبط) |
| Memory Efficient | معالجة مجموعات بيانات كبيرة دون تجاوز ذاكرة GPU |
| Unified Variance | الحفاظ على تدفق gradients صحيح أثناء التعلم |
| Progress Tracking | تحديثات معالجة في الزمن الحقيقي |

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

### Typical Generated Artifacts

| نمط الملف | يُنتج بواسطة | الأهمية |
|---|---|---|
| `*_segments/Scan_*_events.npz` | التقسيم | مدخلات تدريب/تصوّر معيارية لكل مسح |
| `*learned_params_n13.npz` (وكذلك `.json`, `.csv`) | مدرب التعويض | إعادة الاستخدام، قابلية إعادة الإنتاج، والفحص |
| `visualization_YYYYmmdd_HHMMSS/` | سكربتات التصوّر / وضع التصوّر في المدرب | عزل مخرجات كل تشغيل بالطابع الزمني |
| `events_with_params.png` ومخططات الإطارات/التراكمي | سكربتات التصوّر | تحقق نوعي من تأثيرات التعويض |

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

يدعم النظام التصوّر الطيفي عبر ربط التطور الزمني بالطول الموجي:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**المدى الافتراضي**: $380\text{–}680~\text{nm}$ (قابل للضبط).

## Tips and Best Practices

### Parameter Selection

- **Microstepping**: استخدم `32×` لحركة سلسة (Arduino).
- **Bin Width**: ابدأ بـ `50 ms` للتحسين، و`2 ms` للتحليل.
- **Temperature**: القيم الأعلى (حوالي `5000`) لحدود أكثر نعومة.
- **Smoothness**: القيمة `0.001` تمنح تنظيمًا جيدًا.

### Memory Management

- **GPU Memory**: استخدم المعالجة المجزأة بحجم chunk مناسب.
- **Event Count**: يوصى بـ `> 10^6` حدث للتعلم المستقر.
- **Iterations**: غالبًا ما تكون `1000` تكرار كافية.

### File Organization

- أبقِ ملفات RAW وsegments في الدليل نفسه.
- تُكتشف ملفات المعاملات تلقائيًا وفق نمط التسمية.
- استخدم بادئات أسماء واضحة لتنظيم المخرجات.

## Development Notes

- يصف `versions.md` المراحل التاريخية للمشروع وأسباب الانتقال بينها.
- يمنع `.githooks/pre-commit` عمليات commit كبيرة/ثنائية وأنواع ملفات غير كود/توثيق.
- يضبط `scripts/setup_hooks.sh` قيمة `core.hooksPath` إلى `.githooks`.
- يحتوي `versions/05_archive_code_variants/` على نسخ سكربتات أقدم للحفاظ على تركيز أدوات الجذر الحالية.

### Developer Workflow Notes

- فضّل `scripts/run_scan_pipeline.sh` لتشغيلات baseline القابلة لإعادة الإنتاج، ثم انتقل لضبط السكربتات بشكل منفصل.
- اعتبر المسارات تحت `comparisons/` مثل `outputs_root/`, `reference_*`, و`align_*` مساحات مختلطة للتحليل/التاريخ؛ لا تفترض أنها عينات اختبار دنيا فقط.
- عند إضافة سكربتات جديدة، احرص أن تبقى نقاط الدخول في الجذر واضحة من هذا README مع ربط المستندات ذات الصلة (`QUICKSTART.md` وREADME الخاصة بالمجلدات الفرعية).

انحرافات توثيق معروفة (محفوظة عمدًا للتوافق الخلفي):

- تشير بعض الوثائق القديمة إلى `sync_image_system/` أو `dual_camera_gui.py`؛ بينما هذا الإصدار يحتوي `ImagingGUI/DualCamera_separate_transform.py` وأدلة SDK.
- لا يزال `ImagingGUI/README.md` يشير إلى `pip install -r requirements.txt`، لكن لا يوجد `requirements.txt` في الجذر بهذا الإصدار.
- يشير `firmware/README.md` إلى مجلدات Arduino sketch فرعية غير موجودة في هذا الإصدار.
- يذكر `versions.md` أسماء سكربتات قديمة تختلف عن أسماء السكربتات الحالية في الجذر.
- يتضمن `i18n/` حاليًا كل الملفات المرتبطة في شريط اللغات (`ar`, `de`, `es`, `fr`, `ja`, `ko`, `ru`, `vi`, `zh-Hans`, `zh-Hant`)؛ حافظ على تزامن ملفات الجذر والترجمة عند تعديل العناوين/الأقسام.

## Troubleshooting

| العَرَض | السبب المحتمل | الإجراء |
|---|---|---|
| أخطاء تحميل المعاملات | عدم تطابق عدد المعاملات | تأكد أن `--num_params` يطابق الملف المحفوظ |
| OOM / ضغط ذاكرة | chunk كبير جدًا أو bins دقيقة جدًا | قلّل `--chunk_size` و/أو زد `--bin_width` |
| جودة تعويض ضعيفة | تدريب غير كافٍ أو تقسيم ضعيف | زد `--iterations`، فعّل معاملات قابلة للتدريب، وتحقق من جودة التقسيم |
| عدم إنتاج ملفات segment | مشكلة في RAW/SDK/flags | تحقق من مسار RAW وإعداد Metavision ووجود `--segment_events` |
| تجاهل معاملات turbo wrapper | صياغة تمرير خاطئة | مرّر معاملات المدرب بعد `--` (أو استخدم `--extra`) |
| مشاكل GUI | عدم توافق Tkinter/backend أو SDK | تحقق من backend للواجهة وتوفر SDK الكاميرا |

قائمة فحص موسعة للأعطال (محفوظة للفحص السريع):

- **أخطاء تحميل المعاملات**: تأكد من توافق `--num_params` مع ملف المعاملات المحمّل.
- **OOM / ضغط ذاكرة**: قلّل `--chunk_size` و/أو زد `--bin_width`.
- **جودة تعويض ضعيفة**: زد `--iterations`، فعّل المعاملات القابلة للتدريب (`--a_trainable`, `--b_trainable`, واختياريًا `--boundary_trainable`)، وتحقق من جودة التقسيم.
- **لا توجد ملفات segment ناتجة**: تحقق من مسار RAW، وتوفر قارئ Metavision، وتمرير `--segment_events`.
- **تمرير معاملات Turbo wrapper**: ضع معاملات المدرب بعد `--` (أو استخدم `--extra`).
- **مشاكل GUI**: تحقق من دعم Tkinter backend وتوفر SDK الكاميرا على منصتك.

## Roadmap

- تحسين قابلية إعادة إنتاج بيئة التشغيل (`requirements.txt` أو lockfile للبيئة).
- توحيد أسماء السكربتات القديمة وإشارات المسارات عبر التوثيق.
- توسيع توثيق مخططات البيانات المتوقعة وحقول NPZ.
- إضافة اختبارات نمط regression للتقسيم/التعويض على بيانات fixture صغيرة.
- مواصلة دمج مخرجات تحليل بجودة نشر علمي من مسارات `align_*`.
- الحفاظ على تزامن README الجذر وجميع ملفات `i18n/README.*.md` مع تطور الأقسام.

## Citation

إذا كان هذا المستودع مفيدًا لأبحاثك، يُرجى الاستشهاد بمقالة Optica:

```bibtex
@article{chen2026self,
  title   = {Self-calibrated neuromorphic hyperspectral derivative imaging},
  author  = {Chen, Rongzhou and Wang, Chutian and Li, Yuxing and Cao, Yuqing and Zhu, Shuo and Lam, Edmund},
  journal = {Optica},
  volume  = {13},
  number  = {4},
  pages   = {587--590},
  year    = {2026},
  publisher = {Optica Publishing Group},
  doi     = {10.1364/OPTICA.585766}
}
```

## Acknowledgements

- مقالة Optica المنشورة والمواد المرتبطة بنشر المشروع.
- مساهمو العتاد والبرمجيات عبر تطور المستودع كما هو موثق في `versions/` والأدوات المؤرشفة.
- دعم المجتمع عبر GitHub Sponsors وقنوات المشروع المرتبطة.

## License

هذا المشروع مرخّص بموجب MIT License. راجع [`LICENSE`](../LICENSE) للتفاصيل.

## Contributing

المساهمات مرحب بها.

- ابدأ من نمط السكربتات والتوثيق الحالي.
- احرص على أن تكون أمثلة سطر الأوامر قابلة لإعادة التشغيل باستخدام مسارات المستودع قدر الإمكان.
- عند إضافة بيانات/مخرجات كبيرة، التزم بسياسات `.githooks/pre-commit`.

ملاحظة: لا يوجد `CONTRIBUTING.md` مخصص في هذا الإصدار المحلي. عند الحاجة، افتح issue أو أرسل PR يتضمن آلية المساهمة التي تقترحها.

## Support / Sponsor

| القناة | الرابط | الاستخدام |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | دعم المشروع واستدامته |
| موقع المشروع | https://lazying.art | تحديثات المشروع وروابط المنظومة |
| دردشة المجتمع | https://chat.lazying.art | نقاشات المجتمع |
| صفحة منشئ إضافية | https://onlyideas.art | محتوى منشئ/بحثي ذي صلة |
| صفحة شراء الحزمة الأساسية | https://lazying.art/openhi-kit.html | حزمة عتاد البداية لمسار OpenHI |
| رمز ترويجي | `OPTICA` | خصم 30% (كما ورد أعلاه) |

### Support Scope

| نوع الدعم | أفضل قناة |
|---|---|
| التمويل والاستدامة | GitHub Sponsors |
| منظومة البناء/الشراء | صفحة OpenHI kit على `lazying.art` |
| استكشاف أخطاء المجتمع | `chat.lazying.art` |
| تحديثات المشروع العامة | `lazying.art` وصفحات المنشئ |

---

### Notes

- 📌 يحافظ هذا README على ملاحظات المسارات القديمة حيث أدّى تطور المستودع إلى اختلافات في الأسماء/البنية.
- 🔒 عند عدم اليقين في المراجع القديمة، يتم الإبقاء على النص عمدًا بدل حذفه.
