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
    #znalezienie konturów
    contours_x, contours_y = get_contours(photo)
    #znalezienie ich skrajnych wartości
    max_x = max(contours_x)[0]
    max_y = max(contours_y)[0]
    min_x = min(contours_x)[0]
    min_y = min(contours_y)[0]

    #dostosowanie skrajnych wartości jeżeli nie wykryto lewego górnego rogu
    if max_x == min_x and max_x != 0:
        min_x = 0
    if max_y == min_y and max_y != 0:
        min_y = 0

    #zwrócenie ich w odpowiedniej kolejności przydatnym do przycięcia QPixMap
    return min_x, min_y, max_x - min_x, max_y - min_y