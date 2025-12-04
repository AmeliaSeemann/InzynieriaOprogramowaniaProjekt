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

def extract_mask_and_contour(photo):
    """
    Zwraca (mask, contour) gdzie:
     - mask: binarna maska (0/255) obiektu wycieta z calego obrazu
     - contour: lista punktow (numpy array Nx1x2) największego konturu
    Zwraca (None, None) jeśli nie uda sie wczytac.
    """
    img = open_photo(photo)
    if img is None:
        return None, None

    # jeśli jest alfa - użyjemy kanału alfa jako maski
    if img.ndim == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        _, mask = cv.threshold(alpha, 1, 255, cv.THRESH_BINARY)
    else:
        # konwertujemy do odcieni szarości
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        _, mask = cv.threshold(gray, 250, 255, cv.THRESH_BINARY_INV)

    # znajdź wszystkie kontury
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    if not contours:
        return mask, None

    # wybierzemy największy kontur
    contour = max(contours, key=cv.contourArea)
    return mask, contour

#kształt nie jest tylko obrazem, tylko zestawem matematycznych krawędzi do dopasowania
def get_edge_vectors(contour, step=30):

    vectors = []

    if contour is None or len(contour) < step + 1:
        return vectors

    for i in range(0, len(contour) - step, step):
        p1 = contour[i][0]
        p2 = contour[i + step][0]

        dx = int(p2[0]) - int(p1[0])
        dy = int(p2[1]) - int(p1[1])

        length = (dx ** 2 + dy ** 2) ** 0.5

        vectors.append((p1, p2, (dx, dy), length))

    return vectors


def vectors_match(vec1, vec2, dir_tolerance=15, len_tolerance=20):
    """
    vec1, vec2 = (p1, p2, (dx, dy), length)
    Sprawdza czy dwa wektory są do siebie przeciwne i mają podobną długość
    """

    dx1, dy1 = vec1[2]
    dx2, dy2 = vec2[2]

    l1 = vec1[3]
    l2 = vec2[3]

    # kierunek przeciwny (dx1 ≈ -dx2 i dy1 ≈ -dy2)
    direction_ok = (abs(dx1 + dx2) < dir_tolerance) and (abs(dy1 + dy2) < dir_tolerance)

    # podobna długość
    length_ok = abs(l1 - l2) < len_tolerance

    return direction_ok and length_ok