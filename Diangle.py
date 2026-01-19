#Ten plik odpowiada wyłącznie za zdefiniowanie Diangle'ów oraz
#funkcje potrzebne do ich stworzenia lub porównywania.
#Funkcje porównujące faktycznie zdjęcia mają być w matching.py.
import math
import numpy  as np

from photos_opencv import detect_edge_features, open_photo, get_contours, extract_mask_and_contour
import cv2 as cv


#diangle - "dwójkąt" (słowo zmyślone) [powinny się nazwyać "jednokątami" bo mają tylko jeden kąt ale cicho...]
#opisuje trzy punkty, dwie łączące je krawędzie i kąt między nimi
#na ich podstawie będziemy dopasowywać ze sobą zdjęcia, chyba...
class Diangle:
    #typowy konstruktor, nie trzeba się nim martwić
    def __init__(self,center_coords,left_coords,right_coords,angle,type):
        self.x=center_coords[0]
        self.y=center_coords[1]
        self.xl=left_coords[0]
        self.yl=left_coords[1]
        self.xr=right_coords[0]
        self.yr=right_coords[1]
        self.angle=angle
        self.type=type
        self.left_arm = self.distance(self.x,self.y,self.xl,self.yl)
        self.right_arm = self.distance(self.x,self.y,self.xr,self.yr)

    #jakaś tam metoda do wypisywania
    def __str__(self):
            s=""
            s+="---DIANGLE---\n"
            s+=f"({self.xl},{self.yl}) -- ({self.x},{self.y}) -- ({self.xr},{self.yr})\n"
            s+=f"Left arm: {self.left_arm}, Right arm: {self.right_arm}\n"
            s+=f"Angle: {self.angle}\n"
            s+="-------------"
            return s


    #jakieś tam do liczenia dystansu
    @staticmethod
    def distance(x1,y1,x2,y2):
        return (abs(x1-x2)**2+abs(y1-y2)**2)**0.5


#AKTUALNE PROBLEMY: chyba brak?
def diangles_difference(d1, d2):

    #jak oba są wypukłe, albo oba wklęsłe, to nawet nie bierze ich pod uwagę
    if d1.type==d2.type:
        return 9999

    #wagi tego, jak dużo znaczą podobieństwa kąta i podobieństwa ramienia
    #na razie wszystko jest ustawione na tyle samo
    #można z tym poeksperymentować
    angle_wage = 0.4
    arm_wage = (1-angle_wage)/2

    #zabezpieczenie przed dzieleniem przez 0
    if d1.left_arm==0:
        d1.left_arm=0.001
    if d1.right_arm==0:
        d1.right_arm=0.001

    # Bardzo małe ramiona → zabezpieczenie
    d1_left = max(d1.left_arm, 1.0)
    d1_right = max(d1.right_arm, 1.0)
    d2_left = max(d2.left_arm, 1.0)
    d2_right = max(d2.right_arm, 1.0)

    # Miara różnicy długości ramion - wersja logarytmiczna (symetryczna, odporna na skalę)
    arm_diff1 = abs(math.log(d1_left / d2_right))
    arm_diff2 = abs(math.log(d1_right / d2_left))
    arm_score = (arm_diff1 + arm_diff2) / 2

    # Różnica kątów - zawsze bierzemy mniejszą wartość (uwzględniamy pełny okrąg)
    angle_diff = abs(d1.angle - d2.angle)
    angle_diff = min(angle_diff, 360 - angle_diff)

    #zabezpieczenie przed dzieleniem przez 0
    if d1.angle==0:
        d1.angle=180

    # Różnica kątów - zawsze bierzemy mniejszą wartość (uwzględniamy pełny okrąg)
    angle_diff = abs(d1.angle - d2.angle)
    angle_diff = min(angle_diff, 360 - angle_diff)

    angle_score = angle_diff / max(d1.angle, d2.angle, 10.0)

    score = arm_score * angle_wage + angle_score * arm_wage

    return score


# Sortuje punkty z features, żeby punkty dwójkątów były obok siebie
def sort_features_for_diangles(features, photo):

        #potrzebne listy, bierze kontur ze zdjęcia
        sorted_features = []
        contour = extract_mask_and_contour(photo)[1]
        all_points = []

        #wszystkie punkty z konturu
        for i in range(len(contour)):
            x=(contour[i][0][0])
            y=(contour[i][0][1])
            all_points.append((x,y))

        #wybrane punkty z konturu
        selected_points = []
        for i in range(len(features)):
            selected_points.append(features[i]['point'])

        #sortuje wybrane punkty na podstawie położenia ich w całym konturze
        for p in all_points:
            if p in selected_points:
                sorted_features.append(features[selected_points.index(p)])

        #zwraca tak posortowaną listę cech
        return sorted_features


