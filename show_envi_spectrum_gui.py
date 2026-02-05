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
    args = parser.parse_args()

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

    start_x = samples // 2
    start_y = lines // 2
    spectrum = get_pixel_spectrum(data, interleave, start_x, start_y).astype(np.float32)

    roi_bbox = None
    roi_mask = None
    roi_mean = None
    if args.roi_json is not None:
        roi = load_roi_json(args.roi_json)
        roi_bbox = bbox_from_roi(roi, samples, lines)
        roi_mask = load_mask(_resolve_path(roi.get("mask_png"), args.roi_json.parent), (lines, samples))
        roi_mean = compute_roi_mean(data, interleave, bands, roi_bbox, roi_mask)

    fig = plt.figure(figsize=(12, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=(1.1, 1.0), wspace=0.25)
    ax_img = fig.add_subplot(gs[0, 0])
    ax_spec = fig.add_subplot(gs[0, 1])

    ax_img.imshow(rgb, origin="upper")
    ax_img.set_title("RGB composite (click to view spectrum)")
    ax_img.set_xlabel("Sample (x)")
    ax_img.set_ylabel("Line (y)")

    point, = ax_img.plot([start_x], [start_y], marker="o", markersize=7, markerfacecolor="none",
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
        ax_img.imshow(roi_mask.astype(float), cmap="gray", alpha=0.25, origin="upper")
    if roi_bbox is not None:
        x0, y0, x1, y1 = roi_bbox
        roi_patch = Rectangle(
            (x0, y0),
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
        x = int(round(event.xdata))
        y = int(round(event.ydata))
        if x < 0 or x >= samples or y < 0 or y >= lines:
            return
        spectrum_local = get_pixel_spectrum(data, interleave, x, y).astype(np.float32)
        line.set_ydata(spectrum_local)
        ax_spec.relim()
        ax_spec.autoscale_view(scalex=False, scaley=True)
        ax_spec.set_title(f"Spectrum at (x={x}, y={y})")
        point.set_data([x], [y])
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()


if __name__ == "__main__":
    main()
