[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# Imágenes Hiperespectrales Neuromórficas Autocalibradas (OpenHI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#requisitos-previos)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#visión-general)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#mapa-del-repositorio)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#herramientas-adicionales)
[![Paper](https://img.shields.io/badge/Preprint-Optica%20Open-ff6b6b.svg)](https://doi.org/10.1364/opticaopen.30739151)
[![i18n](https://img.shields.io/badge/i18n-5%20ready%20%7C%206%20planned-22c55e.svg)](#internacionalización)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#visión-general)

> [!NOTE]
> Estado i18n en este checkout: `ar`, `es`, `fr`, `ja`, `ko` están presentes en `i18n/`. Los enlaces de idiomas adicionales se mantienen por compatibilidad con la cobertura de traducción planificada.

Una canalización integral para reconstruir espectros a partir de cámaras de eventos con iluminación de luz dispersa (p. ej., rejilla de difracción). El sistema registra eventos de cambio de intensidad $e = (x, y, t, p)$ donde $p \in \{-1, +1\}$ indica la polaridad del cambio de log-intensidad, e infiere automáticamente la temporización del barrido y metadatos de calibración ("auto info") directamente desde el flujo de eventos.

## Resumen Rápido

| Ítem | Detalles |
|---|---|
| Idea central | Imagen hiperespectral derivativa autocalibrada a partir de flujos de eventos |
| Etapas principales | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> scripts de visualización |
| Documentación de hardware en el repo | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Herramientas de escritorio | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Artículo canónico | [Preprint en Optica Open (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n en este checkout | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md` |

<p align="center">
  <img src="../images/device_setup.png" alt="Montaje del dispositivo" width="24%">
  <img src="../images/data_acquisition_gui.png" alt="GUI de adquisición" width="74%">
</p>

*Izquierda: microscopio de transmisión modular con brazo de iluminación por rejilla motorizado y columna de detección vertical. Derecha: GUI de adquisición de datos usada para monitorear segmentación, compensación y reconstrucciones en tiempo real.*

> [!TIP]
> Compra el kit principal de desarrollo (sin cámara, lente de tubo ni mesa óptica) del artículo [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151) publicado como preprint en Optica Open:
> - https://lazying.art/openhi-kit.html
> - Código promocional con 30% de descuento: `OPTICA`

## Contenido

- [Resumen Rápido 📌](#resumen-rápido)
- [Visión general 🔭](#visión-general)
- [Características ✨](#características)
- [Mapa del repositorio 🗺️](#mapa-del-repositorio)
- [Estructura del proyecto 📁](#estructura-del-proyecto)
- [Inicio rápido (ruta de 5 min) ⚡](#inicio-rápido-ruta-de-5-min)
- [Requisitos previos 🧰](#requisitos-previos)
- [Instalación ⚙️](#instalación)
- [Uso 🚀](#uso)
- [Internacionalización 🌍](#internacionalización)
- [Configuración 🎛️](#configuración)
- [Ejemplos 🧪](#ejemplos)
- [Lista de materiales (módulo principal) 🧾](#lista-de-materiales-módulo-principal)
- [Scripts principales 🧠](#scripts-principales)
- [Herramientas adicionales 🛠️](#herramientas-adicionales)
- [Compensación turbo multi-scan ⚡](#compensación-turbo-multi-scan)
- [Gestión de parámetros 💾](#gestión-de-parámetros)
- [Optimización de memoria 🧱](#optimización-de-memoria)
- [Estructura de salida 📦](#estructura-de-salida)
- [Ejemplos de configuración 🧩](#ejemplos-de-configuración)
- [Mapeo de longitud de onda 🌈](#mapeo-de-longitud-de-onda)
- [Consejos y buenas prácticas ✅](#consejos-y-buenas-prácticas)
- [Notas de desarrollo 🧭](#notas-de-desarrollo)
- [Solución de problemas 🩺](#solución-de-problemas)
- [Hoja de ruta 🛣️](#hoja-de-ruta)
- [Citación 📎](#citación)
- [Agradecimientos 🙏](#agradecimientos)
- [Licencia 📄](#licencia)
- [Contribuciones 🤝](#contribuciones)
- [Soporte / Patrocinio 💖](#soporte--patrocinio)

## Visión general

Cuando la iluminación barre longitudes de onda a lo largo del tiempo, el flujo de eventos codifica una derivada temporal del espectro subyacente a lo largo del eje de dispersión.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

Esta canalización ofrece tres etapas principales:

| Etapa | Objetivo | Script(s) principal(es) |
|---|---|---|
| 1. Segmentar | Encontrar la temporización del barrido y dividir grabaciones en pasadas hacia delante/atrás | `segment_robust_fixed.py` |
| 2. Compensar | Estimar una deformación temporal lineal por tramos para eliminar la inclinación temporal inducida por el barrido | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualizar | Superponer fronteras aprendidas y comparar cuadros con bin temporal (original vs. compensado) | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

El repositorio también incluye recursos de hardware, código GUI de adquisición y ramas de experimentos archivadas en `versions/`.

## Características

- Flujo de trabajo integral de procesamiento de eventos desde RAW hasta espectro.
- Detección automática/manual del periodo de barrido y segmentación hacia delante/atrás.
- Compensación multi-ventana con modos de parámetros entrenables/fijos.
- Guardado/carga de parámetros en `NPZ`, `JSON` y `CSV`.
- Flujo de combinación multi-scan para iteraciones de entrenamiento más rápidas (`compensate_multiwindow_turbo.py`).
- Suite de visualización para fronteras, cuadros con bins, curvas acumulativas y diagnósticos ponderados.
- Documentación de hardware: BOM, PCB, piezas 3D y notas de firmware.
- Utilidades de adquisición para configuraciones sincronizadas de cámaras de eventos/fotogramas.

| Categoría | Capacidades incluidas |
|---|---|
| Procesamiento de señal | Segmentación, detección de periodo, compensación por deformación temporal |
| Optimización | Parámetros entrenables/fijos, controles de suavidad, entrenamiento por bloques |
| Salidas | Superposiciones visuales, comparaciones acumulativas, diagnósticos mapeados a longitud de onda |
| Activos de plataforma | Archivos de diseño de hardware, notas de firmware, herramientas GUI, archivos históricos |

## Mapa del repositorio

Los recursos clave de hardware se mantienen junto al código para acceso rápido:

| Área | Ruta |
|---|---|
| Piezas impresas en 3D | [`3D/`](../3D/) |
| Diseños PCB | [`PCB/`](../PCB/) |
| Firmware del microcontrolador | [`firmware/`](../firmware/) |
| UI de adquisición (escritorio) | [`ImagingGUI/`](../ImagingGUI/) |
| Referencias de experimento/datos | [`reference_spectrum_2835/`](../reference_spectrum_2835/), [`reference_spectrum_lumileds/`](../reference_spectrum_lumileds/), [`references/`](../references/) |
| Análisis de alineación | [`align_background_vs_reference_code/`](../align_background_vs_reference_code/), [`align_data_vs_filter_code/`](../align_data_vs_filter_code/) |

## Estructura del proyecto

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

## Inicio rápido (ruta de 5 min)

Si tu entorno ya está preparado y tu carpeta de dataset contiene un archivo `*event*.raw`:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

Para forzar un archivo RAW específico:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

Este wrapper ejecuta segmentación, entrenamiento de compensación y visualización usando rutas de scripts y flags CLI predeterminados del repositorio.

> [!TIP]
> Para la primera validación, ejecuta el wrapper sobre un directorio de dataset y luego inspecciona el NPZ segmentado generado y las salidas de visualización antes de ajustar variables `PIPELINE_*`.

## Requisitos previos

- Python 3.9+ (Python 3.10+ para algunas herramientas GUI en `ImagingGUI/`).
- Paquetes Python principales: `numpy`, `torch`, `matplotlib`.
- Opcionales pero comunes: `opencv-python`, `pillow`, `cellpose`.
- Metavision SDK / bindings de Python para flujos de lectura RAW (`simple_raw_reader.py`, segmentación desde RAW).
- Se recomienda PyTorch con CUDA para una optimización más rápida.
- Grabaciones RAW y/o archivos NPZ segmentados disponibles localmente.

## Instalación

Actualmente no se proporciona un archivo de entorno bloqueado en la raíz del repositorio. Configuración sugerida:

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

Si usas hooks de Git para higiene de archivos grandes:

```bash
bash scripts/setup_hooks.sh
```

## Uso

### Flujo básico (scripts actuales en raíz)

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

### Wrapper práctico de un solo comando

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

Variables de entorno soportadas por `scripts/run_scan_pipeline.sh`:

| Variable | Valor predeterminado | Propósito |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Fracción de ventana de eventos activa |
| `PIPELINE_BIN_WIDTH` | `50000` | Ancho de bin de entrenamiento en microsegundos |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Ancho del sensor para visualización |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Alto del sensor para visualización |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Fracción de muestreo de eventos para gráficas |
| `PIPELINE_TIME_BIN_US` | `1000` | Tamaño de bin de actividad para segmentación |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Patrón de archivo de segmento para scripts posteriores |

## Internacionalización

El repositorio usa una sola línea de opciones de idioma al inicio de cada README para evitar barras de idioma duplicadas.

Archivos traducidos disponibles actualmente en `i18n/`:

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`

| Enlace de idioma en la navegación | Archivo en `i18n/` | Estado |
|---|---|---|

Los enlaces de idiomas planificados se conservan intencionalmente en la navegación superior para compatibilidad futura.

## Configuración

Controles CLI importantes usados en los scripts:

### Segmentación (`segment_robust_fixed.py`)

- `--time_bin_us`: tamaño del bin de actividad en microsegundos.
- `--round_trip_period`: periodo manual (predeterminado `1688` bins).
- `--auto_calculate_period`: periodo vía autocorrelación.
- `--activity_fraction`: fracción de ventana de eventos activa.
- `--manual_start_shift_ms`: desplazamiento manual del inicio del barrido.

### Compensación (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (predeterminado `13`), `--temperature` (predeterminado `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` para control de memoria.
- `--load_params` para reutilizar parámetros aprendidos.

### Visualización

- `visualize_boundaries_and_frames.py`: `--sample_rate`, `--wavelength_min`, `--wavelength_max`, argumentos de tamaño de sensor.
- `visualize_cumulative_compare.py`: tamaño de sensor, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py`: escalas de polaridad, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

## Ejemplos

### Comandos de inicio rápido estilo dataset (de `../QUICKSTART.md`)

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

### Comandos helper heredados conservados de flujos históricos

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

Estos comandos heredados se conservan intencionalmente para contexto de compatibilidad; en este checkout, usa scripts actuales de la raíz cuando sea posible.

### Entrenamiento turbo multi-scan

```bash
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/your_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params
```

### Reutilizar parámetros aprendidos (omitir reentrenamiento)

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

## Lista de materiales (módulo principal)

Consulta [`../BOM/core_module.md`](../BOM/core_module.md) para la tabla completa con enlaces y notas.

### Tabla S2. Comparación de tiempo y costo de adquisición entre el sistema orientado a eventos propuesto y una cámara hiperespectral de referencia

| Parámetro | Nuestro sistema | Cámara de referencia |
|---|---|---|
| Tiempo de adquisición | ∼585 ms por barrido | 300 s por barrido |
| Volumen de datos | 18.5 MB | 138 MB |
| Precio aproximado | ∼3000 USD | 14 000 USD |

### Tabla S3. Lista de materiales del módulo central de iluminación por barrido
(Excluye cámara de eventos y óptica opcional de validación 4f)

| Componente | Notas | Costo (USD) | Enlace Taobao |
|---|---|---:|---|
| Control de movimiento | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| Óptica (rejilla) | Rejilla de difracción (grado educativo) | 3.47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPRouNw |
| Iluminación | LED 2835 (6 CNY / 10 piezas; se usa 0.6 CNY) | 0.08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| Reflector | Espejo plegable | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| Electrónica | PCB LED (CNY/placa; pedido mínimo 5 piezas) | 1.67 |  |
| Interruptores de límite | Opcional, 2 × 8.07 CNY | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| Impresión 3D | Un tercio de bobina PLA (cubre todas las piezas impresas) | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| Lente | Lente plano-convexa (25.4 mm, AR 350–700 nm) |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| Total | módulo central | **33.99** |  |

## Scripts principales

### 1. Segmentación: `segment_robust_fixed.py`

**Objetivo**: Extraer la temporización del barrido desde eventos RAW y dividir en 6 barridos unidireccionales (F, B, F, B, F, B).

**Descripción matemática**:

- **Señal de actividad** (eventos agrupados con $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Detección de ventana activa**: encontrar la ventana contigua más pequeña que contenga el $80\%$ de los eventos.

- **Estimación de periodo**: autocorrelación o periodo manual (predeterminado: $1688$ bins).

- **Correlación inversa** (estructura temporal):
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  con
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**Uso**:

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Argumentos**:

- `--segment_events`: guardar segmentos individuales de barrido como archivos NPZ.
- `--round_trip_period 1688`: usar periodo manual (predeterminado).
- `--auto_calculate_period`: reemplazar periodo manual con autocorrelación.
- `--activity_fraction 0.80`: fracción de eventos para la región activa.
- `--max_iterations 2`: iteraciones de refinamiento.

### 2. Compensación: `compensate_multiwindow_train_saved_params.py`

**Objetivo**: Aprender parámetros de deformación temporal para eliminar cizallamiento temporal inducido por el barrido usando compensación lineal por tramos y multi-ventana.

**Descripción matemática**:

- **Superficies frontera**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Pertenencias suaves a ventana**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Pendientes interpoladas (opcional)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Deformación temporal**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Pérdida**: minimización de varianza de cuadros con bin temporal y regularización de suavidad sobre parámetros.

**Uso**:

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**Argumentos clave**:

- `--a_trainable` / `--a_fixed`: control del entrenamiento de parámetros `a` (predeterminado: fijo).
- `--b_trainable` / `--b_fixed`: control del entrenamiento de parámetros `b` (predeterminado: entrenable).
- `--num_params 13`: número de parámetros de frontera.
- `--temperature 5000`: temperatura sigmoide para ventanas suaves.
- `--smoothness_weight 0.001`: peso de regularización.
- `--load_params file.npz`: cargar parámetros guardados.
- `--chunk_size 250000`: tamaño de bloque para procesamiento eficiente en memoria.

### 3. Visualización: `visualize_boundaries_and_frames.py`

**Objetivo**: Mostrar parámetros aprendidos y mejoras cualitativas.

**Características**:

- Superposiciones de parámetros sobre proyecciones $x\text{–}t$ y $y\text{–}t$.
- Comparaciones de cuadros con bin temporal (original vs. compensado).
- Análisis con ventana deslizante (bins de 50 ms y 2 ms).
- Mapeo de longitud de onda para visualización espectral.

**Uso**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Comparación acumulativa: `visualize_cumulative_compare.py`

**Objetivo**: Comparar medias acumulativas en pasos de 2 ms con medias en bins deslizantes.

**Descripción matemática**:

- **Medias acumulativas**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Medias deslizantes**: conteos de eventos en $[T-\Delta,\,T)$ divididos por $H \times W$.

- **Relación** (derivada por diferencia finita):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Uso**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Herramientas adicionales

### Aplicación GUI: `scan_compensation_gui_cloud.py`

GUI completa para compensación de barrido con visualización espectral 3D.

**Características**:

- Ajuste interactivo de parámetros.
- Progreso de optimización en tiempo real.
- Visualización 3D mapeada a longitud de onda.
- Exportación de resultados y parámetros.

**Uso**:

```bash
python scan_compensation_gui_cloud.py
```

### Sistema de doble cámara (ruta actual)

Sistema de grabación sincronizada para cámaras de eventos y de fotogramas:

- `ImagingGUI/DualCamera_separate_transform.py`

**Características**:

- Grabación simultánea de eventos y fotogramas.
- Previsualización en tiempo real con transformaciones.
- Controles de ventana siempre al frente.
- Ajuste de parámetros durante la grabación.

### Control de motor con Arduino (referencia de ruta heredada)

El README original hacía referencia a esta ruta de sketch de firmware:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

La estructura actual del repositorio incluye notas de firmware en:

- `firmware/README.md`

Esta discrepancia de rutas se conserva intencionalmente; si tienes carpetas de sketch `rotor` en otra rama o checkout local, sigue usando esas rutas.

Las capacidades heredadas documentadas de este sketch incluyen:

- Control preciso de ángulo con microstepping.
- Perfiles de aceleración/deceleración.
- Integración de interruptores de límite.
- Funcionalidad de autocentrado.

## Compensación turbo multi-scan

Cuando tienes múltiples barridos unidireccionales (Forward/Backward) del mismo barrido, puedes combinarlos y ejecutar el entrenador probado sobre un único flujo de eventos combinado usando `compensate_multiwindow_turbo.py`.

### Qué hace

- Acepta un segmento, una lista explícita o un directorio completo de segmentos.
- Para barridos Backward, invierte polaridad y tiempo antes de combinar:
- Si la polaridad `p ∈ {0,1}`: `p := 1 − p`; luego invierte el tiempo dentro del barrido.
- Si la polaridad `p ∈ {−1,1}`: `p := −p`; luego invierte el tiempo dentro del barrido.
- Concatena barridos en una línea de tiempo continua (con una separación de `1 μs` entre barridos) y llama internamente a `compensate_multiwindow_train_saved_params.py`.

### Uso

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

### Opciones

- `--segment`, `--segments`, `--segments-dir`: elegir conjunto de entrada.
- `--include {all|forward|backward}`: filtrar por dirección del barrido.
- `--sort {name|time}`: orden natural por nombre o por `start_time` del NPZ.
- `--bin-width <μs>`: se reenvía al entrenador base.
- `--load-params`: reutilizar parámetros guardados (omite entrenamiento y regenera salidas rápidamente con nuevos anchos de bin).
- `--extra ...` después de `--`: cualquier flag adicional se reenvía al entrenador base.

### Consejo de escalado de velocidad

Si tu barrido es `N×` más rápido que la línea base, reduce `--bin-width` por el mismo factor (p. ej., línea base `50 ms` -> `10×` más rápido -> `5 ms`: `--bin-width 5000`). Puedes entrenar una vez (p. ej., `5 ms`) y luego usar `--load-params` para regenerar resultados rápidamente a `10 ms` sin reentrenar.

## Gestión de parámetros

El sistema soporta funcionalidad completa de guardado/carga de parámetros.

### Formatos de guardado

- **NPZ**: formato binario para carga rápida.
- **JSON**: legible por humanos con metadatos.
- **CSV**: compatible con Excel para inspección manual.

### Carga de parámetros

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Archivos de parámetros

Los archivos se nombran automáticamente con el recuento de parámetros, por ejemplo: `*_learned_params_n13.*`.

## Optimización de memoria

El sistema usa procesamiento por bloques en todo el flujo:

| Ítem | Detalle |
|---|---|
| Tamaño de bloque | Predeterminado `250000` eventos (configurable) |
| Eficiencia de memoria | Procesa datasets grandes sin desbordar GPU |
| Varianza unificada | Mantiene flujo de gradiente correcto para aprendizaje |
| Seguimiento de progreso | Actualizaciones de procesamiento en tiempo real |

## Estructura de salida

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

## Ejemplos de configuración

### Compensación de alta precisión

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### Procesamiento rápido

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### Memoria restringida

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## Mapeo de longitud de onda

El sistema admite visualización espectral al mapear evolución temporal a longitud de onda:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Rango predeterminado**: $380\text{–}680~\text{nm}$ (configurable).

## Consejos y buenas prácticas

### Selección de parámetros

- **Microstepping**: usa `32×` para movimiento suave (Arduino).
- **Bin Width**: comienza con `50 ms` para optimización y `2 ms` para análisis.
- **Temperatura**: valores altos (alrededor de `5000`) para fronteras más suaves.
- **Suavidad**: `0.001` ofrece buena regularización.

### Gestión de memoria

- **Memoria GPU**: usa procesamiento por bloques con tamaño de bloque adecuado.
- **Conteo de eventos**: se recomienda `> 10^6` eventos para aprendizaje estable.
- **Iteraciones**: `1000` iteraciones suelen ser suficientes.

### Organización de archivos

- Mantén archivos RAW y segmentos en el mismo directorio.
- Los archivos de parámetros se detectan automáticamente por convención de nombre.
- Usa prefijos de nombre descriptivos para mantener salidas ordenadas.

## Notas de desarrollo

- `versions.md` describe eras históricas del proyecto y razones de migración.
- `.githooks/pre-commit` bloquea commits sobredimensionados/binarios y tipos de archivo no código/documentación.
- `scripts/setup_hooks.sh` establece `core.hooksPath` en `.githooks`.
- `archive_code_variants/` almacena variantes antiguas para mantener enfocadas las herramientas de raíz.

Deriva documental conocida (conservada intencionalmente por compatibilidad retroactiva):

- Algunos documentos antiguos mencionan `sync_image_system/` o `dual_camera_gui.py`; el checkout actual contiene `ImagingGUI/DualCamera_separate_transform.py` y directorios SDK.
- `ImagingGUI/README.md` aún menciona `pip install -r requirements.txt`, pero no hay un `requirements.txt` en la raíz en este checkout.
- `firmware/README.md` referencia varias subcarpetas de sketches de Arduino que no están presentes en este checkout.
- `versions.md` menciona nombres de scripts heredados que difieren de los scripts actuales en la raíz.
- `i18n/` existe y actualmente incluye `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md` y `README.ko.md`; los enlaces para idiomas adicionales se conservan como objetivos planificados.

## Solución de problemas

| Síntoma | Causa probable | Acción |
|---|---|---|
| Errores al cargar parámetros | Desajuste en el número de parámetros | Asegura que `--num_params` coincida con el archivo guardado |
| OOM / presión de memoria | Bloque demasiado grande o bins demasiado finos | Reduce `--chunk_size` y/o aumenta `--bin_width` |
| Calidad de compensación débil | Entrenamiento insuficiente o mala segmentación | Aumenta `--iterations`, habilita parámetros entrenables y verifica segmentación |
| No se producen archivos de segmento | Problema de RAW/SDK/flags | Confirma ruta RAW, configuración Metavision y `--segment_events` |
| Se ignoran args del wrapper turbo | Sintaxis de reenvío incorrecta | Pasa args del entrenador después de `--` (o usa `--extra`) |
| Problemas de GUI | Incompatibilidad de Tkinter/backend o SDK | Verifica backend GUI y disponibilidad del SDK de cámara |

- **Errores de carga de parámetros**: asegúrate de que `--num_params` sea compatible con el archivo cargado.
- **OOM / presión de memoria**: reduce `--chunk_size` y/o aumenta `--bin_width`.
- **Calidad de compensación débil**: aumenta `--iterations`, habilita parámetros entrenables (`--a_trainable`, `--b_trainable`, opcionalmente `--boundary_trainable`) y verifica la calidad de segmentación.
- **No se generan archivos de segmento**: confirma ruta RAW, disponibilidad del lector Metavision y que se haya pasado `--segment_events`.
- **Paso de argumentos del wrapper turbo**: coloca los argumentos del entrenador después de `--` (o usa `--extra`).
- **Problemas de GUI**: verifica soporte de backend Tkinter y disponibilidad del SDK de cámara en tu plataforma.

## Hoja de ruta

- Mejorar la reproducibilidad de dependencias/bootstrap (`requirements.txt` o lockfile de entorno).
- Consolidar nombres de scripts heredados y referencias de rutas en la documentación.
- Ampliar esquemas de dataset documentados y convenciones esperadas de campos NPZ.
- Añadir pruebas tipo regresión para segmentación/compensación sobre datos pequeños de prueba.
- Seguir integrando salidas de análisis de calidad de publicación desde pipelines `align_*`.
- Añadir/actualizar los archivos README multilingües restantes en `i18n/` para cubrir completamente los enlaces de idioma de la parte superior.

## Citación

Si este repositorio es útil para tu investigación, cita el preprint de Optica Open:

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

## Agradecimientos

- Preprint de Optica Open y materiales asociados de difusión del proyecto.
- Colaboradores de hardware y software a lo largo de la evolución del repositorio capturada en `versions/` y herramientas archivadas.
- Soporte de la comunidad mediante GitHub Sponsors y canales asociados del proyecto.

## Licencia

Este proyecto se publica bajo la licencia MIT. Consulta [`../LICENSE`](../LICENSE) para más detalles.

## Contribuciones

Las contribuciones son bienvenidas.

- Empieza por el estilo existente de scripts y documentación.
- Mantén ejemplos de línea de comandos reproducibles con rutas del repositorio cuando sea posible.
- Si añades datasets/salidas grandes, asegúrate de respetar las políticas de `.githooks/pre-commit`.

Nota: no existe un `CONTRIBUTING.md` dedicado en este checkout. Si hace falta, abre un issue o envía un PR con el flujo de contribución que propones.

## Soporte / Patrocinio

| Canal | Enlace | Uso |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | Soporte continuo del proyecto |
| Sitio del proyecto | https://lazying.art | Actualizaciones del proyecto y enlaces del ecosistema |
| Chat de la comunidad | https://chat.lazying.art | Discusión comunitaria |
| Página adicional del creador | https://onlyideas.art | Contenido relacionado de creador/investigación |
| Página de compra del kit central | https://lazying.art/openhi-kit.html | Kit inicial de hardware para el flujo OpenHI |
| Código promocional | `OPTICA` | 30% de descuento (como se documenta arriba) |

---

### Notas

- 📌 Este README conserva notas de rutas heredadas cuando la evolución del repositorio introdujo deriva de nombres/diseño.
- 🔒 Si hay incertidumbre sobre referencias antiguas, el texto se conserva intencionalmente en vez de eliminarse.
