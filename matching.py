#Tu mają być funkcje, które dostają zdjęcia jako argumenty, tworzą im
#"dwójkąty", a potem porównują i może wyświetlają wyniki tego.

from Diangle import all_photos_diangles, diangles_difference
from photos_opencv import open_photo, get_crop, extract_mask_and_contour
import cv2 as cv
import numpy as np
from sympy import symbols, Eq, solve
from scipy import ndimage
import math



#AKTUALNE PROBLEMY: dziwne dopasowania, optymalizacja (a raczej jej brak)

def filter_diangles(diangles, min_angle=25):
    return [
        d for d in diangles
        if min_angle < d.angle < 180 - min_angle
    ]


def true_match_all_photos(photos):
    #do tego, ile topowych dopasować wyświetlić (żeby nie wysadzić terminala)
    number_of_top_matches = 100

    #zdobywa wszystkie diangle
    all_diangles = [
    filter_diangles(photo_diangles)
    for photo_diangles in all_photos_diangles(photos)
]
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
                            # FILTR JAKOŚCI
                            if diff < 0.3:
                                matches.append(single_match)
                current_diangle += 1
            current_photo += 1

        #sotruje dopasowania według podobieństwa malejąco
        sorted_matches = sorted(matches, key=lambda d: d['Difference'])

        # usuwa dominację jednej pary zdjęć
        sorted_matches = unique_photo_pairs(sorted_matches, top_per_pair=5)

        #wyświetla tylko ileś topowych dopasowań, bo wszystkie się nie mieszczą
        # print("Sorted matches:")
        # for k in range(number_of_top_matches):
        #     print(sorted_matches[k])
        return sorted_matches

    #to tak na wszelki wypadek bo wcześniej było parę problemów
    except Exception as e:
        print("Ups:",e)
        return None

def unique_photo_pairs(matches, top_per_pair=5):
    result = []
    seen = {}

    for m in matches:
        pair = tuple(sorted((m["Photo1"], m["Photo2"])))
        seen.setdefault(pair, [])
        if len(seen[pair]) < top_per_pair:
            seen[pair].append(m)
            result.append(m)

    return result


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

# Helper: Oblicza transformację (macierz 2x3) dopasowującą diangle2 do diangle1
# Używa cv.estimateAffinePartial2D dla precyzji
def calculate_precise_transform(d1, d2):
    # D1 to diangle na zdjęciu, do którego doklejamy (baza).
    # D2 to diangle na zdjęciu, które chcemy dopasować (obracane/przesuwane).
    
    # Punkty docelowe (na zdjęciu 1): Odwracamy kolejność L->R bo łączenie jest "twarzą w twarz".
    # Wyobraź sobie dwa puzzle. Żeby pasowały, wypustka jednego musi wejść we wcięcie drugiego.
    # Lewa strona wcięcia styka się z prawą stroną wypustki.
    
    # Pobieramy punkty źródłowe (z D2 - tego co obracamy)
    # [Lewy, Środek, Prawy]
    # Konwertujemy na float32, bo tego wymaga OpenCV
    src_pts = np.float32([
        [d2.xl, d2.yl],  # Lewy punkt diangla 2
        [d2.x, d2.y],    # Środkowy punkt diangla 2
        [d2.xr, d2.yr]   # Prawy punkt diangla 2
    ])
    
    # Pobieramy punkty docelowe (z D1 - tego co stoi w miejscu)
    # Tutaj odwracamy kolejność: Prawy -> Środek -> Lewy
    # Dzięki temu "lewe ramię" źródła trafi w "prawe ramię" celu.
    dst_pts = np.float32([
        [d1.xr, d1.yr],  # Prawy punkt diangla 1 (pasuje do Lewego z D2)
        [d1.x, d1.y],    # Środkowy punkt diangla 1 (pasuje do Środka z D2)
        [d1.xl, d1.yl]   # Lewy punkt diangla 1 (pasuje do Prawego z D2)
    ])
    
    # Obliczamy optymalną transformację sztywną:
    # - Szuka takiej rotacji i przesunięcia (bez skalowania!), która najlepiej nakłada punkty src na dst.
    # - estimateAffinePartial2D jest lepsze od zwykłego getAffineTransform, bo
    #   minimalizuje błąd dla wszystkich 3 punktów, zamiast sztywno brać 3.
    #   Tutaj mamy akurat 3 punkty, ale algorytm jest bardziej odporny na drobne niedokładności.
    M, inliers = cv.estimateAffinePartial2D(src_pts, dst_pts)
    
    # Zwracamy macierz transformacji 2x3 ([ [cos -sin tx], [sin cos ty] ])
    return M