#to zwraca zestaw "dwójkątów" dla jednego zdjęcia
def one_photo_diangles(photo):
    some_diangles = []
    features_bad = detect_edge_features(open_photo(photo))[0]

    #tu sobie sortuje cechy, aby diangle miały sens
    features = sort_features_for_diangles(features_bad, photo)

    #łączy punkty od [1] do przedostatniego w dwójkąty po trzy punkty
    for i in range(1,len(features)-1):
        type = features[i]["type"]
        center_coords = list(features[i]["point"])
        left_coords = list(features[i-1]["point"])
        right_coords = list(features[i + 1]["point"])
        angle = features[i]["angle_deg"]
        new_diangle = Diangle(center_coords,left_coords,right_coords,angle,type)
        some_diangles.append(new_diangle)

    #tu jeszcze łączy dwie ostatnei kropki z pierwszą
    last = features[-1]
    previous_to_last = features[-2]
    first = features[0]
    center_coords = list(last["point"])
    left_coords = list(previous_to_last["point"])
    right_coords = list(first["point"])
    angle = last["angle_deg"]
    type = last["type"]
    some_diangles.append(Diangle(center_coords,left_coords,right_coords,angle,type))

    #tu jeszcze łączy dwie pierwsze kropki z ostatnią
    second = features[1]
    center_coords = list(first["point"])
    left_coords = list(last["point"])
    right_coords = list(second["point"])
    angle = first["angle_deg"]
    type = first["type"]
    some_diangles.append(Diangle(center_coords, left_coords, right_coords, angle,type))

    return some_diangles

#to zwraca "dwójkąty" dla listy zdjęć
def all_photos_diangles(photos):
    all_diangles = []
    for photo in photos:
        #na razie wszystkie jest w zagnieżdżonej liście
        #ale nic nie stoi na przeszkodzie by zrobić z tego jakiś słownik potem
        all_diangles.append(one_photo_diangles(photo))
    return all_diangles




def is_convex(diangle, img=None, distance=20):
    """
    Bardzo prosta heurystyka: sprawdza czy 'na zewnątrz' diangla jest jaśniej/ciemniej
    Alternatywnie można sprawdzić signed area lub turning direction
    """
    cx, cy = diangle.x, diangle.y

    # kierunek na zewnątrz (prostopadły do bisectora ramion)
    dxl = diangle.xl - diangle.x
    dyl = diangle.yl - diangle.y
    dxr = diangle.xr - diangle.x
    dyr = diangle.yr - diangle.y

    # wektor bisector odwrócony (na zewnątrz)
    bx = -(dxl + dxr)
    by = -(dyl + dyr)
    norm = np.hypot(bx, by) + 1e-8
    bx /= norm
    by /= norm

    px = int(cx + bx * distance)
    py = int(cy + by * distance)

    if img is None or not (0 <= px < img.shape[1] and 0 <= py < img.shape[0]):
        return None  # nie wiemy

    outside_val = img[py, px]
    inside_val = img[cy, cx]  # w środku diangla

    # jeśli na zewnątrz jest wyraźnie jaśniej → raczej wypukły element puzzla
    return outside_val > inside_val + 25  # próg do tuningu


def improved_diangle_descriptor(d, img=None):
    len_l = np.hypot(d.xl - d.x, d.yl - d.y)
    len_r = np.hypot(d.xr - d.x, d.yr - d.y)

    if len_l < 3 or len_r < 3:
        return None

    # kąt między ramionami (najważniejszy)
    vec_l = np.array([d.xl - d.x, d.yl - d.y]) / len_l
    vec_r = np.array([d.xr - d.x, d.yr - d.y]) / len_r
    cos = np.clip(np.dot(vec_l, vec_r), -1.0, 1.0)
    angle = np.degrees(np.arccos(cos))

    ratio = min(len_l, len_r) / max(len_l, len_r)

    # kierunek bisectora (pomaga odróżnić orientację)
    bis = vec_l + vec_r
    bis /= np.linalg.norm(bis) + 1e-9
    direction = np.degrees(np.arctan2(bis[1], bis[0])) % 360

    convex = is_convex(d, img) if img is not None else None

    return {
        'angle': round(angle, 2),
        'arm_ratio': round(ratio, 3),
        'direction': round(direction, 1),
        'is_convex': convex,
        'arm_lengths': (round(len_l, 1), round(len_r, 1))
    }


def better_diangle_distance(desc1, desc2, weights=None):
    """
    Oblicza odległość między dwoma deskryptorami diangli
    Im mniejsza wartość, tym bardziej podobne diangle
    """
    if weights is None:
        weights = {'angle': 0.55, 'ratio': 0.30, 'direction': 0.15}

    # Najmniejszy kąt między kątami (uwzględniamy, że 0° i 180° mogą być podobne)
    da = min(
        abs(desc1['angle'] - desc2['angle']),
        180 - abs(desc1['angle'] - desc2['angle'])
    )

    # Różnica proporcji ramion
    dr = abs(desc1['arm_ratio'] - desc2['arm_ratio'])

    # Najmniejsza różnica kierunku (mod 360°)
    dd = min(
        abs(desc1['direction'] - desc2['direction']) % 360,
        360 - abs(desc1['direction'] - desc2['direction']) % 360
    )

    score = (
            weights['angle'] * (da / 30.0) +  # 30° = rozsądna maksymalna różnica kąta
            weights['ratio'] * dr +  # różnica proporcji 0..1
            weights['direction'] * (dd / 90.0)  # kierunek bisectora – najmniej pewny
    )

    return score