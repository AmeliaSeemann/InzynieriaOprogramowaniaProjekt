import cv2 as cv
import numpy as np
import math


def open_photo(photo):
    return cv.imread(photo, cv.IMREAD_UNCHANGED)

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

def extract_mask_and_contour(photo,from_path=True):
    """
    Zwraca (mask, contour) gdzie:
     - mask: binarna maska (0/255) obiektu wycieta z calego obrazu
     - contour: lista punktow (numpy array Nx1x2) największego konturu
    Zwraca (None, None) jeśli nie uda sie wczytac.
    """

    #w zależności od tego, czy mamy wczytane zdjęcie czy
    #wczytujemy je ze ścieżki
    if from_path or type(photo) == str:
        img = open_photo(photo)
        if img is None:
            return None, None
    else:
        img = photo

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


#dodatkowo: convexity defects (wcięcia względem wypukłej otoczki)
def convexity_defects_list(photo):
    """
    https://docs.opencv.org/4.x/d5/d45/tutorial_py_contours_more_functions.html
    Funkcja znajduje wcięcia kształtu względem jego wypukłej otoczki (convex hull).
    Zwraca listę punktów:
    - start wcięcia
    - koniec wcięcia
    - najgłębszy punkt wcięcia (najbardziej w środku)
    - głębokość wcięcia

    Jest to przydatne do wykrywania charakterystycznych wgłębień obiektu.
    """

    # pobranie maski i konturu obiektu ze zdjęcia
    _, contour = extract_mask_and_contour(photo)
    if contour is None:
        return []

    cnt = contour
    hull = cv.convexHull(cnt, returnPoints=False)

    # szukamy różnic między prawdziwym kształtem a wypukłą wersją
    # czyli wykrywamy wcięcia (defekty)
    defects = cv.convexityDefects(cnt, hull)

    res = []
    for i in range(defects.shape[0]):
        # s – indeks punktu początkowego wcięcia
        # e – indeks punktu końcowego wcięcia
        # f – indeks punktu najgłębszego
        # depth – głębokość wcięcia
        s, e, f, depth = defects[i, 0]

        # współrzędne punktów na obrazie
        start_pt = tuple(cnt[s][0])
        end_pt = tuple(cnt[e][0])
        far_pt = tuple(cnt[f][0])

        # zapisujemy informacje o wcięciu do listy
        res.append({
            'start_idx': int(s),  # indeks początku wcięcia
            'end_idx': int(e),  # indeks końca wcięcia
            'far_idx': int(f),  # indeks najgłębszego punktu
            'start_pt': start_pt,  # współrzędne początku
            'end_pt': end_pt,  # współrzędne końca
            'far_pt': far_pt,  # współrzędne najgłębszego punktu
            'depth': int(depth)  # głębokość wcięcia
        })

    return res


# wizualizacja cech na obrazie
def draw_features(photo, features, out_bgr=None, contour=None):
    """
    Rysuje features (lista słowników zwróconych przez find_edge_features_from_curvature)
    na obrazie i zwraca obraz BGR (numpy).
    Czyli:
    - obrys obiektu (kontur),
    - ważne punkty: wypukłości i wcięcia,
    - małe opisy przy tych punktach.
    """

    if out_bgr is None:
        img = open_photo(photo)
        if img is None:
            return None
        # jeśli alpha -> konwert do BGR do rysowania
        if img.ndim == 3 and img.shape[2] == 4:
            img_bgr = cv.cvtColor(img[:, :, :3], cv.COLOR_BGR2RGB)
            img_bgr = cv.cvtColor(img[:, :, :3], cv.COLOR_BGRA2BGR) if False else img[:, :, :3].copy()
        else:
            img_bgr = img.copy()
    else:
        img_bgr = out_bgr.copy()

    # rysuj kontur
    if contour is not None:
        cv.drawContours(img_bgr, [contour], -1, (0, 255, 0), 2)     #zielony kolor

    for f in features:
        x, y = f['point']
        if f['type'] == 'protrusion':   #wypukłość
            color = (255, 0, 0)  # niebieski kolor
        else:   #wklęsłość
            color = (0, 0, 255)  # czerwony kolor

        # typ + kąt
        cv.circle(img_bgr, (x, y), 6, color, -1)
        cv.putText(img_bgr, f"{f['type'][0]}:{int(f['angle_deg'])}", (x+8, y-8),
                   cv.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv.LINE_AA)
    return img_bgr

