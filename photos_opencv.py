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

# wykrywanie krzywizny (cech)
def find_edge_features_from_curvature(contour, k=8, angle_thresh_deg=15, min_separation=10):
    """
    Ta funkcja bierze wyniki z poprzedniej i wybiera tylko najważniejsze miejsca (rogi, wcięcia, wypukłości).
    Można powiedzieć, że szuka tam, gdzie krawędź wygina się najmocniej i uznaje te miejsca za cechy charakterystyczne.

    Działa tak:
    1. Dostaje listę kątów skrętu
    2. Zamienia je na stopnie (żeby łatwiej się porównywało)
    3. Sprawdza:
        czy dany punkt wygina się bardziej niż sąsiednie
        i czy ten skręt jest większy niż ustalony próg (np. 15°)
    4. Jeśli tak – zapisuje ten punkt jako cechę krawędzi

    angle_thresh_deg – minimalny kąt, od którego uznajemy punkt za ważny
    min_separation – minimalna odległość między kolejnymi wykrytymi punktami

    Zwraca listę słowników z danymi o cechach krawędzi:
      [{ 'index': i, 'point': (x,y), 'type': 'protrusion'|'indentation', 'angle_deg': val, 'strength': abs(angle_rad) }, ...]
    """

    indices, curvatures, pts = compute_curvature(contour, k=k)
    if indices.size == 0:
        return []

    angle_deg = np.degrees(np.abs(curvatures))      # zamiana radianów na stopnie
    sign = np.sign(curvatures)  # -1 lub +1 (według implementacji wyżej)

    # bierzemy wartości bezwzględne
    abs_curv = np.abs(curvatures)

    N = len(abs_curv)
    candidates = []

    for i in range(N):
        # porównanie z punktami po lewej i prawej stronie
        left = abs_curv[(i-k)%N]
        right = abs_curv[(i+k)%N]
        if abs_curv[i] >= left and abs_curv[i] >= right and angle_deg[i] >= angle_thresh_deg:
            candidates.append((i, abs_curv[i], sign[i], angle_deg[i]))

    if not candidates:
        return []

    # sortuj po sile malejąco i wybierz z zachowaniem min_separation
    candidates.sort(key=lambda x: x[1], reverse=True)
    taken = np.zeros(N, dtype=bool)
    features = []

    # wybieramy tylko najważniejsze i oddalone od siebie punkty
    for idx, strength, sgn, angd in candidates:
        if taken[idx]:
            continue
        # zaznacz okolice jako zajęte
        start = (idx - min_separation) % N
        end = (idx + min_separation) % N
        # blokujemy sąsiednie punkty, żeby nie dublować wykryć
        for j in range(idx - min_separation, idx + min_separation + 1):
            taken[j % N] = True

        ftype = 'protrusion' if sgn < 0 else 'indentation'
        # protrusion = wypukłość
        # indentation = wklęsłość

        features.append({
            'index': int(idx),
            'point': tuple(map(int, pts[idx])),     # współrzędne punktu
            'type': ftype,
            'angle_deg': float(angd),
            'strength': float(strength)
        })

    return features
