#!/usr/bin/env python3
"""
Interactive ENVI spectrum viewer.

Usage:
  python show_envi_spectrum_gui.py hyperspectral_data_sanqin_gt/test300.hdr

Click on the RGB image to update the spectrum plot.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def parse_number(token: str) -> Any:
    token = token.strip()
    if not token:
        return token
    if token.lower() in {"true", "false"}:
        return token.lower() == "true"
    try:
        if any(ch in token for ch in [".", "e", "E"]):
            return float(token)
        return int(token)
    except ValueError:
        return token


def parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        inner = raw[1:-1]
        items = [parse_number(item) for item in inner.replace("\n", " ").split(",")]
        return [item for item in (item for item in items) if item != ""]
    return parse_number(raw)


def parse_envi_header(path: Path) -> Dict[str, Any]:
    text = path.read_text(errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith(";")]
    header: Dict[str, Any] = {}
    key = None
    value_parts: List[str] = []
    brace_level = 0

    for line in lines:
        if key is None:
            if "=" not in line:
                continue
            key, rest = [part.strip() for part in line.split("=", 1)]
            value_parts = [rest]
            brace_level = rest.count("{") - rest.count("}")
            if brace_level == 0:
                header[key.lower()] = parse_value(rest)
                key = None
        else:
            value_parts.append(line)
            brace_level += line.count("{") - line.count("}")
            if brace_level == 0:
                raw = " ".join(value_parts)
                header[key.lower()] = parse_value(raw)
                key = None

    return header


def _resolve_path(raw: Any, base_dir: Path) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()


def load_roi_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _clamp_bbox(bbox: Tuple[int, int, int, int], samples: int, lines: int) -> Tuple[int, int, int, int]:
    x0, y0, x1, y1 = bbox
    x0 = max(0, min(samples - 1, x0))
    x1 = max(0, min(samples - 1, x1))
    y0 = max(0, min(lines - 1, y0))
    y1 = max(0, min(lines - 1, y1))
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return x0, y0, x1, y1


def bbox_from_roi(roi: Dict[str, Any], samples: int, lines: int) -> Tuple[int, int, int, int] | None:
    bbox_rel = roi.get("bbox_rel")
    if isinstance(bbox_rel, list) and len(bbox_rel) == 4:
        x0_rel, y0_rel, x1_rel, y1_rel = [float(v) for v in bbox_rel]
        x0 = int(round(x0_rel * (samples - 1)))
        x1 = int(round(x1_rel * (samples - 1)))
        y0 = int(round(y0_rel * (lines - 1)))
        y1 = int(round(y1_rel * (lines - 1)))
        return _clamp_bbox((x0, y0, x1, y1), samples, lines)

    bbox_xyxy = roi.get("bbox_xyxy")
    if isinstance(bbox_xyxy, list) and len(bbox_xyxy) == 4:
        x0, y0, x1, y1 = [int(round(v)) for v in bbox_xyxy]
        return _clamp_bbox((x0, y0, x1, y1), samples, lines)

    return None


def load_mask(mask_path: Path | None, target_shape: Tuple[int, int]) -> np.ndarray | None:
    if mask_path is None or not mask_path.exists():
        return None
    mask_img = plt.imread(mask_path)
    if mask_img.ndim == 3:
        mask_img = mask_img[..., 0]
    mask = mask_img > 0.5
    if mask.shape == target_shape:
        return mask
    src_h, src_w = mask.shape
    dst_h, dst_w = target_shape
    y_idx = np.round(np.linspace(0, src_h - 1, dst_h)).astype(int)
    x_idx = np.round(np.linspace(0, src_w - 1, dst_w)).astype(int)
    return mask[np.ix_(y_idx, x_idx)]


def rgb_to_gray(rgb: np.ndarray) -> np.ndarray:
    if rgb.ndim == 2:
        return rgb.astype(np.float32)
    r = rgb[..., 0].astype(np.float32)
    g = rgb[..., 1].astype(np.float32)
    b = rgb[..., 2].astype(np.float32)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def resize_nearest(img: np.ndarray, new_h: int, new_w: int) -> np.ndarray:
    h, w = img.shape[:2]
    y_idx = np.round(np.linspace(0, h - 1, new_h)).astype(int)
    x_idx = np.round(np.linspace(0, w - 1, new_w)).astype(int)
    if img.ndim == 2:
        return img[np.ix_(y_idx, x_idx)]
    return img[np.ix_(y_idx, x_idx, np.arange(img.shape[2]))]


def maybe_downsample(img: np.ndarray, scale: float | None) -> Tuple[np.ndarray, float]:
    if scale is None or np.isclose(scale, 1.0):
        return img, 1.0
    h, w = img.shape[:2]
    new_h = max(1, int(round(h * scale)))
    new_w = max(1, int(round(w * scale)))
    return resize_nearest(img, new_h, new_w), float(scale)


def match_feature_roi(search_rgb: np.ndarray, template_path: Path, min_matches: int = 12) -> Tuple[int, int, int, int] | None:
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "OpenCV is required for feature matching. Install with `pip install opencv-python-headless`."
        ) from exc

    templ = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if templ is None:
        raise FileNotFoundError(template_path)

    search = search_rgb
    if search.dtype != np.uint8:
        search = (np.clip(search, 0.0, 1.0) * 255.0).astype(np.uint8)
    search_bgr = search[:, :, ::-1]

    templ_gray = cv2.cvtColor(templ, cv2.COLOR_BGR2GRAY)
    search_gray = cv2.cvtColor(search_bgr, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(nfeatures=1500)
    kp1, des1 = orb.detectAndCompute(templ_gray, None)
    kp2, des2 = orb.detectAndCompute(search_gray, None)
    if des1 is None or des2 is None:
        return None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    if len(good) < min_matches:
        return None

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None:
        return None

    h, w = templ_gray.shape[:2]
    corners = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]).reshape(-1, 1, 2)
    warped = cv2.perspectiveTransform(corners, H).reshape(-1, 2)
    x0 = int(np.floor(warped[:, 0].min()))
    x1 = int(np.ceil(warped[:, 0].max()))
    y0 = int(np.floor(warped[:, 1].min()))
    y1 = int(np.ceil(warped[:, 1].max()))
    Hs, Ws = search_gray.shape
    x0, y0, x1, y1 = _clamp_bbox((x0, y0, x1, y1), Ws, Hs)
    return x0, y0, x1, y1


def match_template_roi(search_rgb: np.ndarray, template_path: Path) -> Tuple[int, int, int, int] | None:
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "OpenCV is required for template matching. Install with `pip install opencv-python-headless`."
        ) from exc

    templ = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if templ is None:
        raise FileNotFoundError(template_path)

    search = search_rgb
    if search.dtype != np.uint8:
        search = (np.clip(search, 0.0, 1.0) * 255.0).astype(np.uint8)
    search_bgr = search[:, :, ::-1]

    templ_gray = cv2.cvtColor(templ, cv2.COLOR_BGR2GRAY)
    search_gray = cv2.cvtColor(search_bgr, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(search_gray, templ_gray, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)
    x0, y0 = int(max_loc[0]), int(max_loc[1])
    h, w = templ_gray.shape[:2]
    x1, y1 = x0 + w - 1, y0 + h - 1
    Hs, Ws = search_gray.shape
    return _clamp_bbox((x0, y0, x1, y1), Ws, Hs)


def detect_cellpose_roi(
    rgb: np.ndarray,
    model_type: str,
    pretrained_model: str,
    diameter: float | None,
    rescale: float | None,
    flow_threshold: float,
    cellprob_threshold: float,
) -> np.ndarray | None:
    try:
        from cellpose import models  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Cellpose is not installed. Install with `pip install cellpose` in your env."
        ) from exc

    img = np.asarray(rgb, dtype=np.float32)
    if img.max() > 1.5:
        img = img / 255.0
    gray = rgb_to_gray(img)
    if hasattr(models, "Cellpose"):
        model = models.Cellpose(model_type=model_type)
        eval_kwargs = dict(
            diameter=diameter,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
        )
        if rescale is not None:
            eval_kwargs["rescale"] = rescale
        masks, _, _, _ = model.eval(gray, channels=[0, 0], **eval_kwargs)
    elif hasattr(models, "CellposeModel"):
        model = models.CellposeModel(pretrained_model=pretrained_model, model_type=None)
        if img.ndim == 2:
            img_in = np.stack([img, img, img], axis=-1)
        else:
            img_in = img
        img_in, scale = maybe_downsample(img_in, rescale)
        masks, _, _ = model.eval(
            img_in,
            diameter=diameter,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
        )
        if not np.isclose(scale, 1.0):
            h, w = img.shape[:2]
            masks = resize_nearest(masks, h, w)
    else:
        raise RuntimeError("Unsupported Cellpose API: no Cellpose or CellposeModel found.")
    if masks is None or masks.max() == 0:
        return None
    return masks


def mask_to_largest(mask: np.ndarray) -> np.ndarray | None:
    labels, counts = np.unique(mask, return_counts=True)
    labels = labels[labels != 0]
    if labels.size == 0:
        return None
    counts = counts[1:] if counts.size > labels.size else counts
    largest_label = labels[np.argmax(counts)]
    return mask == largest_label


def bbox_from_mask(mask: np.ndarray) -> Tuple[int, int, int, int] | None:
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return None
    x0 = int(xs.min())
    x1 = int(xs.max())
    y0 = int(ys.min())
    y1 = int(ys.max())
    return x0, y0, x1, y1

def dtype_from_envi(code: int, byte_order: int) -> np.dtype:
    dtype_map = {
        1: np.uint8,
        2: np.int16,
        3: np.int32,
        4: np.float32,
        5: np.float64,
        12: np.uint16,
        13: np.uint32,
        14: np.int64,
        15: np.uint64,
    }
    if code not in dtype_map:
        raise ValueError(f"Unsupported ENVI data type: {code}")
    endian = "<" if byte_order == 0 else ">"
    return np.dtype(dtype_map[code]).newbyteorder(endian)


def resolve_data_path(hdr_path: Path, header: Dict[str, Any]) -> Path:
    data_file = header.get("data file")
    if isinstance(data_file, str) and data_file:
        return hdr_path.parent / data_file
    # Default: same base name with .spe
    return hdr_path.with_suffix(".spe")


def get_band_image(data: np.memmap, interleave: str, band: int) -> np.ndarray:
    if interleave == "bil":
        return data[:, band, :]
    if interleave == "bip":
        return data[:, :, band]
    if interleave == "bsq":
        return data[band, :, :]
    raise ValueError(f"Unsupported interleave: {interleave}")


def get_pixel_spectrum(data: np.memmap, interleave: str, x: int, y: int) -> np.ndarray:
    if interleave == "bil":
        return data[y, :, x]
    if interleave == "bip":
        return data[y, x, :]
    if interleave == "bsq":
        return data[:, y, x]
    raise ValueError(f"Unsupported interleave: {interleave}")


def stretch_channel(channel: np.ndarray, p_low: float, p_high: float) -> np.ndarray:
    low, high = np.percentile(channel, [p_low, p_high])
    if high <= low:
        return np.zeros_like(channel, dtype=np.float32)
    stretched = (channel - low) / (high - low)
    return np.clip(stretched, 0.0, 1.0)


def parse_rgb_bands(value: str) -> List[int]:
    bands = [int(item.strip()) for item in value.split(",") if item.strip()]
    if len(bands) != 3:
        raise ValueError("--rgb-bands must have exactly three comma-separated values")
    return bands


def compute_roi_mean(
    data: np.memmap,
    interleave: str,
    bands: int,
    bbox: Tuple[int, int, int, int] | None,
    mask: np.ndarray | None,
) -> np.ndarray | None:
    if mask is not None and mask.any():
        ys, xs = np.nonzero(mask)
        if ys.size == 0:
            return None
        roi_mean = np.zeros(bands, dtype=np.float32)
        for band in range(bands):
            if interleave == "bil":
                roi_mean[band] = data[ys, band, xs].mean()
            elif interleave == "bip":
                roi_mean[band] = data[ys, xs, band].mean()
            elif interleave == "bsq":
                roi_mean[band] = data[band, ys, xs].mean()
        return roi_mean

    if bbox is None:
        return None
    x0, y0, x1, y1 = bbox
    if interleave == "bil":
        roi = data[y0 : y1 + 1, :, x0 : x1 + 1]
        return roi.mean(axis=(0, 2))
    if interleave == "bip":
        roi = data[y0 : y1 + 1, x0 : x1 + 1, :]
        return roi.mean(axis=(0, 1))
    if interleave == "bsq":
        roi = data[:, y0 : y1 + 1, x0 : x1 + 1]
        return roi.mean(axis=(1, 2))
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive ENVI spectrum viewer")
    parser.add_argument("hdr", type=Path, help="Path to ENVI .hdr file")
    parser.add_argument("--data", type=Path, default=None, help="Optional path to ENVI data file")
    parser.add_argument(
        "--rgb-bands",
        type=parse_rgb_bands,
        default=None,
        help="Comma-separated RGB band indices (1-based, e.g. 109,80,28)",
    )
    parser.add_argument(
        "--percentiles",
        type=str,
        default="2,98",
        help="Low/high percentiles for RGB stretch (default: 2,98)",
    )
    parser.add_argument("--gamma", type=float, default=1.0, help="Gamma correction for RGB (default: 1.0)")
    parser.add_argument("--roi-json", type=Path, default=None, help="Optional ROI json to overlay and average")
    parser.add_argument("--feature-template", type=Path, default=None, help="Template image to feature-match ROI")
    parser.add_argument("--feature-min-matches", type=int, default=12, help="Min matches for feature ROI (default: 12)")
    parser.add_argument("--crop-to-roi", action="store_true", help="Display only the ROI region")
    parser.add_argument("--font-scale", type=float, default=1.0, help="Scale all font sizes (default: 1.0)")
    parser.add_argument("--cellpose", action="store_true", help="Run Cellpose to auto-detect ROI")
    parser.add_argument("--cellpose-model", default="cyto", help="Cellpose model type (default: cyto)")
    parser.add_argument("--cellpose-pretrained", default="cyto", help="Cellpose pretrained model (default: cyto)")
    parser.add_argument("--cellpose-diameter", type=float, default=None, help="Cellpose diameter; omit for auto")
    parser.add_argument("--cellpose-rescale", type=float, default=None, help="Rescale image before Cellpose (e.g., 0.5)")
    parser.add_argument("--cellpose-flow-threshold", type=float, default=0.4, help="Cellpose flow threshold")
    parser.add_argument("--cellpose-cellprob-threshold", type=float, default=0.0, help="Cellpose cellprob threshold")
    args = parser.parse_args()

    if args.font_scale and not np.isclose(args.font_scale, 1.0):
        base = plt.rcParams["font.size"]
        scale = float(args.font_scale)
        plt.rcParams.update(
            {
                "font.size": base * scale,
                "axes.titlesize": plt.rcParams["axes.titlesize"] * scale,
                "axes.labelsize": plt.rcParams["axes.labelsize"] * scale,
                "xtick.labelsize": plt.rcParams["xtick.labelsize"] * scale,
                "ytick.labelsize": plt.rcParams["ytick.labelsize"] * scale,
                "legend.fontsize": plt.rcParams["legend.fontsize"] * scale,
            }
        )

    header = parse_envi_header(args.hdr)
    samples = int(header.get("samples"))
    lines = int(header.get("lines"))
    bands = int(header.get("bands"))
    interleave = str(header.get("interleave", "bil")).lower()
    data_type = int(header.get("data type"))
    byte_order = int(header.get("byte order", 0))
    header_offset = int(header.get("header offset", 0))

    data_path = args.data if args.data is not None else resolve_data_path(args.hdr, header)
    dtype = dtype_from_envi(data_type, byte_order)

    if interleave == "bil":
        shape = (lines, bands, samples)
    elif interleave == "bip":
        shape = (lines, samples, bands)
    elif interleave == "bsq":
        shape = (bands, lines, samples)
    else:
        raise ValueError(f"Unsupported interleave: {interleave}")

    data = np.memmap(data_path, dtype=dtype, mode="r", offset=header_offset, shape=shape)

    default_bands = header.get("default bands")
    if args.rgb_bands is not None:
        rgb_bands = args.rgb_bands
    elif isinstance(default_bands, list) and len(default_bands) == 3:
        rgb_bands = [int(band) for band in default_bands]
    else:
        rgb_bands = [bands - 1, bands // 2, 0]

    # Convert to 0-based indices (ENVI uses 1-based)
    rgb_bands = [band - 1 for band in rgb_bands]

    if any(band < 0 or band >= bands for band in rgb_bands):
        raise ValueError(f"RGB bands {rgb_bands} out of range for {bands} bands")

    p_low, p_high = [float(item.strip()) for item in args.percentiles.split(",")]

    rgb_channels = []
    for band in rgb_bands:
        channel = get_band_image(data, interleave, band).astype(np.float32)
        rgb_channels.append(stretch_channel(channel, p_low, p_high))

    rgb = np.dstack(rgb_channels)
    if args.gamma != 1.0:
        rgb = np.clip(rgb, 0.0, 1.0) ** (1.0 / args.gamma)

    wavelengths = header.get("wavelength")
    if isinstance(wavelengths, list) and len(wavelengths) == bands:
        x_axis = np.array(wavelengths, dtype=float)
        x_label = f"Wavelength ({header.get('wavelength units', 'nm')})"
    else:
        x_axis = np.arange(bands)
        x_label = "Band index"

    display_x0 = 0
    display_y0 = 0
    display_x1 = samples - 1
    display_y1 = lines - 1

    roi_bbox = None
    roi_mask = None
    roi_mean = None
    if args.feature_template is not None:
        roi_bbox = match_feature_roi(rgb, args.feature_template, min_matches=args.feature_min_matches)
        if roi_bbox is None:
            roi_bbox = match_template_roi(rgb, args.feature_template)
        if roi_bbox is not None:
            roi_mean = compute_roi_mean(data, interleave, bands, roi_bbox, None)
    elif args.roi_json is not None:
        roi = load_roi_json(args.roi_json)
        roi_bbox = bbox_from_roi(roi, samples, lines)
        roi_mask = load_mask(_resolve_path(roi.get("mask_png"), args.roi_json.parent), (lines, samples))
        roi_mean = compute_roi_mean(data, interleave, bands, roi_bbox, roi_mask)
    elif args.cellpose:
        masks = detect_cellpose_roi(
            rgb,
            model_type=args.cellpose_model,
            pretrained_model=args.cellpose_pretrained,
            diameter=args.cellpose_diameter,
            rescale=args.cellpose_rescale,
            flow_threshold=args.cellpose_flow_threshold,
            cellprob_threshold=args.cellpose_cellprob_threshold,
        )
        if masks is not None:
            roi_mask = mask_to_largest(masks)
            if roi_mask is not None:
                roi_bbox = bbox_from_mask(roi_mask)
                roi_mean = compute_roi_mean(data, interleave, bands, roi_bbox, roi_mask)

    if roi_bbox is not None and (args.crop_to_roi or args.feature_template is not None):
        display_x0, display_y0, display_x1, display_y1 = roi_bbox

    start_x = (display_x0 + display_x1) // 2
    start_y = (display_y0 + display_y1) // 2
    spectrum = get_pixel_spectrum(data, interleave, start_x, start_y).astype(np.float32)

    fig = plt.figure(figsize=(12, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=(1.1, 1.0), wspace=0.25)
    ax_img = fig.add_subplot(gs[0, 0])
    ax_spec = fig.add_subplot(gs[0, 1])

    rgb_display = rgb[display_y0 : display_y1 + 1, display_x0 : display_x1 + 1]
    ax_img.imshow(rgb_display, origin="upper")
    ax_img.set_title("RGB composite (click to view spectrum)")
    ax_img.set_xlabel("Sample (x)")
    ax_img.set_ylabel("Line (y)")

    point, = ax_img.plot([start_x - display_x0], [start_y - display_y0], marker="o", markersize=7, markerfacecolor="none",
                         markeredgecolor="white", markeredgewidth=1.5)

    line, = ax_spec.plot(x_axis, spectrum, color="#1f77b4", linewidth=1.5, label="Pixel")
    if roi_mean is not None:
        ax_spec.plot(x_axis, roi_mean, color="#ff7f0e", linewidth=1.6, linestyle="--", label="ROI mean")
    ax_spec.set_xlabel(x_label)
    ax_spec.set_ylabel("Intensity")
    ax_spec.set_title(f"Spectrum at (x={start_x}, y={start_y})")
    if roi_mean is not None:
        ax_spec.legend(loc="best", frameon=False)

    if roi_mask is not None:
        mask_crop = roi_mask[display_y0 : display_y1 + 1, display_x0 : display_x1 + 1]
        ax_img.imshow(mask_crop.astype(float), cmap="autumn", alpha=0.25, origin="upper")
    if roi_bbox is not None and (display_x0, display_y0, display_x1, display_y1) != roi_bbox:
        x0, y0, x1, y1 = roi_bbox
        roi_patch = Rectangle(
            (x0 - display_x0, y0 - display_y0),
            x1 - x0 + 1,
            y1 - y0 + 1,
            fill=False,
            edgecolor="#ffcc00",
            linewidth=1.5,
        )
        ax_img.add_patch(roi_patch)

    def on_click(event) -> None:
        if event.inaxes != ax_img or event.xdata is None or event.ydata is None:
            return
        x = int(round(event.xdata)) + display_x0
        y = int(round(event.ydata)) + display_y0
        if x < display_x0 or x > display_x1 or y < display_y0 or y > display_y1:
            return
        spectrum_local = get_pixel_spectrum(data, interleave, x, y).astype(np.float32)
        line.set_ydata(spectrum_local)
        ax_spec.relim()
        ax_spec.autoscale_view(scalex=False, scaley=True)
        ax_spec.set_title(f"Spectrum at (x={x}, y={y})")
        point.set_data([x - display_x0], [y - display_y0])
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()


if __name__ == "__main__":
    main()
