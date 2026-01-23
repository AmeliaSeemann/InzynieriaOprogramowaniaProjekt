import numpy as np
import cv2 as cv

from photos_opencv import (
    get_crop,
    extract_mask_and_contour,
    compute_curvature,
    find_edge_features_from_curvature,
    resize_photo_for_analysis
)

# =========================
# TESTY get_crop
# =========================

def test_get_crop_returns_valid_bbox_for_alpha_image():
    img = np.zeros((100, 100, 4), dtype=np.uint8)
    img[30:70, 40:80, 3] = 255  # prostokąt widoczny w alfie

    crop = get_crop(img)

    assert crop is not None
    x, y, w, h = crop
    assert w > 0
    assert h > 0


# =========================
# TESTY extract_mask_and_contour
# =========================

def test_extract_mask_and_contour_returns_mask_and_contour():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv.rectangle(img, (20, 20), (80, 80), (255, 255, 255), -1)

    mask, contour = extract_mask_and_contour(img)

    assert mask is not None
    assert contour is not None
    assert len(contour) > 0


def test_extract_mask_and_contour_empty_image():
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    mask, contour = extract_mask_and_contour(img)

    assert mask is not None
    assert contour is not None
    assert len(contour) > 0


# =========================
# TESTY compute_curvature
# =========================

def test_compute_curvature_returns_arrays():
    contour = np.array([
        [[10, 10]],
        [[20, 10]],
        [[20, 20]],
        [[10, 20]]
    ])

    idx, curv, pts = compute_curvature(contour, k=1)

    assert isinstance(idx, np.ndarray)
    assert isinstance(curv, np.ndarray)
    assert isinstance(pts, np.ndarray)


def test_compute_curvature_too_few_points():
    contour = np.array([
        [[0, 0]],
        [[1, 1]]
    ])

    idx, curv, pts = compute_curvature(contour, k=2)

    assert len(idx) == 0
    assert len(curv) == 0
    assert len(pts) == 0


# =========================
# TESTY find_edge_features_from_curvature
# =========================

def test_find_edge_features_returns_list():
    contour = np.array([
        [[10, 10]],
        [[20, 10]],
        [[30, 20]],
        [[20, 30]],
        [[10, 20]]
    ])

    features = find_edge_features_from_curvature(contour, k=1, angle_thresh_deg=10)

    assert isinstance(features, list)


# =========================
# TESTY resize_photo_for_analysis
# =========================

def test_resize_photo_scales_large_image(tmp_path):
    img = np.zeros((2000, 1000, 3), dtype=np.uint8)
    path = tmp_path / "img.png"
    cv.imwrite(str(path), img)

    resized, scale = resize_photo_for_analysis(str(path), max_dim=500)

    assert resized.shape[0] <= 500
    assert scale < 1.0
