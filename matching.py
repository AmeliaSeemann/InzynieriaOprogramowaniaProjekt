#Tu mają być funkcje, które dostają zdjęcia jako argumenty, tworzą im
#"dwójkąty", a potem porównują i może wyświetlają wyniki tego.
import math

from Diangle import all_photos_diangles,diangles_difference
from photos_opencv import open_photo
import cv2 as cv
import numpy as np
from sympy import symbols, Eq, solve
from scipy import ndimage


#AKTUALNE PROBLEMY: na bank dopasowuje kąty proste i półproste jako ~idealne~,
#więc jak jakieś zdjęcie jest "na rogu" to stwierdzi że pasuje do innego zdjęcia
#"na rogu", nawet jak są to zupełnie przeciwne rogi obrazka

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
        left_image = draw_diangle(photo1,diangle1)

        # rysuje Point2 na Photo2
        photo2 = open_photo(photos[matches[i]['Photo2']])
        diangle2 = matches[i]['diangle2']
        right_image = draw_diangle(photo2,diangle2)

        #oblicza, o ile stopni trzeba obrócić drugie zdjęcie
        degrees = rotate_match(diangle1, diangle2)

        # #obraca je
        right_image = ndimage.rotate(right_image, -degrees,reshape=False)

        #łączy dwa zdjęcia
        vis = np.concatenate((left_image, right_image), axis=1)

        #wizualizuje dopasowanie
        cv.imshow("Match",vis)
        cv.waitKey(0)
        cv.destroyAllWindows()



#oblicza, o ile stopni ma się obrócić drugie zdjęcie
def rotate_match(d1,d2):
    #yyyy....yyy???....???hmmm???
    desc = ""

    #tu liczy jakieś równanie prostej łączącej lewy i prawy wierzchołek diangla
    a1,b1=symbols('a1,b1')
    eq1_l = Eq((a1 * d1.xl + b1), d1.yl)
    eq1_r = Eq((a1 * d1.xr + b1), d1.yr)
    sol1 = solve((eq1_l, eq1_r), (a1, b1))
    #print(f"l1: y={sol1[a1]}x+{sol1[b1]}")

    #tutaj liczy jakąś prostą łączącą środkowy wierzchołek z tamtą prostą wyżej?
    b1_up = d1.y - (1 / sol1[a1]) * d1.x
    a1_up = 1/sol1[a1]

    #magią pitagorasa i trygonometri oblicza kąt pod jakim jest zdjęcie??
    x1_hit = -1*b1_up/a1_up
    c_bok = (d1.y ** 2 + (d1.x - x1_hit) ** 2) ** 0.5
    ratio1 = d1.y / c_bok
    if d1.x-x1_hit<0:
        desc+="1.Ujemny case!\n"
        alpha = 180-np.degrees(np.arccos(np.float64(ratio1)))
    else:
        alpha = np.degrees(np.arccos(np.float64(ratio1)))

    #print(f"l2: y={a1_up}x+{b1_up}")
    desc+=f"alpha:{alpha}\n"


    #<JAK WYŻEJ>
    a2, b2 = symbols('a2,b2')
    eq2_l = Eq((a2 * d2.xl + b2), d2.yl)
    eq2_r = Eq((a2 * d2.xr + b2), d2.yr)
    sol2 = solve((eq2_l, eq2_r), (a2, b2))
    #print(f"l1: y={sol2[a2]}x+{sol2[b2]}")
    b2_up = d2.y - (1 / sol2[a2]) * d2.x
    a2_up = 1/sol2[a2]
    x2_hit = -1 * b2_up / a2_up
    c_bok = (d2.y**2+(d2.x-x2_hit)**2)**0.5
    ratio2 = d2.y/c_bok
    if d2.x-x2_hit<0:
        desc+=("2.Ujemny case!\n")
        beta = 180-np.degrees(np.arccos(np.float64(ratio2)))
    else:
        beta = np.degrees(np.arccos(np.float64(ratio2)))

    #print(f"l2: y={a2_up}x+{b2_up}")
    desc+=f"beta:{beta}\n"

    #różnica między kątem obu zdjęć
    difference = alpha-beta
    desc+=f"Difference:{difference}\n\n"
    print(desc)
    return difference




