[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


# Imagerie hyperspectrale neuromorphique auto-calibrée (OpenHI)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#prérequis)
[![Status](https://img.shields.io/badge/Status-Research%20Pipeline-informational.svg)](#vue-densemble)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink.svg)](https://github.com/sponsors/lachlanchen)
[![Hardware](https://img.shields.io/badge/Hardware-3D%20%7C%20PCB%20%7C%20Firmware-success.svg)](#cartographie-du-dépôt)
[![GUI](https://img.shields.io/badge/GUI-Imaging%20Tools-0ea5e9.svg)](#outils-supplémentaires)
[![Paper](https://img.shields.io/badge/Preprint-Optica%20Open-ff6b6b.svg)](https://doi.org/10.1364/opticaopen.30739151)
[![i18n](https://img.shields.io/badge/i18n-5%20ready%20%7C%206%20planned-22c55e.svg)](#internationalisation)
[![Pipeline](https://img.shields.io/badge/Pipeline-Segment%20%E2%86%92%20Compensate%20%E2%86%92%20Visualize-0ea5e9.svg)](#vue-densemble)

> [!NOTE]
> Statut i18n dans ce checkout : `ar`, `es`, `fr`, `ja`, `ko` sont présents sous `i18n/`. Les liens vers des langues supplémentaires sont conservés pour compatibilité avec la couverture de traduction prévue.

Un pipeline complet pour reconstruire des spectres à partir de caméras événementielles avec illumination dispersée (p. ex. réseau de diffraction). Le système enregistre des événements de variation d'intensité $e = (x, y, t, p)$ où $p \in \{-1, +1\}$ indique la polarité de variation de log-intensité, et infère automatiquement la temporalité du balayage et les métadonnées de calibration (« auto info ») directement à partir du flux d'événements.

## En bref

| Élément | Détails |
|---|---|
| Idée centrale | Imagerie dérivée hyperspectrale auto-calibrée à partir de flux d'événements |
| Étapes principales | `segment_robust_fixed.py` -> `compensate_multiwindow_train_saved_params.py` -> scripts de visualisation |
| Documentation matérielle dans le dépôt | `3D/`, `PCB/`, `firmware/`, `BOM/` |
| Outils desktop | `scan_compensation_gui_cloud.py`, `ImagingGUI/DualCamera_separate_transform.py` |
| Article canonique | [Prépublication Optica Open (DOI: 10.1364/opticaopen.30739151)](https://doi.org/10.1364/opticaopen.30739151) |
| i18n dans ce checkout | `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md`, `README.ko.md` |

<p align="center">
  <img src="images/device_setup.png" alt="Device setup" width="24%">
  <img src="images/data_acquisition_gui.png" alt="Acquisition GUI" width="74%">
</p>

*Gauche : microscope de transmission modulaire avec bras d'illumination par réseau motorisé et pile de détection verticale. Droite : interface d'acquisition utilisée pour surveiller en temps réel la segmentation, la compensation et les reconstructions.*

> [!TIP]
> Achetez le kit de développement principal (hors caméra, lentille tube et table optique) pour l'article [Self-calibrated neuromorphic hyperspectral imaging](https://doi.org/10.1364/opticaopen.30739151) prépublié sur Optica Open :
> - https://lazying.art/openhi-kit.html
> - Code promotionnel pour -30 % : `OPTICA`

## Sommaire

- [En bref 📌](#en-bref)
- [Vue d'ensemble 🔭](#vue-densemble)
- [Fonctionnalités ✨](#fonctionnalités)
- [Cartographie du dépôt 🗺️](#cartographie-du-dépôt)
- [Structure du projet 📁](#structure-du-projet)
- [Démarrage rapide (5 min) ⚡](#démarrage-rapide-5-min)
- [Prérequis 🧰](#prérequis)
- [Installation ⚙️](#installation)
- [Utilisation 🚀](#utilisation)
- [Internationalisation 🌍](#internationalisation)
- [Configuration 🎛️](#configuration)
- [Exemples 🧪](#exemples)
- [Nomenclature (module principal) 🧾](#nomenclature-module-principal)
- [Scripts principaux 🧠](#scripts-principaux)
- [Outils supplémentaires 🛠️](#outils-supplémentaires)
- [Compensation Turbo multi-scan ⚡](#compensation-turbo-multi-scan)
- [Gestion des paramètres 💾](#gestion-des-paramètres)
- [Optimisation mémoire 🧱](#optimisation-mémoire)
- [Structure de sortie 📦](#structure-de-sortie)
- [Exemples de configuration 🧩](#exemples-de-configuration)
- [Correspondance longueur d'onde 🌈](#correspondance-longueur-donde)
- [Conseils et bonnes pratiques ✅](#conseils-et-bonnes-pratiques)
- [Notes de développement 🧭](#notes-de-développement)
- [Dépannage 🩺](#dépannage)
- [Feuille de route 🛣️](#feuille-de-route)
- [Citation 📎](#citation)
- [Remerciements 🙏](#remerciements)
- [Licence 📄](#licence)
- [Contribuer 🤝](#contribuer)
- [Support / Sponsor 💖](#support--sponsor)

## Vue d'ensemble

Quand l'illumination balaie les longueurs d'onde dans le temps, le flux d'événements encode une dérivée temporelle du spectre sous-jacent le long de l'axe de dispersion.

```text
RAW event recording
   -> scan timing segmentation (F/B passes)
   -> multi-window time-warp compensation
   -> frame/cumulative/wavelength diagnostics
```

Ce pipeline fournit trois étapes principales :

| Étape | But | Script(s) principal(aux) |
|---|---|---|
| 1. Segment | Détecter la temporalité du scan et découper les enregistrements en passages aller/retour | `segment_robust_fixed.py` |
| 2. Compensate | Estimer un warping temporel affine par morceaux pour supprimer l'inclinaison temporelle induite par le scan | `compensate_multiwindow_train_saved_params.py` |
| 3. Visualize | Superposer les frontières apprises et comparer les trames binées originales vs compensées | `visualize_boundaries_and_frames.py`, `visualize_cumulative_compare.py` |

Le dépôt inclut aussi les ressources matérielles, le code d'interface d'acquisition et des branches d'expériences archivées sous `versions/`.

## Fonctionnalités

- Workflow de traitement événementiel de bout en bout, de RAW vers spectre.
- Détection auto/manuelle de période de scan et segmentation avant/arrière.
- Compensation multi-fenêtre avec modes paramètres entraînables/fixes.
- Sauvegarde/chargement des paramètres en `NPZ`, `JSON` et `CSV`.
- Workflow de fusion multi-scan pour accélérer les itérations d'entraînement (`compensate_multiwindow_turbo.py`).
- Suite de visualisation pour frontières, trames binées, courbes cumulées et diagnostics pondérés.
- Documentation matérielle : BOM, PCB, pièces 3D, notes firmware.
- Utilitaires d'acquisition pour configurations synchronisées caméra événementielle/caméra image.

| Catégorie | Capacités incluses |
|---|---|
| Traitement du signal | Segmentation, détection de période, compensation de warping temporel |
| Optimisation | Paramètres entraînables/fixes, contrôles de lissage, entraînement par chunks |
| Sorties | Superpositions visuelles, comparaisons cumulées, diagnostics avec mappage spectral |
| Ressources plateforme | Fichiers de conception matérielle, notes firmware, outils GUI, archives historiques |

## Cartographie du dépôt

Les ressources matérielles clés sont conservées avec le code pour un accès rapide :

| Zone | Chemin |
|---|---|
| Pièces imprimées en 3D | [`3D/`](3D/) |
| Cartes PCB | [`PCB/`](PCB/) |
| Firmware microcontrôleur | [`firmware/`](firmware/) |
| Interface d'acquisition (desktop) | [`ImagingGUI/`](ImagingGUI/) |
| Références expérience/données | [`reference_spectrum_2835/`](reference_spectrum_2835/), [`reference_spectrum_lumileds/`](reference_spectrum_lumileds/), [`references/`](references/) |
| Analyse d'alignement | [`align_background_vs_reference_code/`](align_background_vs_reference_code/), [`align_data_vs_filter_code/`](align_data_vs_filter_code/) |

## Structure du projet

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

## Démarrage rapide (5 min)

Si votre environnement est déjà prêt et que votre dossier de dataset contient un fichier `*event*.raw` :

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir
```

Pour forcer un fichier RAW spécifique :

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir /path/to/recording_event.raw
```

Ce wrapper exécute segmentation, entraînement de compensation et visualisation avec les chemins de scripts et flags CLI par défaut du dépôt.

> [!TIP]
> Pour une première validation, lancez le wrapper sur un dossier de dataset, puis inspectez le NPZ de segment généré et les sorties de visualisation avant d'ajuster les variables `PIPELINE_*`.

## Prérequis

- Python 3.9+ (Python 3.10+ pour certains outils GUI sous `ImagingGUI/`).
- Packages Python de base : `numpy`, `torch`, `matplotlib`.
- Optionnels mais courants : `opencv-python`, `pillow`, `cellpose`.
- Metavision SDK / bindings Python pour les workflows de lecture RAW (`simple_raw_reader.py`, segmentation depuis RAW).
- PyTorch avec CUDA recommandé pour une optimisation plus rapide.
- Enregistrements RAW et/ou fichiers NPZ segmentés disponibles localement.

## Installation

Aucun fichier d'environnement verrouillé n'est actuellement fourni à la racine du dépôt. Configuration suggérée :

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

Si vous utilisez des hooks Git pour l'hygiène des gros fichiers :

```bash
bash scripts/setup_hooks.sh
```

## Utilisation

### Workflow de base (scripts actuels à la racine)

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

### Wrapper pratique en une commande

```bash
scripts/run_scan_pipeline.sh /path/to/dataset_dir [raw_file]
```

Variables d'environnement prises en charge par `scripts/run_scan_pipeline.sh` :

| Variable | Défaut | But |
|---|---:|---|
| `PIPELINE_ACTIVITY_FRACTION` | `0.90` | Fraction de fenêtre d'événements actifs |
| `PIPELINE_BIN_WIDTH` | `50000` | Largeur de bin d'entraînement en microsecondes |
| `PIPELINE_SENSOR_WIDTH` | `1280` | Largeur capteur pour visualisation |
| `PIPELINE_SENSOR_HEIGHT` | `720` | Hauteur capteur pour visualisation |
| `PIPELINE_SAMPLE_RATE` | `0.10` | Fraction d'échantillonnage d'événements pour tracé |
| `PIPELINE_TIME_BIN_US` | `1000` | Taille de bin d'activité pour segmentation |
| `PIPELINE_SEGMENT_PATTERN` | `Scan_1_Forward_events.npz` | Motif de fichier segment pour scripts aval |

## Internationalisation

Le dépôt utilise une seule ligne d'options de langue en haut de chaque README afin d'éviter les barres de langue dupliquées.

Fichiers traduits actuellement disponibles dans `i18n/` :

- `README.ar.md`
- `README.es.md`
- `README.fr.md`
- `README.ja.md`
- `README.ko.md`

| Lien de langue dans la navigation | Fichier dans `i18n/` | Statut |
|---|---|---|

Les liens de langues prévues sont volontairement conservés dans la navigation supérieure pour compatibilité future.

## Configuration

Contrôles CLI importants utilisés à travers les scripts :

### Segmentation (`segment_robust_fixed.py`)

- `--time_bin_us` : taille de bin d'activité en microsecondes.
- `--round_trip_period` : période manuelle (défaut `1688` bins).
- `--auto_calculate_period` : période via autocorrélation.
- `--activity_fraction` : fraction de fenêtre d'événements actifs.
- `--manual_start_shift_ms` : décalage manuel du départ de scan.

### Compensation (`compensate_multiwindow_train_saved_params.py`)

- `--num_params` (défaut `13`), `--temperature` (défaut `5000`).
- `--a_trainable` / `--a_fixed`, `--b_trainable` / `--b_fixed`, `--boundary_trainable`.
- `--a_default`, `--b_default`.
- `--iterations`, `--learning_rate`, `--smoothness_weight`.
- `--chunk_size` pour le contrôle mémoire.
- `--load_params` pour réutiliser des paramètres appris.

### Visualisation

- `visualize_boundaries_and_frames.py` : `--sample_rate`, `--wavelength_min`, `--wavelength_max`, arguments de taille capteur.
- `visualize_cumulative_compare.py` : taille capteur, `--output_dir`, `--sample_label`.
- `visualize_cumulative_weighted.py` : échelles de polarité, `--step_us`, `--auto_scale`, `--exp`, `--no_comp`.

## Exemples

### Commandes style dataset en démarrage rapide (depuis `QUICKSTART.md`)

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

### Commandes d'aide legacy conservées depuis des workflows historiques

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

Ces commandes legacy sont volontairement conservées pour le contexte de compatibilité ; dans ce checkout, utilisez les scripts actuels à la racine quand c'est possible.

### Entraînement Turbo multi-scan

```bash
python compensate_multiwindow_turbo.py \
  --segments-dir path/to/your_segments \
  --include all --sort name \
  --bin-width 5000 \
  -- --a_trainable --iterations 1000 --smoothness_weight 0.001 --chunk_size 250000 --visualize --plot_params
```

### Réutiliser des paramètres appris (sans réentraînement)

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

## Nomenclature (module principal)

Voir [`BOM/core_module.md`](BOM/core_module.md) pour le tableau complet avec liens et notes.

### Tableau S2. Comparaison du temps d'acquisition et du coût entre le système événementiel proposé et une caméra hyperspectrale de référence

| Paramètre | Notre système | Caméra de référence |
|---|---|---|
| Temps d'acquisition | ∼585 ms par scan | 300 s par scan |
| Volume de données | 18.5 MB | 138 MB |
| Prix approximatif | ∼3000 USD | 14 000 USD |

### Tableau S3. Nomenclature du module principal d'illumination de balayage
(Hors caméra événementielle et optiques de validation 4f optionnelles)

| Composant | Notes | Coût (USD) | Lien Taobao |
|---|---|---:|---|
| Contrôle de mouvement | NEMA42 + TB6600 + Arduino Uno | 15.00 | https://e.tb.cn/h.7FHgkEvoo6tpKTo?tk=QYRFUPRqazE |
| Optique (réseau) | Réseau de diffraction (niveau éducation) | 3.47 | https://e.tb.cn/h.7Fhj16MkrSDHNnE?tk=3Q8dUPRouNw |
| Illumination | LED 2835 (6 CNY / 10 pcs ; 0.6 CNY utilisé) | 0.08 | https://e.tb.cn/h.7uubHIVL5diILHl?tk=tzTAUPRr14K |
| Réflecteur | Miroir pliant | 6.25 | https://e.tb.cn/h.7uu1rNNSbgVdS31?tk=PqsxUPRHb32 |
| Électronique | LED PCB (CNY/carte ; commande min 5 pcs) | 1.67 |  |
| Interrupteurs de fin de course | Optionnel, 2 × 8.07 CNY | 2.24 | https://e.tb.cn/h.7FHEKbcgJmc2Ll1?tk=I4FRUP8diRE |
| Impression 3D | Un tiers de bobine PLA (couvre toutes les pièces imprimées) | 5.09 | https://e.tb.cn/h.7FhOVWX7SLHvNNf?tk=kOcQUPRJsbo |
| Lentille | Lentille plan-convexe (25.4 mm, AR 350–700 nm) |  | https://e.tb.cn/h.7FSePNYhqt7ITbh?tk=tH8ZUP8i3cC |
| Total | module principal | **33.99** |  |

## Scripts principaux

### 1. Segmentation : `segment_robust_fixed.py`

**Objectif** : extraire la temporalité du scan depuis les événements bruts et découper en 6 scans unidirectionnels (F, B, F, B, F, B).

**Description mathématique** :

- **Signal d'activité** (événements binnés avec $\Delta t = 1000~\mu\text{s}$) :
  $$a[n] = \left|\{ i \mid t_{\min} + n\Delta t \le t_i < t_{\min} + (n+1)\Delta t \}\right|.$$

- **Détection de fenêtre active** : trouver la plus petite fenêtre contiguë contenant $80\%$ des événements.

- **Estimation de période** : autocorrélation ou période manuelle (défaut : $1688$ bins).

- **Corrélation inverse** (structure temporelle) :
  $$R[k] = \sum_{n} a[n]\, a_{\text{rev}}[n+k]$$
  avec
  $$a_{\text{rev}}[n] = a[N-1-n].$$

**Utilisation** :

```bash
# Automatic period detection
python segment_robust_fixed.py recording.raw --segment_events --output_dir segments/

# Manual period (fixed 1688 bins)
python segment_robust_fixed.py recording.raw --segment_events --round_trip_period 1688
```

**Arguments** :

- `--segment_events` : sauvegarder les segments de scan individuels en fichiers NPZ.
- `--round_trip_period 1688` : utiliser une période manuelle (par défaut).
- `--auto_calculate_period` : remplacer la période manuelle par l'autocorrélation.
- `--activity_fraction 0.80` : fraction d'événements pour la région active.
- `--max_iterations 2` : itérations de raffinement.

### 2. Compensation : `compensate_multiwindow_train_saved_params.py`

**Objectif** : apprendre des paramètres de warping temporel pour supprimer le cisaillement temporel induit par le scan via une compensation multi-fenêtre affine par morceaux.

**Description mathématique** :

- **Surfaces frontières** :
  $$T_i(x, y) = a_i x + b_i y + c_i,\quad i=0,\ldots,M-1.$$

- **Appartenances de fenêtre soft** :
  $$m_i = \sigma\!\Big(\frac{t - T_i}{\tau}\Big)\,\sigma\!\Big(\frac{T_{i+1} - t}{\tau}\Big),\qquad w_i = \frac{m_i}{\sum_j m_j + \varepsilon}.$$

- **Pentes interpolées (optionnel)** :
  $$\alpha_i = \frac{t - T_i}{T_{i+1} - T_i},\quad a_i' = (1-\alpha_i)a_i + \alpha_i a_{i+1},\quad b_i' = (1-\alpha_i)b_i + \alpha_i b_{i+1}.$$

- **Warping temporel** :
  $$\Delta t(x,y,t) = \sum_i w_i (\tilde{a}_i x + \tilde{b}_i y),\qquad t' = t - \Delta t(x,y,t).$$

- **Loss** : minimisation de variance des trames binnées dans le temps avec régularisation de lissage sur les paramètres.

**Utilisation** :

```bash
# Train with a-parameters trainable, b fixed
python compensate_multiwindow_train_saved_params.py segment.npz \
  --bin_width 50000 --a_trainable --b_default -76.0 \
  --iterations 1000 --smoothness_weight 0.001

# Load pre-trained parameters
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
```

**Arguments clés** :

- `--a_trainable` / `--a_fixed` : contrôle de l'entraînement des paramètres a (défaut : fixe).
- `--b_trainable` / `--b_fixed` : contrôle de l'entraînement des paramètres b (défaut : entraînable).
- `--num_params 13` : nombre de paramètres frontière.
- `--temperature 5000` : température sigmoid pour fenêtres soft.
- `--smoothness_weight 0.001` : poids de régularisation.
- `--load_params file.npz` : charger des paramètres sauvegardés.
- `--chunk_size 250000` : taille de chunk pour traitement efficace en mémoire.

### 3. Visualisation : `visualize_boundaries_and_frames.py`

**Objectif** : afficher les paramètres appris et montrer les améliorations qualitatives.

**Fonctionnalités** :

- Superpositions de paramètres sur projections $x\text{–}t$ et $y\text{–}t$.
- Comparaisons de trames binnées dans le temps (original vs compensé).
- Analyse par fenêtre glissante (bins de 50 ms et 2 ms).
- Correspondance longueur d'onde pour visualisation spectrale.

**Utilisation** :

```bash
python visualize_boundaries_and_frames.py segment.npz \
  --sample_rate 0.1 --wavelength_min 380 --wavelength_max 680
```

### 4. Comparaison cumulative : `visualize_cumulative_compare.py`

**Objectif** : comparer les moyennes cumulées par pas de 2 ms avec les moyennes en fenêtre glissante.

**Description mathématique** :

- **Moyennes cumulées** :
  $$F(T) = \frac{1}{HW}\sum_{t < T}\text{events}(t).$$

- **Moyennes glissantes** : comptes d'événements dans $[T-\Delta,\,T)$ divisés par $H \times W$.

- **Relation** (dérivée en différences finies) :
  $$\Delta F(T) \approx \frac{F(T) - F(T-\Delta)}{\Delta}.$$

**Utilisation** :

```bash
python visualize_cumulative_compare.py segment.npz \
  --sensor_width 1280 --sensor_height 720 \
  --sample_label "My Dataset"
```

## Outils supplémentaires

### Application GUI : `scan_compensation_gui_cloud.py`

GUI complète pour la compensation de scan avec visualisation spectrale 3D.

**Fonctionnalités** :

- Réglage interactif des paramètres.
- Progression d'optimisation en temps réel.
- Visualisation 3D avec mappage des longueurs d'onde.
- Export des résultats et paramètres.

**Utilisation** :

```bash
python scan_compensation_gui_cloud.py
```

### Système double caméra (chemin actuel)

Système d'enregistrement synchronisé pour caméra événementielle et caméra image :

- `ImagingGUI/DualCamera_separate_transform.py`

**Fonctionnalités** :

- Enregistrement simultané événement + image.
- Prévisualisation en temps réel avec transformations.
- Contrôles de fenêtre toujours au premier plan.
- Ajustement des paramètres pendant l'enregistrement.

### Contrôle moteur Arduino (référence de chemin legacy conservée)

Le README d'origine référençait ce chemin de sketch firmware :

- `rotor/step42_with_key_int/step42_with_key_int.ino`

La disposition actuelle du dépôt inclut des notes firmware à :

- `firmware/README.md`

Cette divergence de chemin est volontairement conservée ici ; si vous avez les dossiers de sketch rotor dans une autre branche/un autre checkout local, continuez d'utiliser ces chemins.

Capacités legacy documentées pour ce sketch :

- Contrôle angulaire précis avec microstepping.
- Profils d'accélération/décélération.
- Intégration des fins de course.
- Fonction d'auto-centrage.

## Compensation Turbo multi-scan

Quand vous avez plusieurs scans unidirectionnels (Forward/Backward) du même balayage, vous pouvez les fusionner et exécuter l'entraîneur éprouvé sur un seul flux d'événements combiné via `compensate_multiwindow_turbo.py`.

### Ce que cela fait

- Accepte un segment, une liste explicite ou un dossier complet de segments.
- Pour les scans Backward, inverse la polarité et renverse le temps avant fusion :
- Si polarité `p ∈ {0,1}` : `p := 1 − p`; puis inversion du temps dans le scan.
- Si polarité `p ∈ {−1,1}` : `p := −p`; puis inversion du temps dans le scan.
- Concatène les scans sur une timeline continue (avec un écart de `1 μs` entre scans) et appelle `compensate_multiwindow_train_saved_params.py` en interne.

### Utilisation

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

- `--segment`, `--segments`, `--segments-dir` : choisir votre jeu d'entrée.
- `--include {all|forward|backward}` : filtrer par direction de scan.
- `--sort {name|time}` : ordre naturel des noms de fichiers ou ordre NPZ `start_time`.
- `--bin-width <μs>` : transmis à l'entraîneur de base.
- `--load-params` : réutiliser des paramètres sauvegardés (saute l'entraînement et régénère rapidement les sorties à de nouvelles largeurs de bin).
- `--extra ...` après `--` : tous les flags supplémentaires sont transmis à l'entraîneur de base.

### Astuce de mise à l'échelle de vitesse

Si votre scan est `N×` plus rapide que la baseline, réduisez `--bin-width` du même facteur (ex. baseline `50 ms` -> `10×` plus rapide -> `5 ms` : `--bin-width 5000`). Vous pouvez entraîner une fois (p. ex. `5 ms`), puis utiliser `--load-params` pour régénérer rapidement des résultats à `10 ms` sans réentraînement.

## Gestion des paramètres

Le système prend en charge des fonctions complètes de sauvegarde/chargement des paramètres.

### Formats de sauvegarde

- **NPZ** : format binaire pour chargement rapide.
- **JSON** : lisible humain avec métadonnées.
- **CSV** : compatible Excel pour inspection manuelle.

### Chargement des paramètres

```bash
# Load any supported format
python compensate_multiwindow_train_saved_params.py segment.npz \
  --load_params learned_params.npz
# or --load_params learned_params.json
# or --load_params learned_params.csv
```

### Fichiers de paramètres

Les fichiers sont automatiquement nommés avec le nombre de paramètres, par exemple : `*_learned_params_n13.*`.

## Optimisation mémoire

Le système utilise un traitement par chunks de bout en bout :

| Élément | Détail |
|---|---|
| Taille de chunk | `250000` événements par défaut (configurable) |
| Efficacité mémoire | Traite de gros datasets sans overflow GPU |
| Variance unifiée | Maintient un flux de gradient correct pour l'apprentissage |
| Suivi de progression | Mises à jour de traitement en temps réel |

## Structure de sortie

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

## Exemples de configuration

### Compensation haute précision

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 21 --temperature 3000 --iterations 2000 \
  --a_trainable --b_trainable --boundary_trainable \
  --smoothness_weight 0.0001 --chunk_size 100000
```

### Traitement rapide

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --num_params 7 --iterations 500 --chunk_size 500000 \
  --a_fixed --b_default -76.0
```

### Contrainte mémoire

```bash
python compensate_multiwindow_train_saved_params.py segment.npz \
  --chunk_size 50000 --bin_width 100000
```

## Correspondance longueur d'onde

Le système prend en charge la visualisation spectrale en associant l'évolution temporelle à la longueur d'onde :

```python
# Linear mapping: time -> wavelength
wavelength = wavelength_min + (t_normalized / t_max) * (wavelength_max - wavelength_min)
```

**Plage par défaut** : $380\text{–}680~\text{nm}$ (configurable).

## Conseils et bonnes pratiques

### Sélection de paramètres

- **Microstepping** : utilisez `32×` pour un mouvement fluide (Arduino).
- **Largeur de bin** : commencez à `50 ms` pour l'optimisation, `2 ms` pour l'analyse.
- **Température** : des valeurs plus élevées (autour de `5000`) pour des frontières plus lisses.
- **Lissage** : `0.001` fournit une bonne régularisation.

### Gestion mémoire

- **Mémoire GPU** : utilisez le traitement par chunks avec une taille adaptée.
- **Nombre d'événements** : `> 10^6` événements recommandés pour un apprentissage stable.
- **Itérations** : `1000` itérations suffisent généralement.

### Organisation des fichiers

- Gardez les fichiers RAW et les segments dans le même répertoire.
- Les fichiers de paramètres sont auto-détectés via la convention de nommage.
- Utilisez des préfixes de nom de fichier descriptifs pour organiser les sorties.

## Notes de développement

- `versions.md` décrit les ères historiques du projet et la logique de migration.
- `.githooks/pre-commit` bloque les commits surdimensionnés/binaires et certains types de fichiers non code/doc.
- `scripts/setup_hooks.sh` définit `core.hooksPath` sur `.githooks`.
- `archive_code_variants/` stocke les variantes de scripts plus anciennes pour garder les outils racine concentrés.

Dérive documentaire connue (conservée intentionnellement pour contexte de compatibilité rétro) :

- Certains anciens docs mentionnent `sync_image_system/` ou `dual_camera_gui.py` ; le checkout actuel contient `ImagingGUI/DualCamera_separate_transform.py` et des répertoires SDK.
- `ImagingGUI/README.md` mentionne encore `pip install -r requirements.txt`, mais aucun `requirements.txt` racine n'est présent dans ce checkout.
- `firmware/README.md` mentionne plusieurs sous-dossiers de sketches Arduino qui ne sont pas présents dans ce checkout.
- `versions.md` mentionne des noms de scripts legacy différents des noms de scripts actuels à la racine.
- `i18n/` existe et inclut actuellement `README.ar.md`, `README.es.md`, `README.fr.md`, `README.ja.md` et `README.ko.md` ; les liens vers des langues supplémentaires sont conservés en tant que cibles prévues.

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Erreurs de chargement de paramètres | Incohérence du nombre de paramètres | Vérifiez que `--num_params` correspond au fichier sauvegardé |
| OOM / pression mémoire | Chunk trop grand ou bins trop fins | Réduisez `--chunk_size` et/ou augmentez `--bin_width` |
| Qualité de compensation faible | Entraînement insuffisant ou segmentation médiocre | Augmentez `--iterations`, activez les paramètres entraînables, vérifiez la segmentation |
| Aucun fichier segment produit | Problème RAW/SDK/flag | Confirmez le chemin RAW, la configuration Metavision et `--segment_events` |
| Args du wrapper Turbo ignorés | Syntaxe de forwarding incorrecte | Passez les args entraîneur après `--` (ou utilisez `--extra`) |
| Problèmes GUI | Incompatibilité Tkinter/backend ou SDK | Vérifiez le backend GUI et la disponibilité du SDK caméra |

- **Erreurs de chargement de paramètres** : assurez-vous que `--num_params` est compatible avec le fichier de paramètres chargé.
- **OOM / pression mémoire** : réduisez `--chunk_size` et/ou augmentez `--bin_width`.
- **Qualité de compensation faible** : augmentez `--iterations`, activez les paramètres entraînables (`--a_trainable`, `--b_trainable`, éventuellement `--boundary_trainable`), et vérifiez la qualité de segmentation.
- **Aucun fichier segment produit** : confirmez le chemin RAW, la disponibilité du lecteur Metavision, et que `--segment_events` a bien été passé.
- **Passage d'arguments au wrapper Turbo** : placez les arguments entraîneur après `--` (ou utilisez `--extra`).
- **Problèmes GUI** : vérifiez le support backend Tkinter et la disponibilité du SDK caméra sur votre plateforme.

## Feuille de route

- Améliorer la reproductibilité des dépendances/bootstrap (`requirements.txt` ou lockfile d'environnement).
- Consolider les noms de scripts legacy et les références de chemins à travers la documentation.
- Étendre les schémas de datasets documentés et les conventions attendues des champs NPZ.
- Ajouter des tests de type régression pour segmentation/compensation sur de petites données de fixture.
- Continuer l'intégration de sorties d'analyse de qualité publication issues des pipelines `align_*`.
- Ajouter/actualiser les fichiers README multilingues restants sous `i18n/` pour correspondre entièrement aux liens de navigation de langue en tête.

## Citation

Si ce dépôt vous est utile dans vos recherches, veuillez citer la prépublication Optica Open :

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

## Remerciements

- Prépublication Optica Open et supports de diffusion du projet associés.
- Contributeurs matériels et logiciels à travers l'évolution du dépôt capturée dans `versions/` et les outils archivés.
- Soutien de la communauté via GitHub Sponsors et les canaux projet associés.

## Licence

Ce projet est publié sous licence MIT. Voir [`LICENSE`](LICENSE) pour les détails.

## Contribuer

Les contributions sont bienvenues.

- Commencez par les scripts et le style de documentation existants.
- Gardez les exemples en ligne de commande reproductibles avec les chemins du dépôt lorsque possible.
- Si vous ajoutez de gros datasets/sorties, assurez-vous de respecter les politiques `.githooks/pre-commit`.

Remarque : aucun `CONTRIBUTING.md` dédié n'est présent dans ce checkout. Si nécessaire, ouvrez une issue ou soumettez une PR avec le workflow de contribution que vous proposez.

## Support / Sponsor

| Canal | Lien | Usage |
|---|---|---|
| GitHub Sponsors | https://github.com/sponsors/lachlanchen | Support continu du projet |
| Site du projet | https://lazying.art | Mises à jour projet et liens écosystème |
| Chat communauté | https://chat.lazying.art | Discussion communautaire |
| Page créateur additionnelle | https://onlyideas.art | Contenu créateur/recherche connexe |
| Page d'achat du kit principal | https://lazying.art/openhi-kit.html | Kit de démarrage matériel pour workflow OpenHI |
| Code promotionnel | `OPTICA` | 30 % de réduction (comme documenté ci-dessus) |

---

### Notes

- 📌 Ce README conserve des notes de chemins legacy là où l'évolution du dépôt a introduit des écarts de nommage/de structure.
- 🔒 En cas d'incertitude sur d'anciennes références, le texte est conservé intentionnellement plutôt que supprimé.
