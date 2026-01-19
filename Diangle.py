#Ten plik odpowiada wyłącznie za zdefiniowanie Diangle'ów oraz
#funkcje potrzebne do ich stworzenia lub porównywania.
#Funkcje porównujące faktycznie zdjęcia mają być w matching.py.
import math

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

