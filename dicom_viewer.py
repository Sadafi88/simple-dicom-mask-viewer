import argparse
from pathlib import Path

import cv2
import numpy as np
import pydicom
import matplotlib.pyplot as plt


def load_dicom(dicom_path):
    ds = pydicom.dcmread(dicom_path)
    image = ds.pixel_array.astype(np.float32)

    slope = float(getattr(ds, "RescaleSlope", 1))
    intercept = float(getattr(ds, "RescaleIntercept", 0))
    image = image * slope + intercept

    return image, ds


def apply_window(image, window_center=None, window_width=None):
    if window_center is None or window_width is None:
        low = np.percentile(image, 1)
        high = np.percentile(image, 99)
    else:
        low = window_center - window_width / 2
        high = window_center + window_width / 2

    image = np.clip(image, low, high)
    image = (image - low) / (high - low + 1e-8)
    image = (image * 255).astype(np.uint8)

    return image


def load_mask(mask_path, target_shape):
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise ValueError(f"Could not read mask: {mask_path}")

    if mask.shape != target_shape:
        mask = cv2.resize(
            mask,
            (target_shape[1], target_shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )

    mask = mask > 0
    return mask


def overlay_mask(image_uint8, mask, alpha=0.4):
    image_rgb = cv2.cvtColor(image_uint8, cv2.COLOR_GRAY2RGB)

    overlay = image_rgb.copy()
    overlay[mask] = [255, 0, 0]

    blended = cv2.addWeighted(overlay, alpha, image_rgb, 1 - alpha, 0)
    return blended


def show_image(image, title="DICOM Viewer"):
    plt.figure(figsize=(7, 7))
    plt.imshow(image, cmap="gray" if image.ndim == 2 else None)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def save_image(image, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    cv2.imwrite(str(output_path), image)


def main():
    parser = argparse.ArgumentParser(
        description="Simple DICOM viewer with windowing and mask overlay"
    )

    parser.add_argument("--dicom", required=True, help="Path to DICOM file")
    parser.add_argument("--mask", default=None, help="Optional path to mask image")
    parser.add_argument("--window-center", type=float, default=None)
    parser.add_argument("--window-width", type=float, default=None)
    parser.add_argument("--alpha", type=float, default=0.4)
    parser.add_argument("--save", default=None, help="Optional output image path")

    args = parser.parse_args()

    image, ds = load_dicom(args.dicom)
    if image.ndim == 3:
       image = image[image.shape[0] // 2]

    window_center = args.window_center
    window_width = args.window_width

    if window_center is None:
        wc = getattr(ds, "WindowCenter", None)
        if isinstance(wc, pydicom.multival.MultiValue):
            wc = wc[0]
        window_center = float(wc) if wc is not None else None

    if window_width is None:
        ww = getattr(ds, "WindowWidth", None)
        if isinstance(ww, pydicom.multival.MultiValue):
            ww = ww[0]
        window_width = float(ww) if ww is not None else None

    image_uint8 = apply_window(image, window_center, window_width)

    if args.mask:
        mask = load_mask(args.mask, image_uint8.shape)
        output = overlay_mask(image_uint8, mask, alpha=args.alpha)
        title = "DICOM with Mask Overlay"
    else:
        output = image_uint8
        title = "DICOM Image"

    show_image(output, title=title)

    if args.save:
        save_image(output, args.save)
        print(f"Saved to: {args.save}")


if __name__ == "__main__":
    main()
