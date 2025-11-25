#W tym pliku powinny być same rzeczy wykorzystujące opencv
#Czyli na przykład szukanie krawędzi zdjęć, algorytmy dopasowywania itp.

import cv2 as cv


#wygląda na bezużyteczne, ale potrzebne to przetestowania nazw plików
def open_photo(photo):
    return cv.imread(photo)

def get_contours(photo):
    # znajdywanie konturów zdjęcia
    img = open_photo(photo)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    contours = cv.findContours(image=img_gray, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)[0]
    contours_x = contours[0][:, :, 0]
    contours_y = contours[0][:, :, 1]
    return contours_x, contours_y

#zwraca koordynaty potrzebne do przycięcia zdjęć z przezroczystym tłem
def get_crop(photo):
    img = cv.imread(photo, cv.IMREAD_UNCHANGED)
    if img is None:
        return None     # plik nie istnieje lub nie jest zdjęciem

    # obraz ma kanał alfa = PNG z przezroczystością
    if img.shape[2] == 4:
        # wyciągamy kanał alfa (odpowiada za przezroczystość)
        alpha = img[:, :, 3]

        # tworzymy binarną maskę:
        # piksele > 1 traktujemy jako należące do kształtu
        _, thresh = cv.threshold(alpha, 1, 255, cv.THRESH_BINARY)
    else:
        # brak kanału alfa - konwertujemy do grayscale
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray, 250, 255, cv.THRESH_BINARY_INV)

    # znajduje kontury
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None       # nic nie znaleziono - prawdopodobnie puste zdjęcie

    # wybieramy największy kontur, zakładając że jest właściwym obiektem
    cnt = max(contours, key=cv.contourArea)

    # pobieramy minimalny prostokąt otaczający kontur
    x, y, w, h = cv.boundingRect(cnt)

    return x, y, w, h