# Helper: Sprawdza czy kontur 2 (po transformacji) nie nachodzi na kontur 1
# Rozwiązanie geometryczne (bez zliczania pikseli masek)
def verify_no_overlap(photo1, photo2, M, tolerance=5, collision_threshold=10):
    # 1. Pobieramy kontury (obrysy) obu obiektów.
    # extract_mask_and_contour zwraca nam listę punktów tworzących obwiednię.
    _, cnt1 = extract_mask_and_contour(photo1)
    _, cnt2 = extract_mask_and_contour(photo2)
    
    # Jeśli nie udało się znaleźć konturu (np. puste zdjęcie), to bezpieczniej zwrócić False.
    if cnt1 is None or cnt2 is None:
        return False
        
    # 2. Transformujemy kontur drugiego zdjęcia używając wyliczonej wcześniej macierzy M.
    # Dzięki temu wiemy, gdzie znajdą się krawędzie zdjęcia 2 po dopasowaniu.
    cnt2_trans = cv.transform(cnt2, M)
    
    # 3. Sprawdzamy kolizję punkt po punkcie.
    # pointPolygonTest to funkcja OpenCV, która mówi, gdzie leży punkt względem wielokąta (konturu):
    # > 0 : wewnątrz konturu
    # < 0 : na zewnątrz konturu
    # = 0 : idealnie na krawędzi
    
    # Prawidłowe dopasowanie puzzli oznacza, że puzzle stykają się krawędziami,
    # ale jeden nie wchodzi w środek drugiego.
    
    bad_points = 0 # licznik punktów, które "weszły" w drugi obiekt
    
    # Sprawdzamy co 10-ty punkt drugiego konturu dla wydajności (optymalizacja).
    # Sprawdzanie każdego punktu byłoby zbyt wolne.
    for pt in cnt2_trans[::10]:
        # Pobieramy współrzędne (x, y) punktu
        p = (float(pt[0][0]), float(pt[0][1]))
        
        # Testujemy czy punkt p (z konturu 2) leży wewnątrz konturu 1.
        # Trzeci argument 'True' oznacza, że funkcja zwróci odległość od krawędzi (w pikselach).
        # Jeśli dist > 0, to jesteśmy w środku. Im większa liczba, tym głębiej.
        dist = cv.pointPolygonTest(cnt1, p, True)
        
        # Jeśli punkt jest głęboko wewnątrz (> tolerance pikseli), uznajemy to za błąd.
        # Tolerancja (5px) pozwala na minimalne, niedostrzegalne nachodzenie (błędy zaokrągleń).
        if dist > tolerance:
            bad_points += 1
            # Jeśli za dużo punktów (więcej niż 10) nachodzi, przerywamy.
            # To oznacza, że zdjęcia się krzyżują/kolidują.
            if bad_points > collision_threshold:
                return False # Odrzucamy to dopasowanie
                
    # Jeśli pętla przeszła i nie wykryliśmy dużej kolizji - jest OK.
    return True

