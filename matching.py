#Tu mają być funkcje, które dostają zdjęcia jako argumenty, tworzą im
#"dwójkąty", a potem porównują i może wyświetlają wyniki tego.

from Diangle import all_photos_diangles,diangles_difference
from photos_opencv import open_photo
import cv2 as cv
import numpy as np


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
        print(e)
        return None


#ma rysować Point1 na Photo1
#rysować Point2 na Photo2
#jakoś połączyć te dwa zdjęcia i pokazać czy match ma wogóle sens
def draw_matches(matches,photos):
    n=10 #ile "najlepszych" dopasowań chcemy pokazać
    print("Pokazujemy {n} najlepszych match'y, możesz to zmienić w funkcji draw_matches w matching.py :)")
    for i in range(n):
        #rysuje Point1 na Photo1
        photo1 = open_photo(photos[matches[i]['Photo1']])
        coords_1 = matches[i]["Point1"]
        img1 = cv.circle(photo1,(coords_1[0],coords_1[1]),5,(255,255,255),-1)

        # rysuje Point2 na Photo2
        photo2 = open_photo(photos[matches[i]['Photo2']])
        coords_2 = matches[i]["Point2"]
        img2 = cv.circle(photo2, (coords_2[0], coords_2[1]), 5, (255, 255, 255), -1)

        #łączy dwa zdjęcia ze sobą
        vis = np.concatenate((img1, img2), axis=1)


        #wizualizuje dopasowanie
        cv.imshow("Match",vis)
        cv.waitKey(0)
        cv.destroyAllWindows()