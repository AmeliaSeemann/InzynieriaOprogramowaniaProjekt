#Tu mają być funkcje, które dostają zdjęcia jako argumenty, tworzą im
#"dwójkąty", a potem porównują i może wyświetlają wyniki tego.

from Diangle import all_photos_diangles,diangles_difference
from photos_opencv import open_photo
import cv2 as cv
import numpy as np
from sympy import symbols, Eq, solve


#AKTUALNE PROBLEMY: poczytaj sobie w draw_matches() i calculate_rotation_angle()

def true_match_all_photos(photos):
    #do tego, ile topowych dopasować wyświetlić (żeby nie wysadzić terminala)
    number_of_top_matches = 100

    #zdobywa wszystkie diangle
    all_diangles = all_photos_diangles(photos)
    current_photo=0

    #do przechowywania wyników
    matches = []
    try:
        #troche skomplikowany ten for ale spokojnie
        for photo in all_diangles:
            current_diangle=0
            for d1 in photo:
                for i in range(0,len(all_diangles)):
                    #to jest, żeby zdjęcie nie przeszukiwało podobieństwa ze
                    #samym sobą
                    if i==current_photo:
                        continue
                    else:
                        #tu konkretny diangle z jednego zdjęcia przeszukuje
                        #wszystkei diangle innych zdjęć
                        for j in range(len(all_diangles[i])):
                            d2 = all_diangles[i][j]

                            #oblicza podobieństwo aktualnego diangle'a
                            #i sprawdzanego
                            diff = diangles_difference(d1, d2)
                            single_match = {}

        #np. {'Difference':12,'Point1':[0,100],'Point2':[10,80],'Photo1':0,'Photo2':2'}
        #znaczy, że na zdjęciu 0 punkt o współrzędnych [0,100] ma różnicę 12 z punktem
        #na zdjęciu 2 o współrzędnych [10,80].
                            single_match["Difference"] = diff
                            single_match["Point1"] = [d1.x,d1.y]
                            single_match["Point2"] = [d2.x, d2.y]
                            single_match["Photo1"] = current_photo
                            single_match["Photo2"] = i
                            single_match["diangle1"] = d1
                            single_match["diangle2"] = d2
                            matches.append(single_match)
                current_diangle += 1
            current_photo += 1

        #sotruje dopasowania według podobieństwa malejąco
        sorted_matches = sorted(matches, key=lambda d: d['Difference'])

        #wyświetla tylko ileś topowych dopasowań, bo wszystkie się nie mieszczą
        # print("Sorted matches:")
        # for k in range(number_of_top_matches):
        #     print(sorted_matches[k])
        return sorted_matches

    #to tak na wszelki wypadek bo wcześniej było parę problemów
    except Exception as e:
        print("Ups:",e)
        return None


#do rysowania pojedyńczego diangla
def draw_diangle(photo,diangle):
    #lewe ramie
    img1 = cv.line(photo,(diangle.x,diangle.y),(diangle.xl,diangle.yl),(255,0,0),5)
    #nakłada jeszcze prawe ramie
    img2 = cv.line(img1, (diangle.x, diangle.y), (diangle.xr, diangle.yr), (0, 255, 0), 5)
    #nakłada środek
    img3 = cv.circle(img2,(diangle.x,diangle.y),5,(0,0,255),-1)
    #zwraca obraz z rysunkiem
    return img3

#do rysowania pojedyńczej kropki, przydatne w łączeniu zdjęć
def draw_dot(photo,x,y):
    img = cv.circle(photo,(x,y),1,(0,0,255),-1)
    return img

#ma rysować Point1 na Photo1
#rysować Point2 na Photo2
#jakoś połączyć te dwa zdjęcia i pokazać czy match ma wogóle sens
def draw_matches(matches,photos):

    n=40 #ile "najlepszych" dopasowań chcemy pokazać
    print(f"Pokazujemy {n} najlepszych match'y, możesz to zmienić w funkcji draw_matches w matching.py :)")
    print(matches[:n])

    for i in range(n):
        #rysuje Point1 na Photo1
        photo1 = open_photo(photos[matches[i]['Photo1']])
        diangle1 = matches[i]['diangle1']

        # te zdjecie do pokazania
        left_image_vis = draw_diangle(photo1.copy(),diangle1)

        # te do realnych działań za kulisami
        left_image = cv.cvtColor(photo1, cv.COLOR_BGR2GRAY)
        left_image = cv.cvtColor(left_image, cv.COLOR_GRAY2BGR)
        left_image = draw_dot(left_image,diangle1.x,diangle1.y)


        # rysuje Point2 na Photo2
        photo2 = open_photo(photos[matches[i]['Photo2']])
        diangle2 = matches[i]['diangle2']

        #te zdjecie do pokazania
        right_image_vis = draw_diangle(photo2.copy(),diangle2)

        #te do realnych działań za kulisami
        right_image = cv.cvtColor(photo2, cv.COLOR_BGR2GRAY)
        right_image = cv.cvtColor(right_image, cv.COLOR_GRAY2BGR)
        right_image = draw_dot(right_image, diangle2.x, diangle2.y)

        #łączy dwa zdjęcia (te do wizualizacji dla nas)
        vis = np.concatenate((left_image_vis, right_image_vis), axis=1)

        #tu będzie obracanie prawego zdjęcia
        #trzeba będzie to zrobić na bazie calculate_rotation_degree()
        #tamta funkcja zwraca dwa kąty, trzeba to będzie przetestować dla obu
        #to drugie zdjęcie będzie też mogło zmienić swój rozmiar abyśmy przy obróceniu
        #nie stracili żadnych informacji
        #tymczasowo zostawiamy to tak:

        angle1,angle2 = calculate_rotation_degree(diangle1,diangle2)
        rotated_right_image1 = right_image #dla angle1 będzie
        rotated_right_image2 = right_image #dla angle2 będzie

        # obliczanie o ile trzeba przesunąć to prawe zdjęcie, jak będzie już obrócone
        x,y = calculate_vector(left_image,rotated_right_image1)
        print(f"How to move right image: {x} on X-axis, {y} on Y-axis")
        #te przesunięcia trzeba będzie zrobić dla obu przypadków obrócenia
        #potem trzeba rozkminić jakoś jak zrobić te zdjęcia przezroczystymi i nałożyć
        #siebie czy coś

        #potem się sprawdzi dla którego przypadku po przesunięciu stracono mniej tła
        #(czyli zdjęcia się mniej nałożyły czyli lepiej pasowały)
        #to będzie ten dobry przypadek obrócenia, drugi się odrzuci

        #tu wizualizuje dopasowanie (ale jeszcze nie tych obróconych zdjęć)
        #(w przyszłości się tu zwizualizuje ten dobry przypadek obrócenia i przeniesienia)
        cv.imshow("Jestem zdjęciem",vis)
        cv.waitKey(0)
        cv.destroyAllWindows()



