#!/usr/bin/env python3
"""
Run Cellpose on a single image and save the mask + overlay.

Example:
  python scripts/cellpose_simple_mask.py \
      --image hyperspectral_data_sanqin_gt/test300_rotated_frames_137d37_rgb_colorimetric.png \
      --out-dir outputs_root/cellpose_test
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Cellpose single-image mask")
    ap.add_argument("--image", type=Path, required=True, help="Input image (PNG/JPG/TIF)")
    ap.add_argument("--out-dir", type=Path, required=True, help="Output directory")
    ap.add_argument("--model", default="cyto", help="Cellpose model type (default: cyto)")
    ap.add_argument("--pretrained-model", default="cyto", help="Cellpose pretrained model name (default: cyto)")
    ap.add_argument("--diameter", type=float, default=None, help="Cellpose diameter (omit for auto)")
    ap.add_argument("--rescale", type=float, default=None, help="Rescale image before running (e.g., 0.5)")
    ap.add_argument("--flow-threshold", type=float, default=0.4, help="Cellpose flow threshold")
    ap.add_argument("--cellprob-threshold", type=float, default=0.0, help="Cellpose cellprob threshold")
    ap.add_argument("--largest-only", action="store_true", help="Keep only the largest mask")
    ap.add_argument("--alpha", type=float, default=0.35, help="Overlay alpha (default: 0.35)")
    return ap.parse_args()


def load_image(path: Path) -> np.ndarray:
    img = plt.imread(str(path))
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    if img.shape[2] == 4:
        img = img[:, :, :3]
    img = img.astype(np.float32)
    if img.max() > 1.5:
        img = img / 255.0
    return img


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


def run_cellpose(
    img: np.ndarray,
    model_type: str,
    pretrained_model: str,
    diameter: float | None,
    rescale: float | None,
    flow_threshold: float,
    cellprob_threshold: float,
) -> np.ndarray:
    try:
        from cellpose import models  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Cellpose is not installed. Install with `pip install cellpose`.") from exc

    if hasattr(models, "Cellpose"):
        eval_kwargs = dict(
            diameter=diameter,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
        )
        if rescale is not None:
            eval_kwargs["rescale"] = rescale
        model = models.Cellpose(model_type=model_type)
        masks, _, _, _ = model.eval(img, channels=[0, 0], **eval_kwargs)
    elif hasattr(models, "CellposeModel"):
        model = models.CellposeModel(pretrained_model=pretrained_model, model_type=None)
        img_in, scale = maybe_downsample(img, rescale)
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
    return masks


def keep_largest(mask: np.ndarray) -> np.ndarray:
    labels, counts = np.unique(mask, return_counts=True)
    labels = labels[labels != 0]
    if labels.size == 0:
        return mask
    counts = counts[1:] if counts.size > labels.size else counts
    largest_label = labels[np.argmax(counts)]
    return (mask == largest_label).astype(mask.dtype)


def overlay_mask(img: np.ndarray, mask: np.ndarray, alpha: float) -> np.ndarray:
    overlay = img.copy()
    color = np.array([1.0, 0.2, 0.2], dtype=np.float32)
    if mask.max() > 1:
        region = mask > 0
    else:
        region = mask.astype(bool)
    overlay[region] = (1 - alpha) * overlay[region] + alpha * color
    return np.clip(overlay, 0.0, 1.0)


def save_mask(mask: np.ndarray, out_dir: Path) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    mask_path = out_dir / "cellpose_mask.png"
    overlay_path = out_dir / "cellpose_overlay.png"
    plt.imsave(str(mask_path), mask, cmap="gray")
    return mask_path, overlay_path


def main() -> None:
    args = parse_args()
    img = load_image(args.image)
    masks = run_cellpose(
        img,
        model_type=args.model,
        pretrained_model=args.pretrained_model,
        diameter=args.diameter,
        rescale=args.rescale,
        flow_threshold=args.flow_threshold,
        cellprob_threshold=args.cellprob_threshold,
    )
    if args.largest_only:
        masks = keep_largest(masks)

    mask_path, overlay_path = save_mask(masks, args.out_dir)
    overlay = overlay_mask(img, masks, args.alpha)
    plt.imsave(str(overlay_path), overlay)

    unique = np.unique(masks)
    n_masks = int((unique != 0).sum())
    area = int((masks > 0).sum())
    print(f"Saved mask: {mask_path}")
    print(f"Saved overlay: {overlay_path}")
    print(f"Masks: {n_masks}, area(px): {area}")


if __name__ == "__main__":
    main()
