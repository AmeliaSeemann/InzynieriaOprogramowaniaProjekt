import numpy as np
import numbers

from matching import (
    adjust_photos,
    rotate_and_clean,
    calculate_rotation_degree,
    calculate_vector,
    join_photos
)



# Pomocnicza klasa testowa

class FakeDiangle:

    def __init__(self, x, y, xl, yl, xr, yr):
        self.x = x
        self.y = y
        self.xl = xl
        self.yl = yl
        self.xr = xr
        self.yr = yr


# =========================
# TESTY adjust_photos
# =========================

def test_adjust_photos_same_size():
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)

    out1, out2 = adjust_photos(img1, img2)

    assert out1.shape == out2.shape
    assert out1.shape == (100, 100, 3)


def test_adjust_photos_different_size():
    img1 = np.zeros((50, 120, 3), dtype=np.uint8)
    img2 = np.zeros((100, 80, 3), dtype=np.uint8)

    out1, out2 = adjust_photos(img1, img2)

    assert out1.shape == out2.shape
    assert out1.shape[0] == 100
    assert out1.shape[1] == 120


# TESTY rotate_and_clean

def test_rotate_and_clean_returns_image():
    img = np.zeros((100, 200, 3), dtype=np.uint8)

    rotated = rotate_and_clean(img, 45)

    assert rotated is not None
    assert rotated.shape[0] > 0
    assert rotated.shape[1] > 0


def test_rotate_and_clean_preserves_channels():
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    rotated = rotate_and_clean(img, 90)

    assert rotated.shape[2] == 3

# TESTY calculate_rotation_degree

def test_calculate_rotation_degree_valid_input():
    d1 = FakeDiangle(60, 40, 30, 80, 90, 70)
    d2 = FakeDiangle(55, 45, 35, 85, 95, 75)

    angle1, angle2 = calculate_rotation_degree(d1, d2)

    assert angle1 is not None
    assert angle2 is not None



# TESTY calculate_vector

def test_calculate_vector_returns_two_ints():
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)

    # Rysujemy WIĘKSZĄ czerwoną kropkę (3x3)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            img1[50+dy, 50+dx] = [0, 0, 255]
            img2[50+dy, 50+dx] = [0, 0, 255]

    x, y = calculate_vector(img1, img2)

    assert isinstance(x, numbers.Integral)
    assert isinstance(y, numbers.Integral)


# TESTY join_photos

def test_join_photos_returns_image():
    img1 = np.zeros((50, 50, 4), dtype=np.uint8)
    img2 = np.zeros((50, 50, 4), dtype=np.uint8)

    # Dodajemy alfa > 0, żeby coś było widoczne
    img1[:, :, 3] = 255
    img2[:, :, 3] = 255

    result = join_photos(img1, img2, 0, 0)

    assert result is not None
    assert result.shape[0] > 0
    assert result.shape[1] > 0
