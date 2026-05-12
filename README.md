# Medical Image Mask Viewer

A lightweight Python tool for visualizing medical images with optional segmentation mask overlay.

Supports:

* DICOM (`.dcm`)
* NIfTI (`.nii`, `.nii.gz`)

## Features

- Read DICOM images
- Read NIfTI volumes
- Middle-slice visualization for 3D medical volumes
- Automatic windowing
- Adjustable image windowing using custom window center/width
- Segmentation mask overlay
- Save visualization output using the `--save` option
## Installation

```bash
pip install -r requirements.txt
```

## Usage

### View DICOM image

```bash
python dicom_viewer.py --dicom sample.dcm
```

### View NIfTI image

```bash
python dicom_viewer.py --dicom sample.nii.gz
```

### View with segmentation mask

```bash
python dicom_viewer.py --dicom sample.nii.gz --mask mask.png
```

## Requirements

* pydicom
* nibabel
* numpy
* matplotlib
* opencv-python