#oblicza, o ile stopni ma się obrócić drugie zdjęcie, na podstawie ich dianglów
def calculate_rotation_degree(d1,d2):

    # to się dzieje na bazie jakiejś matematyki której na ten moment już nie kumam
    # ale ostatecznie zwraca sensowne wyniki, kiedyś to było dla mnie zrozumiałe,
    # teraz nieco mniej


    #tu liczy jakieś równanie prostej łączącej lewy i prawy wierzchołek diangla
    a1,b1=symbols('a1,b1')
    eq1_l = Eq((a1 * d1.xl + b1), d1.yl)
    eq1_r = Eq((a1 * d1.xr + b1), d1.yr)
    sol1 = solve((eq1_l, eq1_r), (a1, b1))


    #tutaj liczy jakąś prostą łączącą środkowy wierzchołek z tamtą prostą wyżej?
    b1_up = d1.y - (1 / sol1[a1]) * d1.x
    a1_up = 1/sol1[a1]

    #magią pitagorasa i trygonometri oblicza kąt pod jakim jest zdjęcie??
    x1_hit = -1*b1_up/a1_up
    c_bok = (d1.y ** 2 + (d1.x - x1_hit) ** 2) ** 0.5
    ratio1 = d1.y / c_bok
    if d1.x-x1_hit<0:
        alpha = 180-np.degrees(np.arccos(np.float64(ratio1)))
    else:
        alpha = np.degrees(np.arccos(np.float64(ratio1)))


    #<JAK WYŻEJ>
    a2, b2 = symbols('a2,b2')
    eq2_l = Eq((a2 * d2.xl + b2), d2.yl)
    eq2_r = Eq((a2 * d2.xr + b2), d2.yr)
    sol2 = solve((eq2_l, eq2_r), (a2, b2))
    b2_up = d2.y - (1 / sol2[a2]) * d2.x
    a2_up = 1/sol2[a2]
    x2_hit = -1 * b2_up / a2_up
    c_bok = (d2.y**2+(d2.x-x2_hit)**2)**0.5
    ratio2 = d2.y/c_bok
    if d2.x-x2_hit<0:
        beta = 180-np.degrees(np.arccos(np.float64(ratio2)))
    else:
        beta = np.degrees(np.arccos(np.float64(ratio2)))


    #PROBLEM: czasem pasuje kąt difference, a czasem difference+180
    #Nie wiem na jakiej podstawie wybiera się ten właściwy
    #Bierzemy więc dwa i potem w draw_matches() się wybierze lepszy, jakoś

    #różnica między kątem obu zdjęć
    difference = alpha-beta

    #druga potencjalna różnica między kątem obu zdjęć
    difference2 = difference + 180

    #zwraca obie, potem się jakoś sprawdzi która jest lepsza
    return difference,difference2


# do policzenia o ile trzeba przesunąć prawe zdjęcie względem lewego
# wrzucane zdjecia są czarnobiałe i mają zaznaczony środek dwójkąta czerwoną kropką
# robimy takie coś, bo te zdjęcie wcześnej mogą zostać obrócone albo powiększone,
# więc nie możemy polegać na współrżednej środka dwójkąta trzeba go samemu odnaleźć
def calculate_vector(p1,p2):

    #znajduje czerwone punkty na pierwszym zdjęciu
    img_hsv = cv.cvtColor(p1, cv.COLOR_BGR2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv.inRange(img_hsv, lower_red, upper_red)
    red_points = np.where(mask == 255)

    #bierze punkt, który jest środkiem czerwonej kropki więc też środkiem dwójkąta
    y1,x1 = red_points[0][2], red_points[1][2]

    # znajduje czerwone punkty na drugim zdjęciu
    img_hsv = cv.cvtColor(p2, cv.COLOR_BGR2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv.inRange(img_hsv, lower_red, upper_red)
    red_points = np.where(mask == 255)

    # bierze punkt, który jest środkiem czerwonej kropki więc też środkiem dwójkąta
    y2,x2 = red_points[0][2], red_points[1][2]

    # oblicza o ile trzeba przesunąć prawe zdjęcie aby dopasować jego czerwoną kropkę
    # z tym po lewej
    width1 = p1.shape[1]
    width_difference = -(width1-x1+x2)
    height_difference = y2-y1

    # zwraca tą informację
    return width_difference,height_difference

