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

#  wykrywanie krawędzi
#  krzywizna krawędzi
def compute_curvature(contour, k=8):
    """
    Przechodzi punkt po punkcie po krawędzi obiektu i sprawdza, jak bardzo i w którą stronę skręca linia w każdym miejscu.

    Dla każdego punktu na krawędzi:
        Bierze punkt przed nim (k punktów wstecz)
        Bierze punkt za nim (k punktów do przodu)
        Patrzy, jaki kąt tworzą te trzy punkty
    Czyli trochę tak, jakby:
        - stanął w jednym punkcie krawędzi
        - spojrzał, skąd przyszedł
        - i dokąd dalej idzie krawędź
        - i zmierzył „zakręt”
    Potem zapisuje:
        - jak duży to skręt (kąt)
        - w którą stronę (wypukłość czy wklęsłość)
    Na końcu zwraca:
        - indeksy punktów konturu
        - kąty skrętu w tych punktach
        - współrzędne punktów
    Czyli: mapa „skręcalności” krawędzi.
    Uwaga: im większe k -> bardziej wygładzone oszacowanie (bardziej globalne), mniejsze k -> bardziej lokalne.
    """
    pts = contour.reshape(-1, 2)
    N = len(pts)

    # jeśli punktów jest za mało – nie da się nic policzyć
    if N < 2*k + 1:
        return np.array([]), np.array([]), np.array([])

    indices = np.arange(N)
    curvatures = np.zeros(N, dtype=float)       # tu będą zapisane kąty

    # przechodzimy przez każdy punkt po kolei
    for i in range(N):
        # wybór punktu przed i po aktualnym punkcie
        i_prev = (i - k) % N
        i_next = (i + k) % N

        p_prev = pts[i_prev].astype(float)
        p = pts[i].astype(float)
        p_next = pts[i_next].astype(float)

        v1 = p - p_prev
        v2 = p_next - p

        # długości wektorów
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 == 0 or n2 == 0:      # jeśli któryś wektor ma długość 0 - pomijamy
            curvatures[i] = 0.0
            continue

        v1_u = v1 / n1
        v2_u = v2 / n2

        # kąt między wektorami
        dot = np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)
        angle = math.acos(dot)  # zawsze >= 0

        # sprawdzamy, czy to wypukłość, czy wklęsłość (znak kąta)
        cross = v1_u[0]*v2_u[1] - v1_u[1]*v2_u[0]

        # jeśli cross < 0 to wypukłość, jeśli >= 0 to wklęsłość
        signed_angle = angle if cross < 0 else -angle

        # zapisujemy końcową wartość krzywizny
        curvatures[i] = signed_angle

    # zwracamy wszystkie wartości
    return indices, curvatures, pts
