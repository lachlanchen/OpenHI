[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# 自我校準神經形態高光譜成像（OpenHI）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#先決條件)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#概覽)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#儲存庫地圖)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#附加工具)
[![Paper](https://img.shields.io/badge/Preprint-Optica%20Open-ff6b6b.svg)](https://doi.org/10.1364/opticaopen.30739151)
[![i18n](https://img.shields.io/badge/i18n-5%20ready%20%7C%206%20planned-22c55e.svg)](#國際化)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#概覽)

> [!NOTE]
> 此 checkout 的 i18n 狀態：`ar`、`es`、`fr`、`ja`、`ko` 已存在於 `i18n/`。其餘語言連結為了與規劃中的翻譯覆蓋範圍相容而保留。

一個完整流程，用於在色散光照（例如繞射光柵）下，從事件相機重建光譜。系統記錄強度變化事件 $e = (x, y, t, p)$，其中 $p \in \{-1, +1\}$ 表示對數強度變化的極性，並可直接從事件流中自動推斷掃描時序與校準中繼資料（"auto info"）。

## 快速總覽

| 項目 | 說明 |
|---|---|
| 核心概念 | 從事件流進行自我校準高光譜導數成像 |
| 主要階段 | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> 視覺化腳本 |
| 儲存庫中的硬體文件 | `3D/`、`PCB/`、`firmware/`、`BOM/` |
| 桌面工具 | `scan_compensation_gui_cloud.py`、`ImagingGUI/DualCamera_separate_transform.py` |
| 標準論文 | [Optica Open preprint（DOI: 10.1364/opticaopen.30739151）](https://doi.org/10.1364/opticaopen.30739151) |
| 此 checkout 的 i18n | `README.ar.md`、`README.es.md`、`README.fr.md`、`README.ja.md`、`README.ko.md` |

<p align="center">
  <img src="../images/device_setup.png" alt="裝置配置" width="24%">
  <img src="../images/data_acquisition_gui.png" alt="資料擷取 GUI" width="74%">
</p>

*左圖：模組化穿透式顯微系統，含馬達化光柵照明臂與垂直偵測堆疊。右圖：用於即時監看分段、補償與重建的資料擷取 GUI。*

> [!TIP]
> 購買論文 [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151)（已於 Optica Open 預印）所使用的核心開發套件（不含相機、tube lens 與光學平台）：
> - https://lazying.art/openhi-kit.html
> - 7 折優惠碼：`OPTICA`

## 目錄

- [快速總覽 📌](#快速總覽)
- [概覽 🔭](#概覽)
- [功能特色 ✨](#功能特色)
- [儲存庫地圖 🗺️](#儲存庫地圖)
- [專案結構 📁](#專案結構)
- [快速開始（5 分鐘路徑）⚡](#快速開始5-分鐘路徑)
- [先決條件 🧰](#先決條件)
- [安裝 ⚙️](#安裝)
- [使用方式 🚀](#使用方式)
- [國際化 🌍](#國際化)
- [設定 🎛️](#設定)
- [範例 🧪](#範例)
- [材料清單（核心模組）🧾](#材料清單核心模組)
- [核心腳本 🧠](#核心腳本)
- [附加工具 🛠️](#附加工具)
- [Turbo 多掃描補償 ⚡](#turbo-多掃描補償)
- [參數管理 💾](#參數管理)
- [記憶體最佳化 🧱](#記憶體最佳化)
- [輸出結構 📦](#輸出結構)
- [設定範例 🧩](#設定範例)
- [波長映射 🌈](#波長映射)
- [技巧與最佳實務 ✅](#技巧與最佳實務)
- [開發備註 🧭](#開發備註)
- [疑難排解 🩺](#疑難排解)
- [路線圖 🛣️](#路線圖)
- [引用 📎](#引用)
- [致謝 🙏](#致謝)
- [授權 📄](#授權)
- [貢獻 🤝](#貢獻)
- [支持 / 贊助 💖](#支持--贊助)

## 概覽

當照明隨時間掃過不同波長時，事件流會在色散軸上編碼出底層光譜的時間導數。

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

此流程包含三個主要階段：

| 階段 | 目的 | 主要腳本 |
|---|---|---|
| 1. 分段 | 找出掃描時序，並將錄製內容切分為前向/後向通道 | `segment_robust_fixed.py` |
| 2. 補償 | 估計分段線性 time-warp，以移除掃描引入的時間傾斜 | `compensate_multiwindow_train_saved_params.py` |
| 3. 視覺化 | 疊加學習到的邊界，並比較原始與補償後的時間分箱影格 | `visualize_boundaries_and_frames.py`、`visualize_cumulative_compare.py` |

儲存庫也包含硬體資產、擷取 GUI 程式碼，以及 `versions/` 下的歷史實驗分支。

## 功能特色

- 端到端 RAW-to-spectrum 事件處理工作流。
- 自動/手動掃描週期偵測與前向/後向分段。
- 多視窗補償，支援可訓練/固定參數模式。
- 支援 `NPZ`、`JSON`、`CSV` 的參數儲存/載入。
- 多掃描合併流程，加速訓練迭代（`compensate_multiwindow_turbo.py`）。
- 視覺化套件涵蓋邊界、分箱影格、累積曲線與加權診斷。
- 硬體文件：BOM、PCB、3D 零件與韌體備註。
- 同步事件相機/幀相機擷取工具。

| 類別 | 內含能力 |
|---|---|
| 訊號處理 | 分段、週期偵測、time-warp 補償 |
| 最佳化 | 可訓練/固定參數、平滑控制、分塊訓練 |
| 輸出 | 視覺疊圖、累積比較、波長映射診斷 |
| 平台資產 | 硬體設計檔、韌體備註、GUI 工具、歷史檔案 |

## 儲存庫地圖

關鍵硬體資產與程式碼放在同一個儲存庫，方便快速存取：

| 區域 | 路徑 |
|---|---|
| 3D 列印零件 | [`3D/`](../3D/) |
| PCB 佈局 | [`PCB/`](../PCB/) |
| 微控制器韌體 | [`firmware/`](../firmware/) |
| 擷取 UI（桌面） | [`ImagingGUI/`](../ImagingGUI/) |
| 實驗/資料參考 | [`reference_spectrum_2835/`](../reference_spectrum_2835/)、[`reference_spectrum_lumileds/`](../reference_spectrum_lumileds/)、[`references/`](../references/) |
| 對齊分析 | [`align_background_vs_reference_code/`](../align_background_vs_reference_code/)、[`align_data_vs_filter_code/`](../align_data_vs_filter_code/) |

## 專案結構

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

## 快速開始（5 分鐘路徑）

如果你的環境已準備完成，且資料集目錄中包含 `*event*.raw` 檔案：

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

若要強制指定特定 RAW 檔案：

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

此 wrapper 會使用儲存庫預設腳本路徑與 CLI 參數，執行分段、補償訓練與視覺化。

> [!TIP]
> 初次驗證時，先在單一資料夾執行 wrapper，再檢查產生的 segment NPZ 與視覺化輸出，之後再調整 `PIPELINE_*` 變數。

## 先決條件

- Python 3.9+（`ImagingGUI/` 下部分 GUI 工具建議 Python 3.10+）。
- 核心 Python 套件：`numpy`、`torch`、`matplotlib`。
- 選用但常見：`opencv-python`、`pillow`、`cellpose`。
- Metavision SDK / Python 綁定（用於 RAW 事件讀取流程，例如 `simple_raw_reader.py` 與 RAW 分段）。
- 建議使用啟用 CUDA 的 PyTorch 以加速最佳化。
- 本機需有 RAW 錄製檔與/或分段 NPZ 檔案。

## 安裝

目前儲存庫根目錄沒有鎖定的環境檔。建議設定如下：

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

若你使用 Git hooks 管理大檔案提交規範：

```bash
bash scripts/setup_hooks.sh
```

## 使用方式

### 基本流程（目前根目錄腳本）

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

### 一行命令便利 wrapper

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

`scripts/run_scan_pipeline.sh` 支援的環境變數：

| 變數 | 預設值 | 用途 |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | 活躍事件視窗比例 |
| `PIPELINE_BIN_WIDTH` | `50000` | 訓練時間分箱寬度（微秒） |
| `PIPELINE_SENSOR_WIDTH` | `1280` | 視覺化使用的感測器寬度 |
| `PIPELINE_SENSOR_HEIGHT` | `720` | 視覺化使用的感測器高度 |
| `PIPELINE_SAMPLE_RATE` | `0.10` | 繪圖事件抽樣比例 |
| `PIPELINE_TIME_BIN_US` | `1000` | 分段活動分箱大小 |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | 下游腳本使用的 segment 檔案模式 |

## 國際化

儲存庫在每個 README 頂部使用單一語言選項列，避免重複語言列。

目前 `i18n/` 中已提供的翻譯檔案：

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`

| 導覽列語言連結 | `i18n/` 中對應檔案 | 狀態 |
|---|---|---|

規劃中的語言連結會刻意保留在頂部導覽列中，以確保前向相容性。

## 設定

各腳本常用的重要 CLI 控制項：

### 分段（`segment_robust_fixed.py`）

- `--time_bin_us`：活動分箱大小（微秒）。
- `--round_trip_period`：手動週期（預設 `1688` bins）。
- `--auto_calculate_period`：以自相關估算週期。
- `--activity_fraction`：活躍事件視窗比例。
- `--manual_start_shift_ms`：手動掃描起始偏移。

### 補償（`compensate_multiwindow_train_saved_params.py`）

- `--num_params`（預設 `13`）、`--temperature`（預設 `5000`）。
- `--a_trainable` / `--a_fixed`、`--b_trainable` / `--b_fixed`、`--boundary_trainable`。
- `--a_default`、`--b_default`。
- `--iterations`、`--learning_rate`、`--smoothness_weight`。
- `--chunk_size` 用於記憶體控制。
- `--load_params` 重用已學習參數。

### 視覺化

- `visualize_boundaries_and_frames.py`：`--sample_rate`、`--wavelength_min`、`--wavelength_max`、感測器尺寸參數。
- `visualize_cumulative_compare.py`：感測器尺寸、`--output_dir`、`--sample_label`。
- `visualize_cumulative_weighted.py`：極性縮放、`--step_us`、`--auto_scale`、`--exp`、`--no_comp`。

## 範例

### 快速開始資料集風格命令（來自 `QUICKSTART.md`）

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

### 保留自歷史工作流的舊版輔助命令

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

這些舊版命令會刻意保留作為相容性背景；在此 checkout 中，請優先使用目前根目錄腳本。

### Turbo 多掃描訓練

```bash
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/your_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params
```

### 重用已學習參數（略過重新訓練）

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

## 材料清單（核心模組）

完整表格與連結、備註請見 [`BOM/core_module.md`](../BOM/core_module.md)。

### 表 S2. 本方法事件驅動系統與參考高光譜相機的採集時間與成本比較

| 參數 | 本系統 | 參考相機 |
|---|---|---|
| 採集時間 | 每次掃描約 ∼585 ms | 每次掃描 300 s |
| 資料量 | 18.5 MB | 138 MB |
| 約略價格 | 約 ∼3000 USD | 14 000 USD |

### 表 S3. 核心掃描照明模組材料清單
（不含事件相機與可選 4f 驗證光學）

| 元件 | 備註 | 成本（USD） | Taobao 連結 |
|---|---|---:|---|
| 運動控制 | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| 光學（光柵） | 繞射光柵（教育級） | 3.47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPRouNw |
| 照明 | 2835 LED（6 CNY / 10 pcs；使用 0.6 CNY） | 0.08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| 反射鏡 | 折疊反射鏡 | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| 電子元件 | LED PCB（CNY/板；最小訂量 5 片） | 1.67 |  |
| 限位開關 | 選配，2 × 8.07 CNY | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| 3D 列印 | PLA 線材約三分之一卷（涵蓋所有列印件） | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| 透鏡 | 平凸透鏡（25.4 mm，350–700 nm AR） |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| 總計 | 核心模組 | **33.99** |  |

## 核心腳本

### 1. 分段：`segment_robust_fixed.py`

**目標**：從原始事件提取掃描時序，並切成 6 個單向掃描（F、B、F、B、F、B）。

**數學描述**：

- **活動訊號**（以 $\Delta t = 1000~\mu\text{s}$ 分箱）：
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **活躍視窗偵測**：找到包含 $80\%$ 事件的最小連續視窗。

- **週期估計**：自相關或手動週期（預設：$1688$ bins）。

- **反向相關**（時序結構）：
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  其中
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**用法**：

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**參數**：

- `--segment_events`：將單次掃描片段儲存為 NPZ。
- `--round_trip_period 1688`：使用手動週期（預設）。
- `--auto_calculate_period`：以自相關覆寫手動週期。
- `--activity_fraction 0.80`：活躍區域事件比例。
- `--max_iterations 2`：細化迭代次數。

### 2. 補償：`compensate_multiwindow_train_saved_params.py`

**目標**：學習 time-warp 參數，透過多視窗分段線性補償移除掃描造成的時間剪切。

**數學描述**：

- **邊界曲面**：
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **軟視窗歸屬**：
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **插值斜率（選用）**：
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **時間扭曲**：
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **損失函數**：最小化時間分箱影格的方差，並對參數施加平滑正則化。

**用法**：

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**主要參數**：

- `--a_trainable` / `--a_fixed`：控制 a 參數是否訓練（預設：固定）。
- `--b_trainable` / `--b_fixed`：控制 b 參數是否訓練（預設：可訓練）。
- `--num_params 13`：邊界參數數量。
- `--temperature 5000`：軟視窗 sigmoid 溫度。
- `--smoothness_weight 0.001`：正則化權重。
- `--load_params file.npz`：載入已儲存參數。
- `--chunk_size 250000`：記憶體友善的分塊處理大小。

### 3. 視覺化：`visualize_boundaries_and_frames.py`

**目標**：顯示學習後參數，並呈現質化改善效果。

**功能**：

- 在 $x\text{–}t$ 與 $y\text{–}t$ 投影上疊加參數。
- 時間分箱影格比較（原始 vs. 補償）。
- 滑動視窗分析（50 ms 與 2 ms bins）。
- 用於光譜視覺化的波長映射。

**用法**：

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. 累積比較：`visualize_cumulative_compare.py`

**目標**：比較累積 2 ms 步進平均與滑動分箱平均。

**數學描述**：

- **累積平均**：
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **滑動平均**：在 $[T-\Delta,\,T)$ 中的事件計數除以 $H \times W$。

- **關係式**（有限差分導數）：
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**用法**：

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## 附加工具

### GUI 應用程式：`scan_compensation_gui_cloud.py`

完整的掃描補償 GUI，含 3D 光譜視覺化。

**功能**：

- 互動式參數調整。
- 即時最佳化進度。
- 3D 波長映射視覺化。
- 匯出結果與參數。

**用法**：

```bash
python scan_compensation_gui_cloud.py
```

### 雙相機系統（目前路徑）

用於事件相機與幀相機同步錄製：

- `ImagingGUI/DualCamera_separate_transform.py`

**功能**：

- 事件與影格同步錄製。
- 含轉換的即時預覽。
- 視窗置頂控制。
- 錄製期間可調參數。

### Arduino 馬達控制（保留舊版路徑參考）

原 README 曾引用此韌體草圖路徑：

- `rotor/step42_with_key_int/step42_with_key_int.ino`

目前儲存庫版面中的韌體備註位於：

- `firmware/README.md`

此路徑差異會刻意保留；若你在其他分支/本機 checkout 中有 rotor 草圖資料夾，請持續使用那些路徑。

此草圖在舊版文件中描述的功能包括：

- 透過微步進進行精準角度控制。
- 加速/減速控制曲線。
- 限位開關整合。
- 自動回中功能。

## Turbo 多掃描補償

當你有同一輪掃描的多個單向片段（Forward/Backward）時，可使用 `compensate_multiwindow_turbo.py` 合併後，透過單一合併事件流呼叫既有訓練器。

### 功能說明

- 接受單一 segment、明確列表，或整個 segments 目錄。
- 對 Backward 掃描會先翻轉極性、再反轉時間後合併：
- 若極性 `p ∈ {0,1}`：`p := 1 − p`；然後在該掃描內反轉時間。
- 若極性 `p ∈ {−1,1}`：`p := −p`；然後在該掃描內反轉時間。
- 以連續時間軸串接掃描（掃描間保留 `1 μs` 間隔），並在底層呼叫 `compensate_multiwindow_train_saved_params.py`。

### 用法

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

### 選項

- `--segment`、`--segments`、`--segments-dir`：選擇輸入集合。
- `--include {all|forward|backward}`：依掃描方向篩選。
- `--sort {name|time}`：依檔名自然排序或依 NPZ `start_time` 排序。
- `--bin-width <μs>`：轉發給基礎訓練器。
- `--load-params`：重用儲存參數（可略過訓練，快速在新 bin width 產生輸出）。
- `--extra ...`（置於 `--` 之後）：任何額外旗標都會轉發到基礎訓練器。

### 速度縮放建議

如果掃描速度比基準快 `N×`，請將 `--bin-width` 依同樣倍數縮小（例如基準 `50 ms` -> 快 `10×` -> `5 ms`：`--bin-width 5000`）。你可先訓練一次（例如 `5 ms`），再用 `--load-params` 快速在 `10 ms` 產生結果而不必重訓。

## 參數管理

系統支援完整的參數儲存/載入流程。

### 儲存格式

- **NPZ**：二進位格式，載入快速。
- **JSON**：人類可讀，含中繼資料。
- **CSV**：可用 Excel 檢視與人工檢查。

### 參數載入

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### 參數檔命名

檔名會自動包含參數數量，例如：`*_learned_params_n13.*`。

## 記憶體最佳化

系統在整個流程中採用分塊處理：

| 項目 | 說明 |
|---|---|
| Chunk Size | 預設 `250000` 事件（可設定） |
| Memory Efficient | 可處理大型資料集而不致 GPU 溢位 |
| Unified Variance | 維持正確梯度流以支援學習 |
| Progress Tracking | 即時顯示處理進度 |

## 輸出結構

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

## 設定範例

### 高精度補償

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### 快速處理

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### 記憶體受限情境

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## 波長映射

系統可將時間演化映射到波長進行光譜視覺化：

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**預設範圍**：$380\text{–}680~\text{nm}$（可調整）。

## 技巧與最佳實務

### 參數選擇

- **Microstepping**：建議 `32×` 以獲得平順運動（Arduino）。
- **Bin Width**：最佳化先用 `50 ms`，分析可用 `2 ms`。
- **Temperature**：較高值（約 `5000`）可得到更平滑的邊界。
- **Smoothness**：`0.001` 通常有良好正則化效果。

### 記憶體管理

- **GPU 記憶體**：以合適 chunk size 進行分塊處理。
- **事件數量**：建議 `> 10^6` 事件以獲得穩定學習。
- **Iterations**：通常 `1000` 次迭代已足夠。

### 檔案組織

- 將 RAW 檔與 segments 放在同一目錄。
- 參數檔可透過命名慣例自動偵測。
- 使用具描述性的檔名前綴，便於整理輸出。

## 開發備註

- `versions.md` 描述專案歷史階段與遷移原因。
- `.githooks/pre-commit` 會阻擋過大/二進位提交，以及非程式/文件檔案型別。
- `scripts/setup_hooks.sh` 會將 `core.hooksPath` 指向 `.githooks`。
- `archive_code_variants/` 保存舊版腳本，讓根目錄工具維持聚焦。

已知文件漂移（為向後相容背景而刻意保留）：

- 部分舊文件提到 `sync_image_system/` 或 `dual_camera_gui.py`；目前 checkout 為 `ImagingGUI/DualCamera_separate_transform.py` 與 SDK 目錄。
- `ImagingGUI/README.md` 仍提到 `pip install -r requirements.txt`，但此 checkout 根目錄沒有 `requirements.txt`。
- `firmware/README.md` 參考數個 Arduino 草圖子資料夾，但這些資料夾在此 checkout 不存在。
- `versions.md` 提到的舊腳本名稱與目前根目錄腳本名稱不同。
- `i18n/` 已存在，且目前包含 `README.ar.md`、`README.es.md`、`README.fr.md`、`README.ja.md`、`README.ko.md`；其他語言連結保留為規劃目標。

## 疑難排解

| 症狀 | 可能原因 | 建議動作 |
|---|---|---|
| 參數載入錯誤 | 參數數量不匹配 | 確認 `--num_params` 與儲存檔一致 |
| OOM / 記憶體壓力 | chunk 太大或 bin 太細 | 降低 `--chunk_size` 和/或提高 `--bin_width` |
| 補償效果不佳 | 訓練不足或分段品質差 | 增加 `--iterations`、啟用可訓練參數並檢查分段 |
| 未產生 segment 檔 | RAW/SDK/旗標問題 | 確認 RAW 路徑、Metavision 設定與 `--segment_events` |
| Turbo wrapper 參數未生效 | 轉發語法錯誤 | 訓練器參數需放在 `--` 之後（或用 `--extra`） |
| GUI 問題 | Tkinter/backend 或 SDK 不相容 | 檢查 GUI backend 與相機 SDK 可用性 |

- **參數載入錯誤**：確認 `--num_params` 與載入的參數檔相容。
- **OOM / 記憶體壓力**：降低 `--chunk_size` 和/或提高 `--bin_width`。
- **補償效果不佳**：提高 `--iterations`、啟用可訓練參數（`--a_trainable`、`--b_trainable`，可選 `--boundary_trainable`），並檢查分段品質。
- **未產生 segment 檔**：確認 RAW 路徑、Metavision reader 可用性，以及是否傳入 `--segment_events`。
- **Turbo wrapper 參數傳遞**：將訓練器參數放在 `--` 之後（或使用 `--extra`）。
- **GUI 問題**：確認平台上 Tkinter backend 與相機 SDK 是否可用。

## 路線圖

- 改善依賴/啟動重現性（`requirements.txt` 或環境 lockfile）。
- 整合文件中的舊腳本名稱與路徑參考。
- 擴充資料集格式與 NPZ 欄位慣例的文件說明。
- 為分段/補償加入小型 fixture 資料的回歸測試。
- 持續整合 `align_*` 流程中的論文級分析輸出。
- 補齊/更新 `i18n/` 下尚未完成的多語 README，使其與頂部語言導覽連結完全一致。

## 引用

若此儲存庫對你的研究有幫助，請引用 Optica Open 預印本：

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

## 致謝

- Optica Open 預印本與相關專案傳播素材。
- 儲存庫演進過程中的硬體與軟體貢獻者（記錄於 `versions/` 與封存工具）。
- 透過 GitHub Sponsors 與相關專案社群提供的支持。

## 授權

本專案採用 MIT License。詳見 [`LICENSE`](../LICENSE)。

## 貢獻

歡迎提交貢獻。

- 請先遵循既有腳本與文件風格。
- 盡量讓命令列範例可用儲存庫路徑直接重現。
- 若新增大型資料集/輸出，請確認符合 `.githooks/pre-commit` 規範。

注意：此 checkout 中沒有專門的 `CONTRIBUTING.md`。如有需要，請開 issue 或提交 PR，提出你建議的貢獻流程。

## 支持 / 贊助

| 管道 | 連結 | 用途 |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | 持續支持專案 |
| 專案網站 | https://lazying.art | 專案更新與生態系連結 |
| 社群聊天 | https://chat.lazying.art | 社群討論 |
| 額外創作者頁面 | https://onlyideas.art | 相關創作/研究內容 |
| 核心套件購買頁 | https://lazying.art/openhi-kit.html | OpenHI 工作流硬體入門套件 |
| 優惠碼 | `OPTICA` | 7 折（如上所述） |

---

### 備註

- 📌 本 README 保留了因儲存庫演進導致命名/版面差異的舊路徑說明。
- 🔒 若對舊參考有疑慮，會優先保留原文脈絡，而非直接刪除。
