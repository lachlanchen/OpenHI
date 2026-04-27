[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# Самокалиброванная нейроморфная гиперспектральная визуализация (OpenHI)

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
> Статус i18n в этой проверке: `ar`, `es`, `fr`, `ja`, `ko` присутствуют под `i18n/`. Дополнительные языковые ссылки сохраняются для совместимости с запланированным переводом.

Комплексный конвейер для восстановления спектров с камер событий с рассеянным световым освещением (например, дифракционной решеткой). Система записывает события изменения интенсивности $e = (x, y, t, p)$, где $p \in \{-1, +1\}$ указывает полярность изменения журнала регистрации интенсивности, и автоматически определяет время сканирования и метаданные калибровки («автоинформация») непосредственно из потока событий.

<p align="center">
  <img src="../images/device_setup.png" alt="Device setup" width="24%">
  <img src="../images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*Слева: модульный просвечивающий микроскоп с моторизованным решетчатым осветительным кронштейном и вертикальной детекторной стойкой. Справа: графический интерфейс сбора данных, используемый для мониторинга сегментации, компенсации и реконструкции в реальном времени.*


## Краткий обзор

| Товар | Подробности |
|---|---|
| Основная идея | Самокалиброванное гиперспектральное производное изображение на основе потоков событий |
| Основные этапы | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> скрипты визуализации |
| Документация по оборудованию в репозитории | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Настольные инструменты | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Каноническая бумага | [Препринт Optica Open (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n в этой кассе | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md` |



> [!TIP]
> Приобретите основной комплект разработки (за исключением камеры, тубусной линзы и оптического стола) для статьи [Самокалиброванная нейроморфная гиперспектральная визуализация](https://doi.org/10.1364/opticaopen.30739151), предварительно опубликованной на Optica Open:
> - https://lazying.art/openhi-kit.html
> - Промокод на скидку 30%: `OPTICA`.

## Содержание

- [Вкратце 📌](#Вкратце)
- [Обзор 🔭](#обзор)
- [Функции ✨](#features)
- [Карта репозитория 🗺️](#repository-map)
- [Структура проекта 📁](#project-structure)
- [Быстрый старт (5-минутный путь) ⚡](#quick-start-5-min-path)
- [Предпосылки 🧰](#предпосылки)
- [Установка ⚙️](#установка)
- [Использование 🚀](#использование)
- [Интернационализация 🌍](#интернационализация)
- [Конфигурация 🎛️](#конфигурация)
- [Примеры 🧪](#examples)
- [Спецификация (основной модуль) 🧾](#спецификация-основной-модуль)
- [Основные сценарии 🧠](#core-scripts)
- [Дополнительные инструменты 🛠️](#additional-tools)
- [Турбо-компенсация мультисканирования ⚡](#турбо-мульти-сканирование-компенсация)
- [Управление параметрами 💾](#parameter-management)
- [Оптимизация памяти 🧱](#memory-optimization)
- [Структура вывода 📦](#output-structure)
- [Примеры конфигурации 🧩](#configuration-examples)
- [Картирование длин волн 🌈](#wavelength-mapping)
- [Советы и рекомендации ✅](#советы-и-лучшие практики)
- [Заметки разработчиков 🧭](#development-notes)
- [Устранение неполадок 🩺](#устранение неполадок)
- [Дорожная карта 🛣️](#roadmap)
- [Цитата 📎](#цитация)
- [Благодарности 🙏](#признательности)
- [Лицензия 📄](#лицензия)
- [Содействие 🤝](#содействие)
- [Поддержка/Спонсор 💖](#support--спонсор)

## Обзор

Когда освещение меняет длину волны с течением времени, поток событий кодирует временную производную основного спектра вдоль оси дисперсии.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

Этот конвейер обеспечивает три основных этапа:

| Этап | Цель | Основной сценарий(ы) |
|---|---|---|
| 1. Сегмент | Находите время сканирования и разделяйте записи на проходы вперед и назад | `segment_robust_fixed.py` |
| 2. Компенсация | Оценка кусочно-линейного искажения времени для устранения временного наклона, вызванного сканированием | `compensate_multiwindow_train_saved_params.py` |
| 3. Визуализируйте | Наложение изученных границ и сравнение исходных и компенсированных кадров с временной привязкой | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

Репозиторий также включает в себя аппаратные ресурсы, код графического интерфейса пользователя и ветки архивных экспериментов под `versions/`.

## Функции

- Сквозной процесс обработки событий RAW-to-spectrum.
- Автоматическое/ручное определение периода сканирования и сегментация вперед/назад.
- Многооконная компенсация с режимами обучаемых/фиксированных параметров.
- Сохранение/загрузка параметров в `NPZ`, `JSON` и `CSV`.
- Рабочий процесс слияния нескольких сканирований для более быстрых итераций обучения (`compensate_multiwindow_turbo.py`).
- Пакет визуализации границ, группированных кадров, кумулятивных кривых и взвешенной диагностики.
- Документация по оборудованию: спецификация, печатная плата, 3D-детали, примечания к прошивке.
- Утилиты сбора данных для синхронизации настроек камеры по событиям/кадрам.

| Категория | Включенные возможности |
|---|---|
| Обработка сигналов | Сегментация, определение периода, компенсация искажения времени |
| Оптимизация | Обучаемые/фиксированные параметры, контроль плавности, обучение по частям |
| Выходы | Визуальные наложения, совокупные сравнения, диагностика с использованием карт длин волн |
| Активы платформы | Файлы дизайна аппаратного обеспечения, примечания к прошивке, инструменты графического интерфейса, исторические архивы |

## Карта репозитория

Ключевые аппаратные ресурсы хранятся рядом с кодом для быстрого доступа:

| Площадь | Путь |
|---|---|
| 3D-печатные детали | [`3D/`](3D/) |
| Разводка печатных плат | [`PCB/`](PCB/) |
| Прошивка микроконтроллера | [`firmware/`](firmware/) |
| Интерфейс сбора данных (рабочий стол) | [`ImagingGUI/`](ImagingGUI/) |
| Ссылки на эксперименты/данные | [`reference_spectrum_2835/`](reference_spectrum_2835/), [`reference_spectrum_lumileds/`](reference_spectrum_lumileds/), [`references/`](references/) |
| Анализ выравнивания | [`align_background_vs_reference_code/`](align_background_vs_reference_code/), [`align_data_vs_filter_code/`](align_data_vs_filter_code/) |

## Структура проекта

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

## Быстрый старт (5-минутный путь)

Если ваша среда уже подготовлена ​​и папка набора данных содержит файл `*event*.raw`:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

Чтобы принудительно использовать определенный файл RAW:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

Эта оболочка выполняет сегментацию, обучение компенсации и визуализацию с использованием путей сценариев по умолчанию и флагов CLI.

> [!TIP]
> Для первой проверки запустите оболочку в одном каталоге набора данных, затем проверьте сгенерированный сегмент NPZ и выходные данные визуализации перед настройкой переменных `PIPELINE_*`.

## Предварительные условия

- Python 3.9+ (Python 3.10+ для некоторых инструментов графического интерфейса под `ImagingGUI/`).
— Базовые пакеты Python: `numpy`, `torch`, `matplotlib`.
- Необязательные, но общие: `opencv-python`, `pillow`, `cellpose`.
— Привязки Metavision SDK/Python для рабочих процессов чтения событий RAW (`simple_raw_reader.py`, сегментация из RAW).
- Для более быстрой оптимизации рекомендуется использовать PyTorch с поддержкой CUDA.
- Записи RAW и/или сегментированные файлы NPZ доступны локально.

## Установка

В настоящее время в корне репозитория нет заблокированного файла среды. Предлагаемая установка:

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

Если вы используете перехватчики Git для гигиены больших файлов:

```bash
bash scripts/setup_hooks.sh
```

## Использование

### Базовый рабочий процесс (текущие корневые сценарии)

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

### Удобная оболочка, управляемая одной командой

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

Ручки окружения, поддерживаемые `scripts/run_scan_pipeline.sh`:

| Переменная | По умолчанию | Цель |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Доля окна активных событий |
| `PIPELINE_BIN_WIDTH` | `50000` | Ширина обучающего интервала в микросекундах |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Ширина датчика для визуализации |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Высота датчика для визуализации |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Доля выборки событий для построения графиков |
| `PIPELINE_TIME_BIN_US` | `1000` | Размер ячейки активности сегментации |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Шаблон сегментированного файла для последующих сценариев |

## Интернационализация

В репозитории используется одна строка языковых параметров вверху каждого файла README, чтобы избежать дублирования языковых панелей.

На данный момент доступны переведенные файлы в `i18n/`:

- ЗЗЗМАСК0ЗЗЗ
- ЗЗЗМАСК0ЗЗЗ
- ЗЗЗМАСК0ЗЗЗ
- ЗЗЗМАСК0ЗЗЗ
- ЗЗЗМАСК0ЗЗЗ

| Языковая ссылка в навигации | Файл в формате `i18n/` | Статус |
|---|---|---|
| عربية | `README.ar.md` | ✅ Настоящее время |
| испанский | `README.es.md` | ✅ Настоящее время |
| Французский | `README.fr.md` | ✅ Настоящее время |

Запланированные языковые ссылки намеренно сохранены в верхней части навигации для обеспечения совместимости.

## Конфигурация

Важные элементы управления CLI, используемые в сценариях:

### Сегментация (`segment_robust_fixed.py`)

- `--time_bin_us`: размер интервала активности в микросекундах.
- `--round_trip_period`: период вручную (ячейки по умолчанию `1688`).
- `--auto_calculate_period`: период через автокорреляцию.
- `--activity_fraction`: доля окна активных событий.
- `--manual_start_shift_ms`: смещение начала ручного сканирования.

### Компенсация (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (по умолчанию `13`), `--temperature` (по умолчанию `5000`).
- `--a_trainable`/`--a_fixed`, `--b_trainable`/`--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` для управления памятью.
- `--load_params` для повторного использования изученных параметров.

### Визуализация

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, аргументы размера датчика.
- `visualize_cumulative_compare.py`: размер датчика, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: шкалы полярности, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

## Примеры

### Команды быстрого запуска в стиле набора данных (из `QUICKSTART.md`)

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

### Устаревшие вспомогательные команды, сохраненные из прошлых рабочих процессов

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

Эти устаревшие команды намеренно сохраняются для контекста совместимости; в этой проверке по возможности используйте текущие корневые сценарии.

### Турбо-тренировка с несколькими сканированиями

```bash
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/your_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params
```

### Повторное использование изученных параметров (пропуск повторного обучения)

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

## Спецификация (основной модуль)

Полную таблицу со ссылками и примечаниями см. в [`BOM/core_module.md`](BOM/core_module.md).

### Таблица S2. Сравнение времени и стоимости приобретения предлагаемой событийно-ориентированной системы и эталонной гиперспектральной камеры

| Параметр | Наш | Справочная камера |
|---|---|---|
| Время приобретения | ∼585 мс на сканирование | 300 с на сканирование |
| Объем данных | 18,5 МБ | 138 МБ |
| Прибл. цена | ∼3000 долларов США | 14 000 долларов США |

### Таблица S3. Спецификация модуля сканирующего освещения активной зоны
(За исключением камеры событий и дополнительной оптики для проверки 4f)

| Компонент | Заметки | Стоимость (долл. США) | Таобао Ссылка |
|---|---|---:|---|
| Управление движением | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| Оптика (решетка) | Дифракционная решетка (учебный уровень) | 3,47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPROuNw |
| Освещение | 2835 LED (6 юаней / 10 шт.; 0,6 юаней б/у) | 0,08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| Отражатель | Складное зеркало | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| Электроника | Светодиодная плата (CNY/плата; минимальный заказ 5 шт.) | 1,67 |  |
| Концевые выключатели | Дополнительно, 2 × 8,07 юаней | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| 3D-печать | Одна треть катушки с PLA-нитью (покрывает все печатные детали) | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| Объектив | Плоско-выпуклая линза (25,4 мм, 350–700 нм AR) |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| Всего | основной модуль | **33,99** |  |

## Основные сценарии

### 1. Сегментация: `segment_robust_fixed.py`

**Цель**: извлечь время сканирования из необработанных событий и разделить его на 6 односторонних сканирований (F, B, F, B, F, B).

**Математическое описание**:

- **Сигнал активности** (события, объединенные с помощью $\Delta t = 1000~\mu\text{s}$):
$$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Обнаружение активного окна**: найдите наименьшее непрерывное окно, содержащее $80\%$ событий.

- **Оценка периода**: автокорреляция или период вручную (по умолчанию: интервалы $1688$).

- **Обратная корреляция** (временная структура):
$$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
с
$$a_{\text{rev}}[n] = a[N-1-n].$$

**Использование**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Аргументы**:

- `--segment_events`: сохранять отдельные сегменты сканирования в виде файлов NPZ.
- `--round_trip_period 1688`: использовать период вручную (по умолчанию).
- `--auto_calculate_period`: переопределить период вручную с помощью автокорреляции.
- `--activity_fraction 0.80`: доля событий для активного региона.
- `--max_iterations 2`: итерации уточнения.

### 2. Компенсация: `compensate_multiwindow_train_saved_params.py`

**Цель**: изучить параметры деформации времени, чтобы устранить временной сдвиг, вызванный сканированием, с помощью многооконной кусочно-линейной компенсации.

**Математическое описание**:

- **Граничные поверхности**:
$$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Членство в программе Soft Window**:
$$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Интерполированные наклоны (опционально)**:
$$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Искажение времени**:
$$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Потеря**: минимизация дисперсии кадров с привязкой по времени с регуляризацией плавности по параметрам.

**Использование**:

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**Ключевые аргументы**:

- `--a_trainable` / `--a_fixed`: управление обучением параметра a (по умолчанию: фиксированное).
- `--b_trainable` / `--b_fixed`: управление обучением b-параметров (по умолчанию: обучаемое).
- `--num_params 13`: количество граничных параметров.
- `--temperature 5000`: Сигмовидная температура для мягких окон.
- `--smoothness_weight 0.001`: вес регуляризации.
- `--load_params file.npz`: загрузить сохраненные параметры.
- `--chunk_size 250000`: размер блока обработки с эффективным использованием памяти.

### 3. Визуализация: `visualize_boundaries_and_frames.py`

**Цель**: отобразить изученные параметры и продемонстрировать качественные улучшения.

**Функции**:

- Наложение параметров на проекции $x\text{–}t$ и $y\text{–}t$.
- Сравнение кадров с привязкой по времени (исходный и компенсированный).
- Анализ скользящего окна (интервалы 50 мс и 2 мс).
- Картирование длин волн для спектральной визуализации.

**Использование**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Накопительное сравнение: `visualize_cumulative_compare.py`

**Цель**: сравнить совокупные средние значения с шагом 2 мс со средними значениями скользящей корзины.

**Математическое описание**:

- **Совокупное значение**:
$$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Скользящий означает**: количество событий равно $[T-\Delta,\,T)$, деленное на $H \times W$.

- **Зависимость** (производная конечной разности):
$$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Использование**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Дополнительные инструменты

### Приложение с графическим интерфейсом: `scan_compensation_gui_cloud.py`

Полный графический интерфейс для компенсации сканирования с трехмерной спектральной визуализацией.

**Функции**:

- Интерактивная настройка параметров.
- Прогресс оптимизации в реальном времени.
- 3D-визуализация с отображением длин волн.
- Экспорт результатов и параметров.

**Использование**:

```bash
python scan_compensation_gui_cloud.py
```

### Система двойной камеры (текущий путь)

Система синхронной записи событийных и кадровых камер:

- ЗЗЗМАСК0ЗЗЗ

**Функции**:

- Одновременная запись событий и кадров.
- Предварительный просмотр в реальном времени с преобразованиями.
- Всегда наверху элементы управления окнами.
- Регулировка параметров во время записи.

### Управление двигателем Arduino (сохранена устаревшая ссылка на путь)

В исходном README указан путь к эскизу прошивки:

- ЗЗЗМАСК0ЗЗЗ

Текущий макет репозитория включает примечания к прошивке по адресу:

- ЗЗЗМАСК0ЗЗЗ

Это несоответствие путей сохранено здесь намеренно; Если у вас есть папки с эскизами роторов в другом филиале/локальной кассе, продолжайте использовать эти пути.

Устаревшие документированные возможности этого эскиза включают в себя:

- Точный контроль угла с микрошагом.
- Профили ускорения/замедления.
- Интеграция концевого выключателя.
- Функция автоцентрирования.

## Компенсация турбо-мультисканирования

Если у вас есть несколько односторонних сканирований (вперед/назад) одной и той же развертки, вы можете объединить их и запустить проверенный тренажер в одном комбинированном потоке событий, используя `compensate_multiwindow_turbo.py`.

### Что он делает

- Принимает один сегмент, явный список или весь каталог сегментов.
- Для обратного сканирования меняет полярность и меняет время перед слиянием:
- Если полярность `p ∈ {0,1}`: `p := 1 − p`; затем поверните время в пределах сканирования.
- Если полярность `p ∈ {−1,1}`: `p := −p`; затем поверните время в пределах сканирования.
- Объединяет сканы на непрерывной временной шкале (с интервалом между сканами `1 μs`) и скрытно вызывает `compensate_multiwindow_train_saved_params.py`.

### Использование

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

### Параметры

- `--segment`, `--segments`, `--segments-dir`: выберите набор входных данных.
- `--include {all|forward|backward}`: фильтрация по направлению сканирования.
- `--sort {name|time}`: естественный порядок имен файлов или порядок NPZ `start_time`.
- `--bin-width <μs>`: перенаправлено базовому тренеру.
- `--load-params`: повторное использование сохраненных параметров (пропуск обучения и быстрое восстановление выходных данных при новой ширине интервала).
- `--extra ...` после `--`: любые дополнительные флаги передаются базовому тренеру.

### Совет по масштабированию скорости

Если ваше сканирование на `N×` быстрее базового, уменьшите `--bin-width` на тот же коэффициент (например, базовый `50 ms` -> `10×` быстрее -> `5 ms`: `--bin-width 5000`). Вы можете пройти обучение один раз (например, `5 ms`), а затем использовать `--load-params` для быстрого восстановления результатов в `10 ms` без повторного обучения.

## Управление параметрами

Система поддерживает комплексные функции сохранения/загрузки параметров.

### Форматы сохранения

- **NPZ**: двоичный формат для быстрой загрузки.
- **JSON**: удобочитаемый формат с метаданными.
- **CSV**: совместимость с Excel для проверки вручную.

### Загрузка параметров

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Файлы параметров

Файлам автоматически присваиваются имена с указанием количества параметров, например: `*_learned_params_n13.*`.

## Оптимизация памяти

Система использует фрагментированную обработку:

| Товар | Деталь |
|---|---|
| Размер куска | События `250000` по умолчанию (настраиваемые) |
| Эффективная память | Обрабатывает большие наборы данных без переполнения графического процессора |
| Единая дисперсия | Поддерживает правильный градиентный поток для обучения |
| Отслеживание прогресса | Обновления обработки в реальном времени |

## Структура вывода

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

## Примеры конфигурации

### Высокоточная компенсация

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### Быстрая обработка

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### Память ограничена

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## Сопоставление длин волн

Система поддерживает спектральную визуализацию путем сопоставления временной эволюции с длиной волны:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Диапазон по умолчанию**: $380\text{–}680~\text{nm}$ (настраиваемый).

## Советы и лучшие практики

### Выбор параметра

- **Микрошаг**: используйте `32×` для плавного движения (Arduino).
- **Ширина ячейки**: начните с `50 ms` для оптимизации и `2 ms` для анализа.
- **Температура**: более высокие значения (около `5000`) для более плавных границ.
- **Гладкость**: `0.001` обеспечивает хорошую регуляризацию.

### Управление памятью

- **Память графического процессора**: используйте фрагментированную обработку с соответствующим размером фрагмента.
- **Количество событий**: для стабильного обучения рекомендуется использовать события `> 10^6`.
- **Итерации**: обычно достаточно итераций `1000`.

### Организация файлов

- Храните файлы и сегменты RAW в одном каталоге.
- Файлы параметров автоматически определяются по соглашению об именах.
- Используйте описательные префиксы имен файлов для организованного вывода.

## Примечания по разработке

- `versions.md` описывает исторические эпохи проекта и обоснование миграции.
- `.githooks/pre-commit` блокирует негабаритные/двоичные коммиты и типы файлов, не являющиеся кодом/документами.
- `scripts/setup_hooks.sh` устанавливает для `core.hooksPath` значение `.githooks`.
- `archive_code_variants/` хранит старые варианты скриптов, чтобы сосредоточить внимание на инструментах корневого уровня.

Известные отклонения в документации (сохранены намеренно для целей обратной совместимости):

- В некоторых старых документах упоминаются `sync_image_system/` или `dual_camera_gui.py`; текущая проверка содержит каталоги `ImagingGUI/DualCamera_separate_transform.py` и SDK.
- `ImagingGUI/README.md` по-прежнему ссылается на `pip install -r requirements.txt`, но в этой проверке отсутствует корень `requirements.txt`.
- `firmware/README.md` ссылается на несколько подпапок эскизов Arduino, которых нет в этой проверке.
- `versions.md` упоминает устаревшие имена сценариев, которые отличаются от текущих имен сценариев корневого уровня.
- `i18n/` существует и в настоящее время включает `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md` и `README.ko.md`; ссылки на дополнительные языки сохраняются в качестве запланированных целей.

## Поиск неисправностей

| Симптом | Вероятная причина | Действие |
|---|---|---|
| Ошибки загрузки параметров | Несоответствие количества параметров | Убедитесь, что `--num_params` соответствует сохраненному файлу |
| ООМ / давление памяти | Кусок слишком большой или контейнеры слишком мелкие | Уменьшите `--chunk_size` и/или увеличьте `--bin_width` |
| Слабое качество компенсации | Недостаточно обученная или плохая сегментация | Увеличьте `--iterations`, включите обучаемые параметры, проверьте сегментацию |
| Файлы сегментов не создаются | Проблема с RAW/SDK/флагом | Подтвердите путь к RAW, настройку Metavision и `--segment_events` |
| Аргументы турбо-обертки игнорируются | Неправильный синтаксис пересылки | Передайте аргументы тренера после `--` (или используйте `--extra`) |
| Проблемы с графическим интерфейсом | Несоответствие Tkinter/бэкэнда или SDK | Проверка доступности серверной части графического пользовательского интерфейса и SDK камеры |

- **Ошибки загрузки параметров**: убедитесь, что `--num_params` совместим с загруженным файлом параметров.
- **OOM / нехватка памяти**: уменьшите `--chunk_size` и/или увеличьте `--bin_width`.
- **Слабое качество компенсации**: увеличьте `--iterations`, включите обучаемые параметры (`--a_trainable`, `--b_trainable`, дополнительно `--boundary_trainable`) и проверьте качество сегментации.
- **Файлы сегментов не создаются**: подтвердите путь к RAW, доступность программы чтения Metavision и передачу `--segment_events`.
- **Передача аргументов Turbo-обертки**: поместите аргументы тренера после `--` (или используйте `--extra`).
- **Проблемы с графическим интерфейсом**: проверьте поддержку серверной части Tkinter и наличие SDK камеры на вашей платформе.

## Дорожная карта

— Улучшение воспроизводимости зависимостей/начальной загрузки (`requirements.txt` или файл блокировки среды).
- Объедините имена устаревших сценариев и ссылки на пути в документах.
- Расширить документированные схемы наборов данных и ожидаемые соглашения о полях NPZ.
- Добавьте тесты в стиле регрессии для сегментации/компенсации небольших данных о приборах.
- Продолжить интеграцию результатов анализа качества публикации из конвейеров `align_*`.
- Добавьте/обновите оставшиеся многоязычные файлы README под `i18n/`, чтобы они полностью соответствовали ссылкам языковой навигации вверху.

## Цитирование

Если этот репозиторий будет полезен для ваших исследований, пожалуйста, цитируйте препринт Optica Open:

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

## Благодарности

- Препринт Optica Open и сопутствующие материалы для распространения проекта.
- Участники разработки аппаратного и программного обеспечения в ходе эволюции репозитория зафиксированы в `versions/` и заархивированы инструментами.
- Поддержка сообщества через спонсоров GitHub и связанные каналы проекта.

## Лицензия

Этот проект выпущен под лицензией MIT. Подробности см. в [`LICENSE`](LICENSE).

## Вклад

Взносы приветствуются.

- Начните с существующих сценариев и стиля документации.
- По возможности сохраняйте воспроизводимость примеров командной строки с путями к репозиторию.
- Если вы добавляете большие наборы данных/выходные данные, убедитесь, что соблюдаются политики `.githooks/pre-commit`.

Примечание. В этой проверке отсутствует выделенный `CONTRIBUTING.md`. При необходимости откройте проблему или отправьте PR с предлагаемым вами рабочим процессом внесения вклада.

## Поддержка/Спонсор

| Канал | Ссылка | Использование |
|---|---|---|
| Спонсоры GitHub | https://github.com/sponsors/lachlanchen | Постоянная поддержка проекта |
| Сайт проекта | https://lazying.art | Обновления проекта и ссылки на экосистему |
| Сообщество чата | https://chat.lazying.art | Обсуждение сообщества |
| Дополнительная страница автора | https://onlyideas.art | Связанный авторский/исследовательский контент |
| Страница покупки основного комплекта | https://lazying.art/openhi-kit.html | Стартовый комплект аппаратного обеспечения для рабочего процесса OpenHI |
| Промокод | `OPTICA` | Скидка 30% (как описано выше) |

---

### Примечания

- 📌 В этом README хранятся примечания к устаревшим путям, в которых эволюция репозитория приводила к смещению имен и макетов.
- 🔒 Если вы не уверены в старых ссылках, текст намеренно сохраняется, а не удаляется.