# wywołanie rysowania konturów
def detect_edge_features(photo, k=8, angle_thresh_deg=15, min_separation=10, visualize=False):
    """
    zwraca features i obraz z narysowanymi cechami.
    """
    mask, contour = extract_mask_and_contour(photo,False)

    features = find_edge_features_from_curvature(contour, k=k, angle_thresh_deg=angle_thresh_deg,
                                                min_separation=min_separation)

    vis = None
    if visualize:
        vis = draw_features(photo, features, contour=contour)
    return features, vis


#Jako argument bierze listę ścieżek do plików
#Zwraca graf dopasowań, czyli taki słownik gdzie jest napisane
#które zdjęcie łączy sięz któym i jakim punktem?
#Ogólnie to coś może być nie tak z działaniem tej funkcji, bo dopiero
#po zwiększeniu max_dist faktycznie coś znajduje, mimo że na bank mamy
#punkty co leżą bliżej niż 50 pikseli od siebie
def match_all_photos_features(photos, k=10, angle_thresh_deg=15, min_separation=12, max_dist=50):
    """
    Dopasowuje cechy wszystkich zdjęć między sobą.
    Zwraca graf dopasowań:
    """
    features_list = []
    for photo in photos:
        resized_photo, scale = resize_photo_for_analysis(photo, max_dim=800)
        features, _ = detect_edge_features(resized_photo, k=10, angle_thresh_deg=15, min_separation=12)
        # zachowanie punktow w oryginalnym rozmiarze
        for f in features:
            f['point'] = (int(f['point'][0] / scale), int(f['point'][1] / scale))
        features_list.append(features)
    matches_graph = {i: {} for i in range(len(photos))}

    for i in range(len(photos)):
        for j in range(len(photos)):
            if i == j:
                continue
            matches = []
            for f_i in features_list[i]:
                for f_j in features_list[j]:
                    # wypustka pasuje do wcięcia i odwrotnie
                    if f_i['type'] == 'protrusion' and f_j['type'] == 'indentation':
                        dx = f_i['point'][0] - f_j['point'][0]
                        dy = f_i['point'][1] - f_j['point'][1]
                        dist = (dx**2 + dy**2)**0.5
                        if dist <= max_dist:
                            matches.append((f_i, f_j))
            matches_graph[i][j] = matches
    return matches_graph


#Jako argument bierze ścieżki do plików
#Zwraca liste która składa się z takich
# {zdjecie1,zdjecie2,cechyRoguZdjecia1,cechyRoguZdjecia2,dystans}
#Działać działa, ale czy dobrze to należy przetestować
def get_sorted_matches(photos, k=10, angle_thresh_deg=15, min_separation=12, max_dist=50):

    #Tworzy listę dopasowań między cechami wszystkich zdjęć i sortuje je według odległości.
    #trzeba dodac funkcje do tego

    features_list = []
    for photo in photos:
        photo = open_photo(photo)
        features, _ = detect_edge_features(photo, k=k, angle_thresh_deg=angle_thresh_deg, min_separation=min_separation)
        features_list.append(features)

    sorted_matches = []

    for i in range(len(photos)):
        for j in range(len(photos)):
            if i == j:
                continue
            for f_i in features_list[i]:
                for f_j in features_list[j]:
                    if f_i['type'] == 'protrusion' and f_j['type'] == 'indentation':
                        dx = f_i['point'][0] - f_j['point'][0]
                        dy = f_i['point'][1] - f_j['point'][1]
                        dist = (dx**2 + dy**2)**0.5
                        if dist <= max_dist:
                            sorted_matches.append((i, j, f_i, f_j, dist))

    # sortowanie po odległości rosnąco
    sorted_matches.sort(key=lambda x: x[4])
    return sorted_matches


def resize_photo_for_analysis(photo, max_dim=800):
    """
    Skaluje zdjęcie tak, żeby największy wymiar nie przekroczył max_dim.
    """
    photo = cv.imread(photo)
    h, w = photo.shape[:2]
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv.resize(photo, (new_w, new_h), interpolation=cv.INTER_AREA)
        return resized, scale
    else:
        return photo.copy(), 1.0

#Do testowania funkcji match_all_photo_features, w któej coś trzeba naprawić
# import os
# folder = "zdjecia/foto_testowe"
# max_distance = 100
# photos = []
# for filename in os.listdir(folder):
#     photos.append(os.path.join(folder, filename))
# print(match_all_photos_features(photos=photos,max_dist=max_distance))

