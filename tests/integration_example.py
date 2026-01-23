import cv2
import numpy as np

from matching import (
    adjust_photos,
    join_photos
)

# =========================
# Przygotowanie danych
# =========================

img1 = np.zeros((120, 200, 4), dtype=np.uint8)
img2 = np.zeros((120, 200, 4), dtype=np.uint8)

# białe prostokąty (widoczne)
cv2.rectangle(img1, (40, 30), (160, 90), (255, 255, 255, 255), -1)
cv2.rectangle(img2, (20, 50), (140, 110), (255, 255, 255, 255), -1)

cv2.imwrite("integration_input_1.png", img1)
cv2.imwrite("integration_input_2.png", img2)

# =========================
# Integracja funkcji
# =========================

# wyrównanie rozmiarów
img1_adj, img2_adj = adjust_photos(img1, img2)

# ręcznie dobrany wektor przesunięcia (kontrolowany)
dx, dy = 0, 0

# łączenie obrazów
result = join_photos(img1_adj, img2_adj, dx, dy)

cv2.imwrite("integration_result.png", result)

print("Test integracyjny zakończony poprawnie")
