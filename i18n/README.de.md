[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# Selbstkalibrierte neuromorphe hyperspektrale Bildgebung (OpenHI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#voraussetzungen)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#ueberblick)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#repository-karte)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#zusaetzliche-tools)
[![Paper](https://img.shields.io/badge/Preprint-Optica%20Open-ff6b6b.svg)](https://doi.org/10.1364/opticaopen.30739151)
[![i18n](https://img.shields.io/badge/i18n-5%20ready%20%7C%206%20planned-22c55e.svg)](#internationalisierung)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#ueberblick)


> [!NOTE]
> i18n-Status in diesem Checkout: `ar`, `es`, `fr`, `ja`, `ko` sind unter `i18n/` vorhanden. Zusätzliche Sprachlinks bleiben aus Kompatibilitätsgründen für die geplante Übersetzungsabdeckung erhalten.

Eine umfassende Pipeline zur Rekonstruktion von Spektren aus Event-Kameras bei dispersiver Beleuchtung (z. B. Beugungsgitter). Das System zeichnet Intensitätsänderungs-Events $e = (x, y, t, p)$ auf, wobei $p \in \{-1, +1\}$ die Polarität der Log-Intensitätsänderung kennzeichnet, und leitet Scan-Timing sowie Kalibriermetadaten ("Auto-Info") direkt aus dem Event-Stream ab.

## Auf einen Blick

| Element | Details |
|---|---|
| Kernidee | Selbstkalibrierte hyperspektrale Ableitungsbildgebung aus Event-Streams |
| Hauptstufen | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> Visualisierungsskripte |
| Hardware-Doku im Repo | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Desktop-Tools | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Referenz-Paper | [Optica Open Preprint (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n in diesem Checkout | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md` |

<p align="center">
  <img src="images/device_setup.png" alt="Device setup" width="24%">
  <img src="images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*Links: modulares Transmissionsmikroskop mit motorisiertem Gitter-Beleuchtungsarm und vertikalem Detektionsstapel. Rechts: Datenaufnahme-GUI zur Echtzeitüberwachung von Segmentierung, Kompensation und Rekonstruktion.*

> [!TIP]
> Kaufen Sie das zentrale Development-Kit (ohne Kamera, Tubuslinse und optischen Tisch) für das Paper [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151), das auf Optica Open als Preprint veröffentlicht wurde:
> - https://lazying.art/openhi-kit.html
> - Gutscheincode mit 30% Rabatt: `OPTICA`

## Inhalt

- [Auf einen Blick 📌](#auf-einen-blick)
- [Überblick 🔭](#ueberblick)
- [Funktionen ✨](#funktionen)
- [Repository-Karte 🗺️](#repository-karte)
- [Projektstruktur 📁](#projektstruktur)
- [Schnellstart (5-Minuten-Pfad) ⚡](#schnellstart-5-minuten-pfad)
- [Voraussetzungen 🧰](#voraussetzungen)
- [Installation ⚙️](#installation)
- [Nutzung 🚀](#nutzung)
- [Internationalisierung 🌍](#internationalisierung)
- [Konfiguration 🎛️](#konfiguration)
- [Beispiele 🧪](#beispiele)
- [Stueckliste (Kernmodul) 🧾](#stueckliste-kernmodul)
- [Kernskripte 🧠](#kernskripte)
- [Zusaetzliche Tools 🛠️](#zusaetzliche-tools)
- [Turbo-Multi-Scan-Kompensation ⚡](#turbo-multi-scan-kompensation)
- [Parameterverwaltung 💾](#parameterverwaltung)
- [Speicheroptimierung 🧱](#speicheroptimierung)
- [Ausgabestruktur 📦](#ausgabestruktur)
- [Konfigurationsbeispiele 🧩](#konfigurationsbeispiele)
- [Wellenlaengenabbildung 🌈](#wellenlaengenabbildung)
- [Tipps und Best Practices ✅](#tipps-und-best-practices)
- [Entwicklungsnotizen 🧭](#entwicklungsnotizen)
- [Fehlerbehebung 🩺](#fehlerbehebung)
- [Roadmap 🛣️](#roadmap)
- [Zitat 📎](#zitat)
- [Danksagung 🙏](#danksagung)
- [Lizenz 📄](#lizenz)
- [Beitraegen 🤝](#beitraegen)
- [Support / Sponsoring 💖](#support--sponsoring)

## Ueberblick

Wenn die Beleuchtung zeitlich durch Wellenlängen sweeped, kodiert der Event-Stream entlang der Dispersionsachse eine zeitliche Ableitung des zugrunde liegenden Spektrums.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

Diese Pipeline bietet drei Hauptstufen:

| Stufe | Zweck | Primäre Skripte |
|---|---|---|
| 1. Segmentieren | Scan-Timing finden und Aufzeichnungen in Vorwärts-/Rückwärtsdurchläufe aufteilen | `segment_robust_fixed.py` |
| 2. Kompensieren | Stückweise linearen Time-Warp schätzen, um scan-induzierte zeitliche Scherung zu entfernen | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualisieren | Gelernte Grenzen überlagern und Original- gegen kompensierte zeitgebinnte Frames vergleichen | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

Das Repository enthält außerdem Hardware-Assets, Datenaufnahme-GUI-Code und archivierte Experimentzweige unter `versions/`.

## Funktionen

- End-to-End-Workflow für Event-Verarbeitung von RAW bis Spektrum.
- Automatische/manuelle Erkennung der Scan-Periode und Vorwärts-/Rückwärtssegmentierung.
- Multi-Window-Kompensation mit trainierbaren/fixen Parametermodi.
- Parameter speichern/laden in `NPZ`, `JSON` und `CSV`.
- Multi-Scan-Merge-Workflow für schnellere Trainingsiterationen (`compensate_multiwindow_turbo.py`).
- Visualisierungssuite für Grenzen, gebinnte Frames, kumulative Kurven und gewichtete Diagnostik.
- Hardwaredokumentation: BOM, PCB, 3D-Teile, Firmware-Hinweise.
- Aufnahme-Utilities für synchronisierte Event-/Frame-Kamera-Setups.

| Kategorie | Enthaltene Fähigkeiten |
|---|---|
| Signalverarbeitung | Segmentierung, Periodenerkennung, Time-Warp-Kompensation |
| Optimierung | Trainierbare/fixe Parameter, Glättungssteuerung, chunk-basiertes Training |
| Ausgaben | Visuelle Overlays, kumulative Vergleiche, wellenlängen-kartierte Diagnostik |
| Plattform-Assets | Hardware-Designdateien, Firmware-Hinweise, GUI-Tooling, historische Archive |

## Repository-Karte

Wichtige Hardware-Assets liegen zur schnellen Nutzung direkt neben dem Code:

| Bereich | Pfad |
|---|---|
| 3D-gedruckte Teile | [`3D/`](3D/) |
| PCB-Layouts | [`PCB/`](PCB/) |
| Mikrocontroller-Firmware | [`firmware/`](firmware/) |
| Aufnahme-UI (Desktop) | [`ImagingGUI/`](ImagingGUI/) |
| Experiment-/Datenreferenzen | [`reference_spectrum_2835/`](reference_spectrum_2835/), [`reference_spectrum_lumileds/`](reference_spectrum_lumileds/), [`references/`](references/) |
| Alignment-Analyse | [`align_background_vs_reference_code/`](align_background_vs_reference_code/), [`align_data_vs_filter_code/`](align_data_vs_filter_code/) |

## Projektstruktur

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

## Schnellstart (5-Minuten-Pfad)

Wenn Ihre Umgebung bereits vorbereitet ist und Ihr Datensatzordner eine Datei `*event*.raw` enthält:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

Um eine bestimmte RAW-Datei zu erzwingen:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

Dieser Wrapper führt Segmentierung, Kompensationstraining und Visualisierung mit den Standard-Skriptpfaden und CLI-Flags des Repositories aus.

> [!TIP]
> Für eine erste Validierung den Wrapper auf einen Datensatzordner ausführen und anschließend die erzeugte Segment-NPZ sowie die Visualisierungsausgaben prüfen, bevor `PIPELINE_*`-Variablen getunt werden.

## Voraussetzungen

- Python 3.9+ (Python 3.10+ für einige GUI-Tools unter `ImagingGUI/`).
- Kern-Python-Pakete: `numpy`, `torch`, `matplotlib`.
- Optional, aber üblich: `opencv-python`, `pillow`, `cellpose`.
- Metavision SDK / Python-Bindings für RAW-Event-Workflows (`simple_raw_reader.py`, Segmentierung aus RAW).
- CUDA-fähiges PyTorch wird für schnellere Optimierung empfohlen.
- RAW-Aufzeichnungen und/oder segmentierte NPZ-Dateien lokal verfügbar.

## Installation

Aktuell gibt es im Repository-Root keine gesperrte Environment-Datei. Empfohlenes Setup:

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

Wenn Sie Git-Hooks für Large-File-Hygiene nutzen:

```bash
bash scripts/setup_hooks.sh
```

## Nutzung

### Basis-Workflow (aktuelle Root-Skripte)

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

Von `scripts/run_scan_pipeline.sh` unterstützte Umgebungsvariablen:

| Variable | Standard | Zweck |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Anteil des aktiven Event-Fensters |
| `PIPELINE_BIN_WIDTH` | `50000` | Trainings-Bin-Breite in Mikrosekunden |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Sensorbreite für Visualisierung |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Sensorhöhe für Visualisierung |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Event-Sampling-Anteil für Plots |
| `PIPELINE_TIME_BIN_US` | `1000` | Aktivitäts-Bin-Größe bei Segmentierung |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Segmentdatei-Muster für nachgelagerte Skripte |

## Internationalisierung

Das Repository verwendet oben in jeder README eine einzelne Sprachoptions-Zeile, um doppelte Sprachleisten zu vermeiden.

Aktuell verfügbare Übersetzungsdateien in `i18n/`:

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`

| Sprachlink in Navigation | Datei in `i18n/` | Status |
|---|---|---|

Geplante Sprachlinks werden in der oberen Navigation absichtlich aus Gründen der Vorwärtskompatibilität beibehalten.

## Konfiguration

Wichtige CLI-Steuerungen, die skriptübergreifend verwendet werden:

### Segmentierung (`segment_robust_fixed.py`)

- `--time_bin_us`: Aktivitäts-Bin-Größe in Mikrosekunden.
- `--round_trip_period`: manuelle Periode (Standard `1688` Bins).
- `--auto_calculate_period`: Periode per Autokorrelation.
- `--activity_fraction`: Anteil des aktiven Event-Fensters.
- `--manual_start_shift_ms`: manueller Scan-Startoffset.

### Kompensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (Standard `13`), `--temperature` (Standard `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` für Speichersteuerung.
- `--load_params` zur Wiederverwendung gelernter Parameter.

### Visualisierung

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, Sensorgrößen-Args.
- `visualize_cumulative_compare.py`: Sensorgröße, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: Polaritätsskalen, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

## Beispiele

### Schnellstart-Datensatzbefehle (aus `QUICKSTART.md`)

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

### Historische Hilfsbefehle aus älteren Workflows (beibehalten)

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

Diese Legacy-Befehle bleiben absichtlich als Kompatibilitätskontext erhalten; in diesem Checkout sollten nach Möglichkeit die aktuellen Root-Skripte verwendet werden.

### Turbo-Multi-Scan-Training

```bash
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/your_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params
```

### Gelernte Parameter wiederverwenden (Retraining überspringen)

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

## Stueckliste (Kernmodul)

Siehe [`BOM/core_module.md`](BOM/core_module.md) für die vollständige Tabelle mit Links und Hinweisen.

### Tabelle S2. Vergleich von Aufnahmezeit und Kosten zwischen dem vorgeschlagenen event-getriebenen System und einer Referenz-Hyperspektralkamera

| Parameter | Unser System | Referenzkamera |
|---|---|---|
| Aufnahmezeit | ∼585 ms pro Scan | 300 s pro Scan |
| Datenvolumen | 18.5 MB | 138 MB |
| Ungefährer Preis | ∼3000 USD | 14 000 USD |

### Tabelle S3. Stückliste für das Kernmodul der Scan-Beleuchtung
(Ausgenommen Event-Kamera und optionale 4f-Validierungsoptik)

| Komponente | Hinweise | Kosten (USD) | Taobao-Link |
|---|---|---:|---|
| Bewegungssteuerung | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| Optik (Gitter) | Beugungsgitter (Education-Qualität) | 3.47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPRouNw |
| Beleuchtung | 2835 LED (6 CNY / 10 Stk.; 0.6 CNY verwendet) | 0.08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| Reflektor | Klappspiegel | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| Elektronik | LED-PCB (CNY/Platine; Mindestbestellung 5 Stk.) | 1.67 |  |
| Endschalter | Optional, 2 × 8.07 CNY | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| 3D-Druck | Ein Drittel PLA-Filamentspule (deckt alle Druckteile) | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| Linse | Plan-konvexe Linse (25.4 mm, 350–700 nm AR) |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| Gesamt | Kernmodul | **33.99** |  |

## Kernskripte

### 1. Segmentierung: `segment_robust_fixed.py`

**Ziel**: Scan-Timing aus rohen Events extrahieren und in 6 Einweg-Scans schneiden (F, B, F, B, F, B).

**Mathematische Beschreibung**:

- **Aktivitätssignal** (Events gebinnt mit $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Aktivfenster-Erkennung**: kleinstes zusammenhängendes Fenster finden, das $80\%$ der Events enthält.

- **Periodenschätzung**: Autokorrelation oder manuelle Periode (Standard: $1688$ Bins).

- **Reverse-Korrelation** (Timing-Struktur):
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  mit
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**Nutzung**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Argumente**:

- `--segment_events`: Einzelne Scan-Segmente als NPZ-Dateien speichern.
- `--round_trip_period 1688`: Manuelle Periode verwenden (Standard).
- `--auto_calculate_period`: Manuelle Periode per Autokorrelation überschreiben.
- `--activity_fraction 0.80`: Event-Anteil für aktive Region.
- `--max_iterations 2`: Verfeinerungsiterationen.

### 2. Kompensation: `compensate_multiwindow_train_saved_params.py`

**Ziel**: Time-Warp-Parameter lernen, um scan-induzierte zeitliche Scherung mittels Multi-Window-Stückweise-Linear-Kompensation zu entfernen.

**Mathematische Beschreibung**:

- **Grenzflächen**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Weiche Fensterzugehörigkeiten**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Interpolierte Steigungen (optional)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Time Warp**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Loss**: Varianzminimierung zeitgebinnter Frames mit Glättungsregularisierung auf den Parametern.

**Nutzung**:

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**Zentrale Argumente**:

- `--a_trainable` / `--a_fixed`: Steuerung des Trainings der a-Parameter (Standard: fix).
- `--b_trainable` / `--b_fixed`: Steuerung des Trainings der b-Parameter (Standard: trainierbar).
- `--num_params 13`: Anzahl der Boundary-Parameter.
- `--temperature 5000`: Sigmoid-Temperatur für weiche Fenster.
- `--smoothness_weight 0.001`: Regularisierungsgewicht.
- `--load_params file.npz`: Gespeicherte Parameter laden.
- `--chunk_size 250000`: Speichereffiziente Chunk-Größe.

### 3. Visualisierung: `visualize_boundaries_and_frames.py`

**Ziel**: Gelernte Parameter anzeigen und qualitative Verbesserungen sichtbar machen.

**Funktionen**:

- Parameter-Overlays auf $x\text{–}t$- und $y\text{–}t$-Projektionen.
- Vergleich zeitgebinnter Frames (Original vs. kompensiert).
- Sliding-Window-Analyse (50 ms und 2 ms Bins).
- Wellenlängen-Mapping für spektrale Visualisierung.

**Nutzung**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Kumulativer Vergleich: `visualize_cumulative_compare.py`

**Ziel**: Kumulative Mittelwerte mit 2-ms-Schritten gegen Sliding-Bin-Mittelwerte vergleichen.

**Mathematische Beschreibung**:

- **Kumulative Mittelwerte**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Sliding Means**: Event-Zählungen in $[T-\Delta,\,T)$ geteilt durch $H \times W$.

- **Beziehung** (finite-difference-Ableitung):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Nutzung**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Zusaetzliche Tools

### GUI-Anwendung: `scan_compensation_gui_cloud.py`

Vollständige GUI für Scan-Kompensation mit 3D-Spektralvisualisierung.

**Funktionen**:

- Interaktive Parametrierung.
- Echtzeit-Fortschritt der Optimierung.
- 3D-Wellenlängen-kartierte Visualisierung.
- Ergebnisse und Parameter exportieren.

**Nutzung**:

```bash
python scan_compensation_gui_cloud.py
```

### Dual-Kamera-System (aktueller Pfad)

Synchronisiertes Aufnahmesystem für Event- und Frame-Kameras:

- `ImagingGUI/DualCamera_separate_transform.py`

**Funktionen**:

- Gleichzeitige Event- und Frame-Aufnahme.
- Echtzeitvorschau mit Transformationen.
- Always-on-top-Fenstersteuerung.
- Parameteranpassung während der Aufnahme.

### Arduino-Motorsteuerung (Legacy-Pfadreferenz beibehalten)

Die ursprüngliche README verwies auf diesen Firmware-Sketch-Pfad:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

Das aktuelle Repository-Layout enthält Firmware-Hinweise unter:

- `firmware/README.md`

Diese Pfadabweichung wird hier absichtlich beibehalten; wenn Sie Rotor-Sketch-Ordner in einem anderen Branch/lokalen Checkout haben, verwenden Sie weiterhin diese Pfade.

Historisch dokumentierte Fähigkeiten dieses Sketches umfassen:

- Präzise Winkelsteuerung mit Microstepping.
- Beschleunigungs-/Verzögerungsprofile.
- Integration von Endschaltern.
- Auto-Centering-Funktionalität.

## Turbo-Multi-Scan-Kompensation

Wenn Sie mehrere Einweg-Scans (Vorwärts/Rückwärts) desselben Sweeps haben, können Sie sie zusammenführen und den bewährten Trainer auf einem einzelnen kombinierten Event-Stream mit `compensate_multiwindow_turbo.py` ausführen.

### Was es macht

- Akzeptiert ein Segment, eine explizite Liste oder ein komplettes Segmentverzeichnis.
- Für Rückwärts-Scans werden Polarität und Zeit vor dem Merge umgedreht:
- Bei Polarität `p ∈ {0,1}`: `p := 1 − p`; danach Zeit innerhalb des Scans umkehren.
- Bei Polarität `p ∈ {−1,1}`: `p := −p`; danach Zeit innerhalb des Scans umkehren.
- Verkettet Scans auf einer kontinuierlichen Zeitachse (mit `1 μs` Lücke zwischen Scans) und ruft intern `compensate_multiwindow_train_saved_params.py` auf.

### Nutzung

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

### Optionen

- `--segment`, `--segments`, `--segments-dir`: Eingabeset auswählen.
- `--include {all|forward|backward}`: Nach Scan-Richtung filtern.
- `--sort {name|time}`: Natürliche Dateinamen-Reihenfolge oder NPZ-`start_time`-Reihenfolge.
- `--bin-width <μs>`: Wird an den Basistrainer weitergereicht.
- `--load-params`: Gespeicherte Parameter wiederverwenden (Training überspringen und Ausgaben bei neuen Bin-Breiten schnell regenerieren).
- `--extra ...` nach `--`: Zusätzliche Flags werden an den Basistrainer weitergereicht.

### Tipp zur Geschwindigkeitsskalierung

Wenn Ihr Scan `N×` schneller als die Basis ist, reduzieren Sie `--bin-width` um denselben Faktor (z. B. Basis `50 ms` -> `10×` schneller -> `5 ms`: `--bin-width 5000`). Sie können einmal trainieren (z. B. `5 ms`) und anschließend mit `--load-params` Ergebnisse bei `10 ms` ohne erneutes Training schnell regenerieren.

## Parameterverwaltung

Das System unterstützt umfassende Save/Load-Funktionalität für Parameter.

### Speicherformate

- **NPZ**: Binärformat für schnelles Laden.
- **JSON**: Menschenlesbar mit Metadaten.
- **CSV**: Excel-kompatibel zur manuellen Prüfung.

### Parameter laden

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Parameterdateien

Dateien werden automatisch mit Parameteranzahl benannt, z. B.: `*_learned_params_n13.*`.

## Speicheroptimierung

Das System nutzt durchgehend chunk-basierte Verarbeitung:

| Element | Detail |
|---|---|
| Chunk-Größe | Standard `250000` Events (konfigurierbar) |
| Speichereffizient | Verarbeitet große Datensätze ohne GPU-Overflow |
| Unified Variance | Erhält korrekten Gradientenfluss für das Lernen |
| Fortschrittsanzeige | Echtzeit-Updates der Verarbeitung |

## Ausgabestruktur

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

## Konfigurationsbeispiele

### Hochpräzise Kompensation

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### Schnelle Verarbeitung

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### Speicherbegrenzt

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## Wellenlaengenabbildung

Das System unterstützt spektrale Visualisierung durch Abbildung der zeitlichen Entwicklung auf Wellenlänge:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Standardbereich**: $380\text{–}680~\text{nm}$ (konfigurierbar).

## Tipps und Best Practices

### Parameterauswahl

- **Microstepping**: `32×` für ruhige Bewegung verwenden (Arduino).
- **Bin-Breite**: Mit `50 ms` für Optimierung starten, `2 ms` für Analyse.
- **Temperatur**: Höhere Werte (um `5000`) für glattere Grenzen.
- **Smoothness**: `0.001` liefert gute Regularisierung.

### Speichermanagement

- **GPU-Speicher**: Chunk-basierte Verarbeitung mit passender Chunk-Größe verwenden.
- **Event-Anzahl**: `> 10^6` Events empfohlen für stabiles Lernen.
- **Iterationen**: `1000` Iterationen sind üblicherweise ausreichend.

### Dateiorganisation

- RAW-Dateien und Segmente im selben Verzeichnis halten.
- Parameterdateien werden über Namenskonvention automatisch erkannt.
- Beschreibende Dateinamen-Präfixe für geordnete Ausgaben verwenden.

## Entwicklungsnotizen

- `versions.md` beschreibt historische Projektepochen und Gründe der Migration.
- `.githooks/pre-commit` blockiert übergroße/binäre Commits sowie nicht Code-/Dokument-Dateitypen.
- `scripts/setup_hooks.sh` setzt `core.hooksPath` auf `.githooks`.
- `archive_code_variants/` enthält ältere Skriptvarianten, damit Root-Level-Tooling fokussiert bleibt.

Bekannte Dokumentationsabweichungen (absichtlich für Rückwärtskompatibilitätskontext erhalten):

- Einige ältere Dokumente erwähnen `sync_image_system/` oder `dual_camera_gui.py`; im aktuellen Checkout sind `ImagingGUI/DualCamera_separate_transform.py` und SDK-Verzeichnisse enthalten.
- `ImagingGUI/README.md` verweist weiterhin auf `pip install -r requirements.txt`, aber im Root dieses Checkouts ist keine `requirements.txt` vorhanden.
- `firmware/README.md` verweist auf mehrere Arduino-Sketch-Unterordner, die in diesem Checkout nicht vorhanden sind.
- `versions.md` nennt Legacy-Skriptnamen, die von den aktuellen Root-Skriptnamen abweichen.
- `i18n/` existiert und enthält aktuell `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md` und `README.ko.md`; Links für zusätzliche Sprachen bleiben als geplante Ziele erhalten.

## Fehlerbehebung

| Symptom | Wahrscheinliche Ursache | Aktion |
|---|---|---|
| Fehler beim Parameterladen | Anzahl der Parameter passt nicht | Sicherstellen, dass `--num_params` zur gespeicherten Datei passt |
| OOM / Speicherdruck | Chunk zu groß oder Bins zu fein | `--chunk_size` reduzieren und/oder `--bin_width` erhöhen |
| Schwache Kompensationsqualität | Untertrainiert oder schlechte Segmentierung | `--iterations` erhöhen, trainierbare Parameter aktivieren, Segmentierung prüfen |
| Keine Segmentdateien erzeugt | RAW/SDK/Flag-Problem | RAW-Pfad, Metavision-Setup und `--segment_events` prüfen |
| Turbo-Wrapper-Args ignoriert | Falsche Forwarding-Syntax | Trainer-Args nach `--` übergeben (oder `--extra` verwenden) |
| GUI-Probleme | Tkinter-/Backend- oder SDK-Mismatch | GUI-Backend und Kamera-SDK-Verfügbarkeit prüfen |

- **Fehler beim Parameterladen**: Sicherstellen, dass `--num_params` mit der geladenen Parameterdatei kompatibel ist.
- **OOM / Speicherdruck**: `--chunk_size` reduzieren und/oder `--bin_width` erhöhen.
- **Schwache Kompensationsqualität**: `--iterations` erhöhen, trainierbare Parameter (`--a_trainable`, `--b_trainable`, optional `--boundary_trainable`) aktivieren und Segmentierungsqualität prüfen.
- **Keine Segmentdateien erzeugt**: RAW-Pfad, Verfügbarkeit des Metavision-Readers und gesetztes `--segment_events` prüfen.
- **Argumentübergabe im Turbo-Wrapper**: Trainer-Argumente nach `--` setzen (oder `--extra` verwenden).
- **GUI-Probleme**: Tkinter-Backend-Unterstützung und Kamera-SDK-Verfügbarkeit auf Ihrer Plattform prüfen.

## Roadmap

- Reproduzierbarkeit von Abhängigkeiten/Bootstrap verbessern (`requirements.txt` oder Environment-Lockfile).
- Legacy-Skriptnamen und Pfadreferenzen in der Dokumentation konsolidieren.
- Dokumentierte Datensatz-Schemata und erwartete NPZ-Feldkonventionen erweitern.
- Regressionstests für Segmentierung/Kompensation auf kleinen Fixture-Daten hinzufügen.
- Publikationsreife Analyseausgaben aus `align_*`-Pipelines weiter integrieren.
- Verbleibende mehrsprachige README-Dateien unter `i18n/` hinzufügen/aktualisieren, damit sie vollständig den Sprachlinks oben entsprechen.

## Zitat

Wenn dieses Repository für Ihre Forschung nützlich ist, zitieren Sie bitte das Optica-Open-Preprint:

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

## Danksagung

- Optica-Open-Preprint und zugehörige Materialien zur Projektverbreitung.
- Hardware- und Software-Beitragende über die gesamte Repository-Evolution, dokumentiert in `versions/` und archivierten Tools.
- Community-Support über GitHub Sponsors und zugehörige Projektkanäle.

## Lizenz

Dieses Projekt wird unter der MIT-Lizenz veröffentlicht. Details siehe [`LICENSE`](LICENSE).

## Beitraegen

Beiträge sind willkommen.

- Mit bestehendem Skript- und Dokumentationsstil beginnen.
- Kommandozeilenbeispiele nach Möglichkeit mit reproduzierbaren Repository-Pfaden halten.
- Wenn große Datensätze/Ausgaben hinzugefügt werden, sicherstellen, dass die Richtlinien von `.githooks/pre-commit` eingehalten werden.

Hinweis: In diesem Checkout ist keine dedizierte `CONTRIBUTING.md` vorhanden. Bei Bedarf ein Issue eröffnen oder einen PR mit dem vorgeschlagenen Beitragsworkflow einreichen.

## Support / Sponsoring

| Kanal | Link | Zweck |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | Laufende Projektunterstützung |
| Projektseite | https://lazying.art | Projektupdates und Ökosystem-Links |
| Community-Chat | https://chat.lazying.art | Community-Diskussion |
| Zusätzliche Creator-Seite | https://onlyideas.art | Verwandte Creator-/Forschungsinhalte |
| Kern-Kit-Kaufseite | https://lazying.art/openhi-kit.html | Hardware-Starterkit für den OpenHI-Workflow |
| Promotion code | `OPTICA` | 30% Rabatt (wie oben dokumentiert) |

---

### Hinweise

- 📌 Diese README behält Hinweise zu Legacy-Pfaden, wenn die Repository-Evolution Namens-/Layoutabweichungen eingeführt hat.
- 🔒 Bei Unsicherheit zu älteren Referenzen wird Text absichtlich beibehalten statt entfernt.
