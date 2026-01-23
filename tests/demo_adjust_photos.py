import cv2
import numpy as np
from matching import adjust_photos

img1 = np.zeros((50, 120, 3), dtype=np.uint8)
img2 = np.zeros((100, 80, 3), dtype=np.uint8)

out1, out2 = adjust_photos(img1, img2)

cv2.imwrite("before_1.png", img1)
cv2.imwrite("before_2.png", img2)
cv2.imwrite("after_1.png", out1)
cv2.imwrite("after_2.png", out2)

print("Zapisano obrazy przed i po dopasowaniu.")
