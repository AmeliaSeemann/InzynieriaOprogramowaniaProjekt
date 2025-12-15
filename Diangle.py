#Ten plik odpowiada wyłącznie za zdefiniowanie Diangle'ów oraz
#funkcje potrzebne do ich stworzenia lub porównywania.
#Funkcje porównujące faktycznie zdjęcia mają być w matching.py.
from photos_opencv import detect_edge_features, open_photo
import cv2 as cv
#diangle - "dwójkąt" (słowo zmyślone) [powinny się nazwyać "jednokątami" bo mają tylko jeden kąt ale cicho...]
#opisuje trzy punkty, dwie łączące je krawędzie i kąt między nimi
#na ich podstawie będziemy dopasowywać ze sobą zdjęcia, chyba...
class Diangle:
    #typowy konstruktor, nie trzeba się nim martwić
    def __init__(self,center_coords,left_coords,right_coords,angle):
        self.x=center_coords[0]
        self.y=center_coords[1]
        self.xl=left_coords[0]
        self.yl=left_coords[1]
        self.xr=right_coords[0]
        self.yr=right_coords[1]
        self.angle=angle
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


#AKTUALNE PROBLEMY: nie wiem, czy nie trzeba amieniać czasem ramion miejscami
#ani czy to odejmowanie drugiego kątu od 180 jest serio dobrym pomysłem

#do sprawdzania na ile dwa "dwójkąty" są od siebie różne
#czyli im MNIEJSZĄ liczbę zwraca, tym są podobniejsze
def diangles_difference(d1, d2):

    #wagi tego, jak dużo znaczą podobieństwa kąta i podobieństwa ramienia
    #na razie wszystko jest ustawione na tyle samo
    #można z tym poeksperymentować
    angle_wage = 0.33
    arm_wage = (1-angle_wage)/2

    #różnice względne między ramionami
    #trzeba będzie dopracować czy jakoś ich nie odwracać miejscami?
    left_arm_ratio = (abs(d1.left_arm - d2.left_arm)/d1.left_arm)*100
    right_arm_ratio = (abs(d1.right_arm - d2.right_arm)/d1.right_arm)*100

    #różnica względna między kątami
    #jeden jest wypukły a drugi wklęsły, więc dlatego "odwracamy" tu ten drugi
    real_d2_angle = d2.angle
    angle_ratio = (abs(d1.angle - real_d2_angle)/d1.angle)*100

    #zwraca to co wyżej tylko przemnożone przez tamte wagi
    return left_arm_ratio * arm_wage + right_arm_ratio * arm_wage + angle_ratio * angle_wage

#to zwraca zestaw "dwójkątów" dla jednego zdjęcia
def one_photo_diangles(photo):
    some_diangles = []
    features = detect_edge_features(open_photo(photo))[0]
    #łączy punkty od [1] do przedostatniego w dwójkąty po trzy punkty
    for i in range(1,len(features)-1):
        center_coords = list(features[i]["point"])
        left_coords = list(features[i-1]["point"])
        right_coords = list(features[i + 1]["point"])
        angle = features[i]["angle_deg"]
        new_diangle = Diangle(center_coords,left_coords,right_coords,angle)
        some_diangles.append(new_diangle)
    #tu jeszcze łączy dwie ostatnei kropki z pierwszą
    last = features[-1]
    previous_to_last = features[-2]
    first = features[0]
    center_coords = list(last["point"])
    left_coords = list(previous_to_last["point"])
    right_coords = list(first["point"])
    angle = last["angle_deg"]
    some_diangles.append(Diangle(center_coords,left_coords,right_coords,angle))

    #tu jeszcze łączy dwie pierwsze kropki z ostatnią
    second = features[1]
    center_coords = list(first["point"])
    left_coords = list(last["point"])
    right_coords = list(second["point"])
    angle = first["angle_deg"]
    some_diangles.append(Diangle(center_coords, left_coords, right_coords, angle))

    return some_diangles

#to zwraca "dwójkąty" dla listy zdjęć
def all_photos_diangles(photos):
    all_diangles = []
    for photo in photos:
        #na razie wszystkie jest w zagnieżdżonej liście
        #ale nic nie stoi na przeszkodzie by zrobić z tego jakiś słownik potem
        all_diangles.append(one_photo_diangles(photo))
    return all_diangles