# Helper: Skleja zdjęcia używając macierzy afinicznej
# Macierz afiniczna to macierz 2x3 która mówi jak przesunąć i obrócić zdjęcie
# img1 to zdjęcie "baza" (nie ruszamy go), img2 to zdjęcie dokładane (transformujemy je macierzą M).
def stitch_images_affine(img1, img2, M):
    # Obliczamy rozmiar nowego płótna, które pomieści oba zdjęcia.
    # img1 to zdjęcie "baza" (nie ruszamy go), img2 to zdjęcie dokładane (transformujemy je macierzą M).
    
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    
    # 1. Obliczamy gdzie trafią narożniki img1 (one są w (0,0), (w,0) itd.)
    # Ponieważ img1 się nie rusza, to po prostu jego wymiary.
    box1 = np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
    
    # 2. Obliczamy gdzie trafią narożniki img2 po transformacji M.
    box2 = np.float32([[0, 0], [w2, 0], [w2, h2], [0, h2]])
    # cv.transform bierze punkty i wykonuje na nich rotację+przesunięcie z M.
    box2_trans = cv.transform(np.array([box2]), M)[0]
    
    # 3. Łączymy wszystkie punkty (narożniki obu zdjęć), żeby znaleźć minimalne i maksymalne współrzędne.
    # To wyznaczy ramki nowego, dużego obrazka.
    all_points = np.vstack((box1, box2_trans))
    x_min, y_min = np.min(all_points, axis=0) # Lewy górny róg całości
    x_max, y_max = np.max(all_points, axis=0) # Prawy dolny róg całości
    
    # Obliczamy szerokość i wysokość wynikowego płótna
    new_w = int(np.ceil(x_max - x_min))
    new_h = int(np.ceil(y_max - y_min))
    
    # 4. Tworzymy macierz korekcyjną T (translacja).
    # Jeśli wynikowa współrzędna x_min wyszła np. -100, to musimy przesunąć wszystko o +100 w prawo,
    # żeby zmieściło się w obrazku (indeksy w tablicy muszą być >= 0).
    T = np.float32([
        [1, 0, -x_min], # przesunięcie w X
        [0, 1, -y_min], # przesuniecie w Y
        [0, 0, 1]
    ])
    
    # 5. Przygotowujemy finalną macierz transformacji dla drugiego zdjęcia.
    # Musimy połączyć dwie operacje:
    #   M (dopasowanie do img1) -> T (przesunięcie na środek płótna)
    # Mnożenie macierzy: M_final = T * M
    M_3x3 = np.vstack((M, [0, 0, 1])) # Rozszerzamy M do 3x3 żeby móc mnożyć
    M_combined_3x3 = np.matmul(T, M_3x3)
    M_final = M_combined_3x3[:2, :] # Wracamy do postaci 2x3 wymaganej przez warpAffine
    
    # 6. Przygotowujemy transformację dla pierwszego zdjęcia.
    # Ono się nie obraca, ale też musi zostać przesunięte na środek płótna (o wektor T).
    M_T = T[:2, :] # Wiersze 0 i 1 z T
    
    # 7. Wykonujemy transformacje ("warping")
    # warpAffine tworzy nowy obraz o wymiarach (new_w, new_h) i "wlewa" w niego piksele
    # zgodnie z zadaną macierzą.
    warped1 = cv.warpAffine(img1, M_T, (new_w, new_h))
    warped2 = cv.warpAffine(img2, M_final, (new_w, new_h))
    
    # 8. Sklejamy oba obrazy w jeden.
    # Tam gdzie warped2 (to dokładane) ma treść (nie jest przezroczyste), tam nadpisuje tło.
    
    if warped2.shape[2] == 4:
        # Jeśli mamy kanał Alfa (przezroczystość):
        # Tworzymy maskę: tam gdzie alfa > 0, tam jest obraz.
        mask2 = warped2[:, :, 3] > 0
        
        # Kopiujemy warped1 (bazę)
        img_final = warped1.copy()
        
        # Wklejamy warped2 w miejscach gdzie maska mówi że coś jest
        img_final[mask2] = warped2[mask2]
    else:
        # Fallback dla obrazów bez Alfy (zakładamy, że czarne to tło)
        gray2 = cv.cvtColor(warped2, cv.COLOR_BGR2GRAY)
        mask2 = gray2 > 0
        img_final = warped1.copy()
        img_final[mask2] = warped2[mask2]
        
    return img_final

#ma rysować Point1 na Photo1
#rysować Point2 na Photo2
#jakoś połączyć te dwa zdjęcia i pokazać czy match ma wogóle sens
def draw_matches(matches, photos, rejected_pairs):

    n = 40 #ile "najlepszych" dopasowań chcemy sprawdzić
    print(f"Ilość potencjalnych dopasowań: {len(matches)}")
    print(f"Sprawdzamy max {n} najlepszych match'y.")
    
    # Zabezpieczenie przed 'list index out of range'
    limit = min(n, len(matches))
    
    for i in range(0, limit): 
        # Pobieramy match
        match = matches[i]
        
        # indeksy zdjęć z pary
        p1_idx = match['Photo1']
        p2_idx = match['Photo2']

        # Sprawdzamy odrzucone pary (używając ścieżek, system robust)
        path1 = photos[p1_idx]
        path2 = photos[p2_idx]
        
        # Sprawdź czy para (jako zbiór ścieżek) jest w odrzuconych
        if frozenset([path1, path2]) in rejected_pairs:
            continue

        # otwiera zdjęcia z tego dopasowania
        photo1 = open_photo(path1)
        photo2 = open_photo(path2)
        
        if photo1 is None or photo2 is None:
            continue

        # Pobieramy diangle
        d1 = match['diangle1']
        d2 = match['diangle2']
        
        # 1. Obliczamy precyzyjną transformację
        M = calculate_precise_transform(d1, d2)
        
        if M is None:
            continue
            
        # 2. Weryfikacja geometryczna (brak nakładania się dużych obszarów)
        # Rozwiązuje problem "krzyżujących się" zdjęć
        if not verify_no_overlap(photo1, photo2, M):
            print(f"Match {i} rejected due to overlap collision.")
            continue
            
        # 3. Jeśli przeszło testy, łączymy zdjęcia
        best_version = stitch_images_affine(photo1, photo2, M)
        
        # Obliczamy kąt dla zwrócenia (z macierzy rotacji)
        angle_rad = math.atan2(M[1, 0], M[0, 0])
        true_angle = math.degrees(angle_rad)

        print(f"Found valid match at index {i} with angle {true_angle:.2f}")
        
        #return najlepsze połaczenie, obrót, indeksy połączonych fragmentów
        return best_version, true_angle, p1_idx, p2_idx

    # Jeśli nie znaleziono żadnego:
    raise Exception("Nie znaleziono poprawnych, niekolidujących dopasowań w topowych wynikach.")

