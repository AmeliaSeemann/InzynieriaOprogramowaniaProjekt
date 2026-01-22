import numbers
import math

from Diangle import Diangle, diangles_difference

#Testy klasy Diangle
def test_diangle_constructor_sets_fields():
    d = Diangle(
        center_coords=(10, 10),
        left_coords=(5, 10),
        right_coords=(15, 10),
        angle=90,
        type=1
    )

    assert d.x == 10
    assert d.y == 10
    assert d.xl == 5
    assert d.yl == 10
    assert d.xr == 15
    assert d.yr == 10
    assert d.angle == 90
    assert d.type == 1

#Test długości ramion
def test_diangle_arm_lengths_are_positive():
    d = Diangle(
        center_coords=(0, 0),
        left_coords=(-3, 0),
        right_coords=(4, 0),
        angle=60,
        type=0
    )

    assert d.left_arm > 0
    assert d.right_arm > 0

#Test metody distance
def test_distance_calculation():
    dist = Diangle.distance(0, 0, 3, 4)

    assert math.isclose(dist, 5.0)

#Test diangles_difference — ten sam typ
def test_diangles_difference_same_type_returns_large_value():
    d1 = Diangle((0, 0), (-1, 0), (1, 0), 60, type=1)
    d2 = Diangle((0, 0), (-2, 0), (2, 0), 60, type=1)

    diff = diangles_difference(d1, d2)

    assert diff >= 9999

#Test diangles_difference — różne diangle
def test_diangles_difference_different_type_returns_number():
    d1 = Diangle((0, 0), (-2, 0), (2, 0), 60, type=0)
    d2 = Diangle((1, 1), (-1, 1), (3, 1), 65, type=1)

    diff = diangles_difference(d1, d2)

    assert isinstance(diff, numbers.Number)
    assert diff >= 0

# odpornośc na zero
def test_diangles_difference_handles_zero_values():
    d1 = Diangle((0, 0), (0, 0), (0, 0), 0, type=0)
    d2 = Diangle((1, 1), (2, 1), (1, 2), 45, type=1)

    diff = diangles_difference(d1, d2)

    assert diff >= 0
