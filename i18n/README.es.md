[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

# Imagen Hiperespectral Neuromórfica Auto-Calibrada (OpenHI)

[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#prerrequisitos)
[![Estado](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#resumen-general)
[![Patrocinio](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#mapa-del-repositorio)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#herramientas-adicionales)
[![Paper](https://img.shields.io/badge/Paper-Optica-ff6b6b.svg)](https://doi.org/10.1364/OPTICA.585766)
[![i18n](https://img.shields.io/badge/i18n-10%20translated%20%7C%20English%20base-22c55e.svg)](#internacionalización)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#resumen-general)
[![Inicio rápido](https://img.shields.io/badge/QuickStart-5%20min%20path-16a34a.svg)](#inicio-rápido-ruta-de-5-minutos)
[![BOM](https://img.shields.io/badge/BOM-Core%20module%20available-f59e0b.svg)](#lista-de-materiales-módulo-central)
[![Guía rápida](https://img.shields.io/badge/Guide-QUICKSTART.md-334155.svg)](../QUICKSTART.md)


> [!NOTE]
> Estado de i18n en este checkout: todos los archivos de traducción enlazados están presentes en `i18n/` (`ar`, `de`, `es`, `fr`, `ja`, `ko`, `ru`, `vi`, `zh-Hans`, `zh-Hant`), con el README en inglés como referencia canónica raíz.

Un pipeline integral para reconstruir espectros a partir de cámaras de eventos con iluminación dispersa (por ejemplo, rejilla de difracción). El sistema registra eventos de cambio de intensidad $e = (x, y, t, p)$ donde $p \in \{-1, +1\}$ indica la polaridad del cambio de log-intensidad, e infiere automáticamente el tiempo de escaneo y metadatos de calibración ("auto info") directamente desde el flujo de eventos.

> [!IMPORTANT]
> Este README es la fuente técnica canónica en la raíz del repositorio. Los archivos localizados en `i18n/` deben reflejar la evolución de secciones/encabezados y mantener exactamente una línea de opciones de idioma al inicio (sin barras de idioma duplicadas).

<p align="center">
  <img src="../images/device_setup.png" alt="Configuración del dispositivo" width="24%">
  <img src="../images/data_acquisition_gui.png" alt="GUI de adquisición" width="74%">
</p>

*Izquierda: microscopio de transmisión modular con brazo motorizado de iluminación por rejilla y pila de detección vertical. Derecha: GUI de adquisición de datos usada para monitorizar segmentación, compensación y reconstrucciones en tiempo real.*


## Acceso Rápido

| Necesidad | Ir a |
|---|---|
| Empezar en ~5 minutos | [Inicio Rápido (Ruta de 5 Minutos) ⚡](#inicio-rápido-ruta-de-5-minutos) |
| Ejecutar el wrapper del pipeline completo | [`scripts/run_scan_pipeline.sh`](../scripts/run_scan_pipeline.sh) |
| Entender el flujo de scripts | [Resumen General 🔭](#resumen-general), [Scripts Principales 🧠](#scripts-principales) |
| Ajustar parámetros | [Configuración 🎛️](#configuración), [Ejemplos de Configuración 🧩](#ejemplos-de-configuración) |
| Usar herramientas GUI | [Herramientas Adicionales 🛠️](#herramientas-adicionales) |
| Documentación de hardware (BOM/PCB/3D/Firmware) | [Mapa del Repositorio 🗺️](#mapa-del-repositorio) |
| Reglas de mantenimiento multilingüe | [Internacionalización 🌍](#internacionalización) |
| Enlaces de soporte/patrocinio | [Soporte / Patrocinio 💖](#soporte--patrocinio) |

## De un Vistazo

| Elemento | Detalles |
|---|---|
| Idea central | Imagen derivativa hiperespectral auto-calibrada desde flujos de eventos |
| Etapas principales | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> scripts de visualización |
| Documentación de hardware en el repo | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Herramientas de escritorio | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Artículo canónico | [Artículo de Optica (DOI: 10.1364/OPTICA.585766)](https://doi.org/10.1364/OPTICA.585766) |
| i18n en este checkout | `README.ar.md`, `README.de.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md`, `README.ru.md`, `README.vi.md`, `README.zh-Hans.md`, `README.zh-Hant.md` |

### Resumen de Compatibilidad

| Área | Situación actual del repositorio |
|---|---|
| Base de Python | Se recomienda `3.9+` (algunas utilidades de `ImagingGUI/` indican `3.10+`) |
| Lanzador principal del pipeline | `scripts/run_scan_pipeline.sh` |
| Script principal de entrenamiento | `compensate_multiwindow_train_saved_params.py` |
| Material de hardware | Disponible en `3D/`, `PCB/`, `BOM/`, `firmware/` |
| Documentación multilingüe | `i18n/` contiene los 10 archivos de idioma enlazados |



> [!TIP]
> Compra el kit de desarrollo central (sin incluir cámara, lente tubular ni mesa óptica) para el artículo [Self-calibrated neuromorphic hyperspectral derivative imaging](https://doi.org/10.1364/OPTICA.585766) publicado en Optica:
> - https://lazying.art/openhi-kit.html
> - Código promocional con 30% de descuento: `OPTICA`

## Contenidos

- [Acceso Rápido ⚡](#acceso-rápido)
- [De un Vistazo 📌](#de-un-vistazo)
- [Resumen General 🔭](#resumen-general)
- [Características ✨](#características)
- [Mapa del Repositorio 🗺️](#mapa-del-repositorio)
- [Estructura del Proyecto 📁](#estructura-del-proyecto)
- [Inicio Rápido (Ruta de 5 Minutos) ⚡](#inicio-rápido-ruta-de-5-minutos)
- [Prerrequisitos 🧰](#prerrequisitos)
- [Instalación ⚙️](#instalación)
- [Uso 🚀](#uso)
- [Internacionalización 🌍](#internacionalización)
- [Configuración 🎛️](#configuración)
- [Ejemplos 🧪](#ejemplos)
- [Lista de Materiales (Módulo Central) 🧾](#lista-de-materiales-módulo-central)
- [Scripts Principales 🧠](#scripts-principales)
- [Herramientas Adicionales 🛠️](#herramientas-adicionales)
- [Compensación Turbo Multi-Scan ⚡](#compensación-turbo-multi-scan)
- [Gestión de Parámetros 💾](#gestión-de-parámetros)
- [Optimización de Memoria 🧱](#optimización-de-memoria)
- [Estructura de Salida 📦](#estructura-de-salida)
- [Ejemplos de Configuración 🧩](#ejemplos-de-configuración)
- [Mapeo de Longitud de Onda 🌈](#mapeo-de-longitud-de-onda)
- [Consejos y Buenas Prácticas ✅](#consejos-y-buenas-prácticas)
- [Notas de Desarrollo 🧭](#notas-de-desarrollo)
- [Solución de Problemas 🩺](#solución-de-problemas)
- [Hoja de Ruta 🛣️](#hoja-de-ruta)
- [Cita 📎](#cita)
- [Agradecimientos 🙏](#agradecimientos)
- [Licencia 📄](#licencia)
- [Contribuciones 🤝](#contribuciones)
- [Soporte / Patrocinio 💖](#soporte--patrocinio)

> [!IMPORTANT]
> Política de fuente de contenido canónico para este repositorio: mantener el `README.md` raíz en inglés como referencia técnica y reflejar la evolución de secciones/encabezados en cada variante `i18n/README.*.md` con una única línea de opciones de idioma al inicio.

## Resumen General

Cuando la iluminación barre longitudes de onda a lo largo del tiempo, el flujo de eventos codifica una derivada temporal del espectro subyacente a lo largo del eje de dispersión.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

### Leyenda del Pipeline

| Icono | Significado |
|---|---|
| 🧩 | Segmentación / división de escaneos |
| 🧠 | Compensación / aprendizaje de parámetros |
| 🖼️ | Diagnósticos visuales / inspección de salidas |
| 🌈 | Mapeo de longitud de onda / renderizado espectral |

Este pipeline proporciona tres etapas principales:

| Etapa | Objetivo | Script(s) principal(es) |
|---|---|---|
| 1. Segmentar | Encontrar el tiempo de escaneo y dividir grabaciones en pasadas hacia delante/hacia atrás | `segment_robust_fixed.py` |
| 2. Compensar | Estimar un time-warp lineal por tramos para eliminar la inclinación temporal inducida por el escaneo | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualizar | Superponer límites aprendidos y comparar frames con bins temporales originales vs. compensados | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

El repositorio también incluye recursos de hardware, código de GUI de adquisición y ramas de experimentos archivados en `versions/`.

### Alcance y Suposiciones

- Este repositorio está orientado a investigación e incluye scripts activos más experimentos/resultados archivados.
- Los comandos de este README asumen ejecución desde la raíz del repositorio, salvo que se indique lo contrario.
- Varios flujos opcionales dependen de SDKs externos (Metavision, SDKs de fabricantes de cámaras) y de datasets locales que no se incluyen en este repositorio.
- Si un comando hace referencia a una ruta histórica ausente, prioriza los scripts raíz actualizados listados en este README y conserva las notas heredadas solo para compatibilidad retroactiva.

## Características

- Flujo de trabajo integral de procesamiento de eventos desde RAW hasta espectro.
- Detección automática/manual de periodo de escaneo y segmentación hacia delante/hacia atrás.
- Compensación multi-ventana con modos de parámetros entrenables/fijos.
- Guardado/carga de parámetros en `NPZ`, `JSON` y `CSV`.
- Flujo de combinación multi-scan para iteraciones de entrenamiento más rápidas (`compensate_multiwindow_turbo.py`).
- Suite de visualización para límites, frames con bins, curvas acumulativas y diagnósticos ponderados.
- Documentación de hardware: BOM, PCB, piezas 3D, notas de firmware.
- Utilidades de adquisición para configuraciones sincronizadas de cámaras de eventos/frame.

| Categoría | Capacidades incluidas |
|---|---|
| Procesamiento de señal | Segmentación, detección de periodo, compensación por time-warp |
| Optimización | Parámetros entrenables/fijos, controles de suavidad, entrenamiento por bloques |
| Salidas | Superposiciones visuales, comparativas acumulativas, diagnósticos mapeados por longitud de onda |
| Activos de plataforma | Archivos de diseño de hardware, notas de firmware, herramientas GUI, archivos históricos |

## Mapa del Repositorio

Los recursos clave de hardware se mantienen junto al código para acceso rápido:

| Área | Ruta |
|---|---|
| Piezas impresas en 3D | [`3D/`](../3D/) |
| Diseños de PCB | [`PCB/`](../PCB/) |
| Firmware de microcontrolador | [`firmware/`](../firmware/) |
| Interfaz de adquisición (escritorio) | [`ImagingGUI/`](../ImagingGUI/) |
| Referencias de experimento/datos | [`comparisons/reference_spectrum_2835/`](../comparisons/reference_spectrum_2835/), [`comparisons/reference_spectrum_lumileds/`](../comparisons/reference_spectrum_lumileds/), [`references/`](../references/) |
| Análisis de alineación | [`comparisons/align_background_vs_reference_code/`](../comparisons/align_background_vs_reference_code/), [`comparisons/alignment_configs/`](../comparisons/alignment_configs/) |

## Estructura del Proyecto

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

## Inicio Rápido (Ruta de 5 Minutos)

Si tu entorno ya está preparado y la carpeta del dataset contiene un archivo `*event*.raw`:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

Para forzar un archivo RAW específico:

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

Este wrapper ejecuta segmentación, entrenamiento de compensación y visualización usando rutas de scripts y flags CLI por defecto del repositorio.

> [!TIP]
> Para una primera validación, ejecuta el wrapper sobre un directorio de dataset, y luego inspecciona el NPZ segmentado generado y las salidas de visualización antes de ajustar las variables `PIPELINE_*`.

## Prerrequisitos

- Python 3.9+ (Python 3.10+ para algunas herramientas GUI en `ImagingGUI/`).
- Paquetes Python principales: `numpy`, `torch`, `matplotlib`.
- Opcionales pero comunes: `opencv-python`, `pillow`, `cellpose`, `spectral`.
- Paquete opcional específico de plataforma: `pywin32` (normalmente para flujos de trabajo de SDK de cámara en Windows).
- SDK de Metavision / bindings Python para flujos de lectura RAW de eventos (`simple_raw_reader.py`, segmentación desde RAW).
- Se recomienda PyTorch con CUDA para optimización más rápida.
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
# pip install spectral pywin32
```

Si usas Git hooks para higiene de archivos grandes:

```bash
bash scripts/setup_hooks.sh
```

Recomendado (opcional) para verificaciones de reproducibilidad:

```bash
python -c "import numpy, torch, matplotlib; print('core deps ok')"
python -c "import torch; print('cuda:', torch.cuda.is_available())"
```

## Uso

### Flujo de Trabajo Básico (scripts raíz actuales)

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

### Referencia Comando-a-Salida

| Paso | Punto de entrada del comando | Salida principal |
|---|---|---|
| 🧩 Segmentar escaneos | `segment_robust_fixed.py` | `*_segments/Scan_*_{Forward,Backward}_events.npz` |
| 🧠 Entrenar compensación | `compensate_multiwindow_train_saved_params.py` | `*learned_params_n*.{npz,json,csv}` + diagnósticos visuales |
| 🖼️ Diagnóstico de límites/frames | `visualize_boundaries_and_frames.py` | carpeta de visualización con marca de tiempo, overlays y bins |
| 📈 Diagnóstico acumulativo | `visualize_cumulative_compare.py`, `visualize_cumulative_weighted.py` | gráficas acumulativas/estadísticas para control de calidad del escaneo |
| ⚡ Ejecución completa conveniente | `scripts/run_scan_pipeline.sh` | segmentación + entrenamiento + visualización de extremo a extremo |

### Wrapper de conveniencia de un solo comando

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

### Prueba Rápida Mínima (sin cambios de entrenamiento)

Úsala cuando quieras validar el cableado de scripts sobre un NPZ segmentado existente antes de ejecutar optimizaciones largas:

```bash
# quick visualization pass
python visualize_boundaries_and_frames.py /path/to/Scan_1_Forward_events.npz \
  --sample_rate 0.05 --sensor_width 1280 --sensor_height 720

# quick cumulative diagnostics
python visualize_cumulative_compare.py /path/to/Scan_1_Forward_events.npz \
  --sensor_width 1280 --sensor_height 720
```

Variables de entorno soportadas por `scripts/run_scan_pipeline.sh`:

| Variable | Valor por defecto | Objetivo |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Fracción de ventana de eventos activos |
| `PIPELINE_BIN_WIDTH` | `50000` | Ancho de bin de entrenamiento en microsegundos |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Ancho del sensor para visualización |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Alto del sensor para visualización |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Fracción de muestreo de eventos para gráficas |
| `PIPELINE_TIME_BIN_US` | `1000` | Tamaño del bin de actividad para segmentación |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Patrón de archivo segmentado para scripts posteriores |

### Wrapper orientado a figuras (flujo de publicación)

```bash
scripts/prepare_figure04.sh /path/to/dataset_dir [raw_file]
```

Este wrapper ejecuta segmentación, diagnósticos, compensación y graficado con valores por defecto orientados a figuras.

> [!NOTE]
> En este checkout, `scripts/prepare_figure04.sh` referencia `publication_code/figure02_scan_segmentation.py`, pero el directorio `publication_code/` no está presente. Conserva esta ruta si tu rama local incluye esa carpeta; en caso contrario prioriza `scripts/run_scan_pipeline.sh`.

## Internacionalización

El repositorio usa una única línea de opciones de idioma al inicio de cada README para evitar barras de idioma duplicadas.

Archivos traducidos actualmente disponibles en `i18n/`:

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

### Matriz de Cobertura de Idiomas

| Configuración regional | Archivo | Cobertura |
|---|---|---|
| Árabe | `README.ar.md` | ✅ Presente |
| Alemán | `README.de.md` | ✅ Presente |
| Español | `README.es.md` | ✅ Presente |
| Francés | `README.fr.md` | ✅ Presente |
| Japonés | `README.ja.md` | ✅ Presente |
| Coreano | `README.ko.md` | ✅ Presente |
| Ruso | `README.ru.md` | ✅ Presente |
| Vietnamita | `README.vi.md` | ✅ Presente |
| Chino (Simplificado) | `README.zh-Hans.md` | ✅ Presente |
| Chino (Tradicional) | `README.zh-Hant.md` | ✅ Presente |

| Enlace de idioma en navegación | Archivo en `i18n/` | Estado |
|---|---|---|
| العربية | `README.ar.md` | Disponible |
| Deutsch | `README.de.md` | Disponible |
| Español | `README.es.md` | Disponible |
| Français | `README.fr.md` | Disponible |
| 日本語 | `README.ja.md` | Disponible |
| 한국어 | `README.ko.md` | Disponible |
| Русский | `README.ru.md` | Disponible |
| Tiếng Việt | `README.vi.md` | Disponible |
| 中文 (简体) | `README.zh-Hans.md` | Disponible |
| 中文（繁體） | `README.zh-Hant.md` | Disponible |

Todas las variantes README deben mantener una única línea de opciones de idioma al inicio (sin barras de idioma duplicadas), consistente con `.auto-readme-work/*/language-nav-*.md`.

> [!NOTE]
> Regla de mantenimiento multilingüe para futuras ediciones: actualiza cada archivo de idioma uno por uno tras cambiar secciones raíz, y mantén barras de idioma no duplicadas en cada README localizado.

### Lista de Verificación de Actualización Multilingüe

1. Actualiza primero el `README.md` raíz.
2. Asegura que `i18n/` exista y que los archivos de idioma estén presentes.
3. Actualiza cada `i18n/README.<lang>.md` uno por uno (no copies en lote contenido obsoleto).
4. Mantén una sola línea de opciones de idioma al inicio de cada variante README.
5. Verifica que no haya barras de idioma duplicadas en archivos raíz o localizados.

## Configuración

Controles CLI importantes usados en los scripts:

### Segmentación (`segment_robust_fixed.py`)

- `--time_bin_us`: tamaño del bin de actividad en microsegundos.
- `--round_trip_period`: periodo manual (por defecto `1688` bins).
- `--auto_calculate_period`: periodo por autocorrelación.
- `--activity_fraction`: fracción de ventana de eventos activos.
- `--manual_start_shift_ms`: desplazamiento manual del inicio del escaneo.

### Compensación (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (por defecto `13`), `--temperature` (por defecto `5000`).
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

### Comandos estilo dataset de inicio rápido (de `QUICKSTART.md`)

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

### Comandos auxiliares heredados, conservados de flujos históricos

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

Estos comandos heredados se conservan intencionalmente por contexto de compatibilidad; en este checkout, usa los scripts raíz actuales siempre que sea posible.

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

## Lista de Materiales (Módulo Central)

Consulta [`BOM/core_module.md`](../BOM/core_module.md) para la tabla completa con enlaces y notas.

### Tabla S2. Comparación de Tiempo de Adquisición y Coste Entre el Sistema Propuesto Basado en Eventos y una Cámara Hiperespectral de Referencia

| Parámetro | Nuestro sistema | Cámara de referencia |
|---|---|---|
| Tiempo de adquisición | ∼585 ms por escaneo | 300 s por escaneo |
| Volumen de datos | 18.5 MB | 138 MB |
| Precio aproximado | ∼3000 USD | 14 000 USD |

### Tabla S3. Lista de Materiales para el Módulo Central de Iluminación de Escaneo
(Excluyendo la cámara de eventos y la óptica opcional 4f de validación)

| Componente | Notas | Coste (USD) | Enlace de Taobao |
|---|---|---:|---|
| Control de movimiento | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| Óptica (rejilla) | Rejilla de difracción (grado educativo) | 3.47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPRouNw |
| Iluminación | LED 2835 (6 CNY / 10 uds; 0.6 CNY usado) | 0.08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| Reflector | Espejo plegable | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| Electrónica | PCB LED (CNY/placa; pedido mínimo 5 uds) | 1.67 |  |
| Finales de carrera | Opcional, 2 × 8.07 CNY | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| Impresión 3D | Un tercio de bobina PLA (cubre todas las piezas impresas) | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| Lente | Lente plano-convexa (25.4 mm, AR 350–700 nm) |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| Total | módulo central | **33.99** |  |

## Scripts Principales

### 1. Segmentación: `segment_robust_fixed.py`

**Objetivo**: Extraer el tiempo de escaneo de eventos RAW y dividir en 6 escaneos unidireccionales (F, B, F, B, F, B).

**Descripción Matemática**:

- **Señal de actividad** (eventos agrupados con $\Delta t = 1000~\mu\text{s}$):
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Detección de ventana activa**: encontrar la ventana contigua más pequeña que contiene el $80\%$ de los eventos.

- **Estimación de periodo**: autocorrelación o periodo manual (por defecto: $1688$ bins).

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

- `--segment_events`: Guarda segmentos individuales de escaneo como archivos NPZ.
- `--round_trip_period 1688`: Usa periodo manual (por defecto).
- `--auto_calculate_period`: Sustituye el periodo manual por autocorrelación.
- `--activity_fraction 0.80`: Fracción de eventos para la región activa.
- `--max_iterations 2`: Iteraciones de refinamiento.

### 2. Compensación: `compensate_multiwindow_train_saved_params.py`

**Objetivo**: Aprender parámetros de time-warp para eliminar el cizallamiento temporal inducido por el escaneo usando compensación lineal por tramos multi-ventana.

**Descripción Matemática**:

- **Superficies de frontera**:
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Pertenencias suaves de ventana**:
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Pendientes interpoladas (opcional)**:
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Time warp**:
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Pérdida**: minimización de varianza de frames con bins temporales y regularización de suavidad sobre parámetros.

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

**Argumentos Clave**:

- `--a_trainable` / `--a_fixed`: Controla el entrenamiento de parámetro a (por defecto: fijo).
- `--b_trainable` / `--b_fixed`: Controla el entrenamiento de parámetro b (por defecto: entrenable).
- `--num_params 13`: Número de parámetros de frontera.
- `--temperature 5000`: Temperatura sigmoide para ventanas suaves.
- `--smoothness_weight 0.001`: Peso de regularización.
- `--load_params file.npz`: Carga parámetros guardados.
- `--chunk_size 250000`: Tamaño de bloque de procesamiento eficiente en memoria.

### 3. Visualización: `visualize_boundaries_and_frames.py`

**Objetivo**: Mostrar parámetros aprendidos y enseñar mejoras cualitativas.

**Características**:

- Superposiciones de parámetros en proyecciones $x\text{–}t$ y $y\text{–}t$.
- Comparativas de frames con bins temporales (original vs. compensado).
- Análisis de ventana deslizante (bins de 50 ms y 2 ms).
- Mapeo de longitud de onda para visualización espectral.

**Uso**:

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Comparación Acumulativa: `visualize_cumulative_compare.py`

**Objetivo**: Comparar medias acumulativas en pasos de 2 ms con medias por bins deslizantes.

**Descripción Matemática**:

- **Medias acumulativas**:
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Medias deslizantes**: conteo de eventos en $[T-\Delta,\,T)$ dividido por $H \times W$.

- **Relación** (derivada por diferencia finita):
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Uso**:

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Herramientas Adicionales

### Aplicación GUI: `scan_compensation_gui_cloud.py`

GUI completa para compensación de escaneo con visualización espectral 3D.

**Características**:

- Ajuste interactivo de parámetros.
- Progreso de optimización en tiempo real.
- Visualización 3D mapeada por longitud de onda.
- Exportación de resultados y parámetros.

**Uso**:

```bash
python scan_compensation_gui_cloud.py
```

### Sistema de Doble Cámara (ruta actual)

Sistema de grabación sincronizada para cámaras de eventos y de frames:

- `ImagingGUI/DualCamera_separate_transform.py`

**Características**:

- Grabación simultánea de eventos y frames.
- Vista previa en tiempo real con transformaciones.
- Controles de ventana siempre en primer plano.
- Ajuste de parámetros durante la grabación.

### Utilidades ENVI hiperespectrales

Scripts del repositorio para visualización de cubos ENVI, extracción ROI y preprocesado de visualización:

- `show_envi_spectrum_gui.py`
- `scripts/hs_to_rgb.py`
- `scripts/envi_export_frames.py`
- `scripts/envi_crop_by_roi.py`
- `scripts/hs_gradient_wavelength.py`
- `scripts/cellpose_roi.py`
- `scripts/cellpose_simple_mask.py`
- `scripts/roi_template_match.py`

Punto de entrada típico:

```bash
python show_envi_spectrum_gui.py
```

### Control de Motor Arduino (referencia de ruta heredada conservada)

El README original referenciaba esta ruta de sketch de firmware:

- `rotor/step42_with_key_int/step42_with_key_int.ino`

La estructura actual del repositorio incluye notas de firmware en:

- `firmware/README.md`

Esta discrepancia de rutas se conserva aquí de forma intencional; si tienes carpetas de sketch rotor en otra rama/checkout local, continúa usando esas rutas.

Las capacidades heredadas documentadas de este sketch incluyen:

- Control preciso de ángulo con microstepping.
- Perfiles de aceleración/desaceleración.
- Integración de finales de carrera.
- Funcionalidad de autocentrado.

## Compensación Turbo Multi-Scan

Cuando tienes múltiples escaneos unidireccionales (Forward/Backward) del mismo barrido, puedes fusionarlos y ejecutar el entrenador probado sobre un único flujo de eventos combinado usando `compensate_multiwindow_turbo.py`.

### Qué hace

- Acepta un segmento, una lista explícita o un directorio completo de segmentos.
- Para escaneos Backward, invierte polaridad y revierte tiempo antes de fusionar:
- Si la polaridad `p ∈ {0,1}`: `p := 1 − p`; luego invierte el tiempo dentro del escaneo.
- Si la polaridad `p ∈ {−1,1}`: `p := −p`; luego invierte el tiempo dentro del escaneo.
- Concatena escaneos en una línea de tiempo continua (con una separación de `1 μs` entre escaneos) y llama internamente a `compensate_multiwindow_train_saved_params.py`.

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

- `--segment`, `--segments`, `--segments-dir`: elige tu conjunto de entrada.
- `--include {all|forward|backward}`: filtra por dirección del escaneo.
- `--sort {name|time}`: orden natural por nombre de archivo o por `start_time` del NPZ.
- `--bin-width <μs>`: se reenvía al entrenador base.
- `--load-params`: reutiliza parámetros guardados (omite entrenamiento y regenera salidas rápido con nuevos anchos de bin).
- `--extra ...` después de `--`: cualquier flag adicional se reenvía al entrenador base.

### Consejo de escalado de velocidad

Si tu escaneo es `N×` más rápido que la línea base, reduce `--bin-width` por el mismo factor (por ejemplo, línea base `50 ms` -> `10×` más rápido -> `5 ms`: `--bin-width 5000`). Puedes entrenar una vez (por ejemplo, `5 ms`) y luego usar `--load-params` para regenerar rápidamente resultados a `10 ms` sin reentrenar.

## Gestión de Parámetros

El sistema soporta funcionalidad completa de guardado/carga de parámetros.

### Formatos de Guardado

- **NPZ**: Formato binario para carga rápida.
- **JSON**: Legible por humanos con metadatos.
- **CSV**: Compatible con Excel para inspección manual.

### Carga de Parámetros

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz

# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Archivos de Parámetros

Los archivos se nombran automáticamente con el número de parámetros, por ejemplo: `*_learned_params_n13.*`.

## Optimización de Memoria

El sistema usa procesamiento por bloques de forma transversal:

| Elemento | Detalle |
|---|---|
| Tamaño de bloque | `250000` eventos por defecto (configurable) |
| Eficiente en memoria | Procesa datasets grandes sin desbordar la GPU |
| Varianza unificada | Mantiene flujo de gradiente correcto para aprendizaje |
| Seguimiento de progreso | Actualizaciones de procesamiento en tiempo real |

## Estructura de Salida

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

### Artefactos Generados Típicos

| Patrón de artefacto | Producido por | Por qué importa |
|---|---|---|
| `*_segments/Scan_*_events.npz` | Segmentación | Entradas canónicas por escaneo para entrenamiento/visualización |
| `*learned_params_n13.npz` (y `.json`, `.csv`) | Entrenador de compensación | Reutilización de parámetros, reproducibilidad e inspección |
| `visualization_YYYYmmdd_HHMMSS/` | Scripts de visualización / modo visual del entrenador | Mantiene salidas de ejecución aisladas por marca de tiempo |
| `events_with_params.png` y gráficas frame/acumulativas | Scripts de visualización | Validación cualitativa de efectos de compensación |

## Ejemplos de Configuración

### Compensación de Alta Precisión

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### Procesamiento Rápido

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### Memoria Limitada

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## Mapeo de Longitud de Onda

El sistema soporta visualización espectral mapeando evolución temporal a longitud de onda:

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Rango por Defecto**: $380\text{–}680~\text{nm}$ (configurable).

## Consejos y Buenas Prácticas

### Selección de Parámetros

- **Microstepping**: Usa `32×` para movimiento suave (Arduino).
- **Ancho de Bin**: Comienza con `50 ms` para optimización, `2 ms` para análisis.
- **Temperatura**: Valores altos (alrededor de `5000`) para fronteras más suaves.
- **Suavidad**: `0.001` proporciona buena regularización.

### Gestión de Memoria

- **Memoria GPU**: Usa procesamiento por bloques con tamaño de bloque apropiado.
- **Conteo de Eventos**: Se recomienda `> 10^6` eventos para aprendizaje estable.
- **Iteraciones**: `1000` iteraciones suelen ser suficientes.

### Organización de Archivos

- Mantén archivos RAW y segmentos en el mismo directorio.
- Los archivos de parámetros se detectan automáticamente por convención de nombres.
- Usa prefijos de nombre descriptivos para una salida organizada.

## Notas de Desarrollo

- `versions.md` describe eras históricas del proyecto y la justificación de migraciones.
- `.githooks/pre-commit` bloquea commits sobredimensionados/binarios y tipos de archivo no código/documentación.
- `scripts/setup_hooks.sh` establece `core.hooksPath` a `.githooks`.
- `versions/05_archive_code_variants/` almacena variantes antiguas de scripts para mantener enfocado el tooling de nivel raíz.

### Notas de Flujo para Desarrolladores

- Prioriza `scripts/run_scan_pipeline.sh` para ejecuciones base reproducibles y luego pasa a ajuste por script.
- Trata las rutas bajo `comparisons/` como `outputs_root/`, `reference_*` y `align_*` como espacios mixtos de análisis/histórico; evita asumir que son fixtures de prueba mínimos.
- Al agregar scripts nuevos, mantén los entrypoints raíz detectables desde este README y enlaza documentación relacionada (`QUICKSTART.md`, READMEs de submódulos).

Deriva conocida de documentación (conservada intencionalmente para contexto de compatibilidad retroactiva):

- Algunos documentos antiguos mencionan `sync_image_system/` o `dual_camera_gui.py`; el checkout actual contiene `ImagingGUI/DualCamera_separate_transform.py` y directorios SDK.
- `ImagingGUI/README.md` aún referencia `pip install -r requirements.txt`, pero no hay `requirements.txt` en la raíz en este checkout.
- `firmware/README.md` referencia varias subcarpetas de sketches Arduino que no están presentes en este checkout.
- `versions.md` menciona nombres de scripts heredados que difieren de los nombres de scripts actuales en raíz.
- `i18n/` actualmente incluye todos los archivos enlazados en la barra de idioma (`ar`, `de`, `es`, `fr`, `ja`, `ko`, `ru`, `vi`, `zh-Hans`, `zh-Hant`); mantén sincronizados archivos raíz y traducidos al editar encabezados/secciones.

## Solución de Problemas

| Síntoma | Causa probable | Acción |
|---|---|---|
| Errores de carga de parámetros | Incompatibilidad en conteo de parámetros | Asegura que `--num_params` coincida con el archivo guardado |
| OOM / presión de memoria | Bloque demasiado grande o bins demasiado finos | Reduce `--chunk_size` y/o incrementa `--bin_width` |
| Calidad de compensación débil | Entrenamiento insuficiente o mala segmentación | Incrementa `--iterations`, habilita parámetros entrenables, verifica segmentación |
| No se generan archivos segmentados | Problema de RAW/SDK/flag | Confirma ruta RAW, configuración de Metavision y `--segment_events` |
| Argumentos del wrapper turbo ignorados | Sintaxis de reenvío incorrecta | Pasa argumentos del entrenador después de `--` (o usa `--extra`) |
| Problemas de GUI | Incompatibilidad Tkinter/backend o SDK | Verifica backend GUI y disponibilidad del SDK de cámara |

Lista ampliada de solución de problemas (conservada para escaneo rápido):

- **Errores de carga de parámetros**: Asegura que `--num_params` sea compatible con el archivo de parámetros cargado.
- **OOM / presión de memoria**: Reduce `--chunk_size` y/o incrementa `--bin_width`.
- **Calidad de compensación débil**: Incrementa `--iterations`, habilita parámetros entrenables (`--a_trainable`, `--b_trainable`, opcionalmente `--boundary_trainable`) y verifica la calidad de segmentación.
- **No se generan archivos segmentados**: Confirma ruta RAW, disponibilidad del lector Metavision y que se pasó `--segment_events`.
- **Paso de argumentos del wrapper turbo**: Coloca los argumentos del entrenador después de `--` (o usa `--extra`).
- **Problemas de GUI**: Verifica soporte de backend Tkinter y disponibilidad del SDK de cámara en tu plataforma.

## Hoja de Ruta

- Mejorar reproducibilidad de dependencias/bootstrap (`requirements.txt` o lockfile de entorno).
- Consolidar nombres de scripts heredados y referencias de rutas en toda la documentación.
- Expandir esquemas de dataset documentados y convenciones esperadas de campos NPZ.
- Añadir pruebas tipo regresión para segmentación/compensación con datos fixture pequeños.
- Continuar integrando salidas de análisis con calidad de publicación desde pipelines `align_*`.
- Mantener sincronizados el README raíz y todas las variantes existentes `i18n/README.*.md` a medida que evolucionen las secciones.

## Cita

Si este repositorio te resulta útil en tu investigación, por favor cita el artículo de Optica:

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

## Agradecimientos

- Artículo publicado en Optica y materiales de difusión asociados al proyecto.
- Colaboradores de hardware y software a lo largo de la evolución del repositorio capturada en `versions/` y tooling archivado.
- Apoyo de la comunidad mediante GitHub Sponsors y canales asociados al proyecto.

## Licencia

Este proyecto se publica bajo la Licencia MIT. Consulta [`LICENSE`](../LICENSE) para más detalles.

## Contribuciones

Las contribuciones son bienvenidas.

- Empieza por los scripts existentes y el estilo de documentación actual.
- Mantén ejemplos de línea de comandos reproducibles con rutas del repositorio cuando sea posible.
- Si agregas datasets/salidas grandes, asegúrate de respetar las políticas de `.githooks/pre-commit`.

Nota: no hay un `CONTRIBUTING.md` dedicado en este checkout. Si hace falta, abre un issue o envía un PR con el flujo de contribución que propones.

## Soporte / Patrocinio

| Canal | Enlace | Uso |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | Soporte continuo del proyecto |
| Sitio del proyecto | https://lazying.art | Actualizaciones del proyecto y enlaces del ecosistema |
| Chat comunitario | https://chat.lazying.art | Discusión en comunidad |
| Página adicional del creador | https://onlyideas.art | Contenido relacionado de creador/investigación |
| Página de compra del kit central | https://lazying.art/openhi-kit.html | Kit inicial de hardware para flujo OpenHI |
| Código promocional | `OPTICA` | 30% de descuento (como se documentó arriba) |

### Alcance del Soporte

| Tipo de soporte | Mejor canal |
|---|---|
| Financiación y sostenibilidad | GitHub Sponsors |
| Ecosistema de construcción/compra | Página del kit OpenHI en `lazying.art` |
| Solución comunitaria de problemas | `chat.lazying.art` |
| Actualizaciones generales del proyecto | `lazying.art` y páginas del creador |

---

### Notas

- 📌 Este README conserva notas de rutas heredadas donde la evolución del repositorio introdujo deriva de nombres/diseño.
- 🔒 Si hay dudas sobre referencias antiguas, el texto se conserva intencionalmente en lugar de eliminarse.