# z racji, że join_photos() działa tylko dla zdjęć tego samego rozmiaru
# to tu je ustawiamy by miały taki sam rozmiar
# jeżeli jakimś cudem już są tego samego rozmiaru, to nic się z nimi nie dzieje
def adjust_photos(p1,p2):


    #pobiera kształty zdjęć
    h1,w1 = p1.shape[:2]
    h2,w2 = p2.shape[:2]

    #takie same rozmiary - nic się nie dzieje
    if h1 == h2 and w1 == w2:
        return p1,p2

    #bierze maksymalne rozmiary
    h_max = max(h1,h2)
    w_max = max(w1,w2)

    #tworzy dwa puste zdjęcia o maksymalnych wymiarach
    if p1.shape[2] == 4:
        im1 = np.zeros((h_max, w_max, 4), np.uint8)
    else:
        im1 = np.zeros((h_max, w_max, 3), np.uint8)

    if p2.shape[2] == 4:
        im2 = np.zeros((h_max, w_max, 4), np.uint8)
    else:
        im2 = np.zeros((h_max, w_max, 3), np.uint8)

    #wsadza do nich te mniejsze
    im1[:h1,:w1] = p1[:,:]
    im2[:h2,:w2] = p2[:,:]

    #bardzo specyficzne zabezpieczenia na bardzo specyficzne przypadki
    if im1.shape==im2.shape:
        return im1,im2

    elif im1.shape[2]<im2.shape[2]:
        print("Im1 - bad shape")
        return im1,im2[:,:,:3]

    else:
        print("Im2 - bad shape")
        return im1[:,:,:3],im2


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
    if d1.x - x1_hit < 0:
        alpha = 180 - np.degrees(np.arccos(np.float64(ratio1)))
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
    if d2.x - x2_hit < 0:
        beta = 180 - np.degrees(np.arccos(np.float64(ratio2)))
    else:
        beta = np.degrees(np.arccos(np.float64(ratio2)))


    #PROBLEM: czasem pasuje kąt difference, a czasem difference+180
    #Nie wiem na jakiej podstawie wybiera się ten właściwy
    #Bierzemy więc dwa i potem w draw_matches() się wybiera ten lepszy

    #różnica między kątem obu zdjęć
    difference = -(alpha-beta)

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
    y1 = int(np.mean(red_points[0]))
    x1 = int(np.mean(red_points[1]))

    # znajduje czerwone punkty na drugim zdjęciu
    img_hsv = cv.cvtColor(p2, cv.COLOR_BGR2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv.inRange(img_hsv, lower_red, upper_red)
    red_points = np.where(mask == 255)

    # bierze punkt, który jest środkiem czerwonej kropki więc też środkiem dwójkąta
    y2 = int(np.mean(red_points[0]))
    x2 = int(np.mean(red_points[1]))

    # oblicza o ile trzeba przesunąć prawe zdjęcie aby dopasować jego czerwoną kropkę
    # z tym po lewej
    width1 = p1.shape[1]
    width_difference = -(width1-x1+x2)
    height_difference = y2-y1

    # zwraca tą informację
    return width_difference,height_difference

#do łączenia dwóch zdjęć
def join_photos(p1,p2,x,y):
    #to się potem zmieni
    p2_height = p2.shape[0]
    p2_width = p2.shape[1]

    #buduje takie duże puste zdjęcie w którym zmieszczą sięoba zdjecia po przesunięciu
    full_width = 4*p2_width
    full_height = 3*p2_height
    image = np.zeros((full_height,full_width,4), np.uint8)

    #wrzuca pierwsze zdjęcie na właściwie miejsce
    image[p2_height:p2_height * 2, p2_width :p2_width * 2] = p1

    #wrzuca drugie zdjęcie przesunięte o wektor
    for i in range(p2_height,p2_height*2):
        for j in range(p2_width*2,p2_width*3):
            if p2[i-p2_height,j-p2_width*2][3]!=0:
                image[i-y,j+x]=p2[i-p2_height,j-p2_width*2]

    #zwraca całe zdjęcie, przycięte (nieco eksperymentalnie)
    x,y,w,h= get_crop(image)
    image = image[y:y+h,x:x+w]
    return image
