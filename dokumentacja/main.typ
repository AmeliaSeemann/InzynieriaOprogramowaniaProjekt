

#set text(size: 12pt, lang: "pl", font: "New Computer Modern")
#set page(margin: 3.5cm)
#set par(justify: true)
#set heading(numbering: "1.1  ")
#show heading: set block(below: 1em)

#show bibliography: set heading(numbering: "1.1  ")

#align(center)[
  #image("media/ps-logo.svg", width: 33%)

  #v(3em)

  Dokumentacja wewnętrzna

  2025/2026

  #v(1em)

  #text(size: 1.3em)[
    *Inżynieria Oprogramowania*

  ]
]

#v(1em)

#align(right)[
  Kierunek: Informatyka

  Członkowie zespołu: #linebreak()
  _Amelia Seemann_ #linebreak()
  _Zuzanna Zięba_ #linebreak()
  _Yana Ivanyna_ #linebreak()

]

#v(1fr)

#align(center)[Gliwice, 2025/2026]

#pagebreak()

#counter(page).update(1)
#set page(numbering: "1")

#outline()

#pagebreak()
#show link: underline

= Schemat graficzny struktury systemu
(tu wstawić fotkę folderów jak będzie gotowe)

(tu wstawić jakiś diagram jak będzie gotowe)

- main.py - odpowiada za interfejs użytkownika

- photos_opencv.py - zawiera funkcje konieczne do: wczytywania zdjęć, przycinania ich, znajdywania ich konturów i wierzchołków, a także testowej wizualizacji tych procesów

- Diangle.py - zawiera klasę Diangle (o której jest więcej w dokumentacji), oraz funkcje bezpośrednio z nią powiązane

- matching.py - odpowiada za dopasowywanie zdjęć oraz wizualizację dopasowań


Główny skrypt main.py przyjmuje polecenia od użytkownika, czyli wgrywanie i dopasowywanie zdjęć. Ich załadowanie odbywa się przez photos_open.cv, które również znajduje ich cechy. Na podstawie tych cech (czyli wierzchołków, krawędzi, kątów...) zostają utworzone obiekty klasy Diangle wewnątrz pliku Diangle.py. Korzystając z tych obiektów, skrypt matching.py dopasowuje wgrane zdjęcie i wizualizauje ich dopasowania.
= Dokumentacja wewnętrzna
== Instrukcja użytkowania
== O pracy zespołowej
Prace nad projektem dokumentowaliśmy na platformie GitHub oraz za pomocą arkusza Excel. Na samym początku korzystaliśmy również z Trello, aczkolwiek okazało się to przerostem formy nad treścią, więc zostaliśmy przy znacznie wygodniejszym dla nas Excel'u.

Składa się on z czterech arkuszy, czyli po jednym indywidualnym na osobę oraz jeden wspólny. Dla każdego zadania jest udokumentowana jego nazwa, przypisana osoba, przewidywany i realny czas pracy oraz wyjaśnienie nieścisłości, jeżeli się akurat pojawiły. Każdy ma też zsumowane swoje godziny pracy. Wygląd arkusza delikatnie ewoluował w trakcie pracy, ale zdecydowanie w sensie pozytywnym.


#figure(
  image("media/obraz.png", width: 100%),
  caption: [Fragment arkuszu Excel],
)

O ile nasz arkusz Excel jest bardzo szczegółowy i uporządowany, to na platformie GitHub przyjęliśmy bardziej ogólne i lekko chaotyczne podejście. Coś, co w Excelu jest kilkoma mniejszymi zadaniami, na GitHub'ie może być jednym commit'em z dość enigmatyczną nazwą. Sposób dokumentowania projektu na GitHub'ie niespecjalnie zmienił się w trakcie.

Do komunikacji korzystaliśmy z serwera utworzonego na platformie Discord, gdzie rozmowy były nie najdłuższe lecz konkretne i owocne.
#figure(
  image("media/obraz (1).png", width: 100%),
  caption: [Fragment serwera na platformie Discord],
)


== Wykorzystanie biblioteki
Cały graficzny interfejs użytkownika został stworzony z pomocą _PyQt5_. Dzięki tej bibliotece mamy wszystkie guziki i możliwość wygodnego wyboru folderu ze zdjęciami. Co ciekawe, na początku planowaliśmy użyć _PyQt6_, tylko okazało się, że tej konkretnej wersji nie da się zainstalować w Pychrarm'ie, więc zostaliśmy przy starszej.


_OpenCV_ faktycznie wgrywa nasze zdjęcia i znajduje ich cechy. Służy nam również do wyświetlania zdjęć z zaznaczonymi krawędziami i wierzchołkami, co było niezwykle pomocne przy obmyślaniu jak w ogóle je ze sobą dopasowywać. Dzięki tej bibliotece mogliśmy też przycinać i łączyć zdjęcia.


Przydatną biblioteką był również _numpy_, ponieważ zdjęcia są w rzeczywistości macierzami a w macierzach _numpy_ jest dobry. Był konieczny przy tworzeniu nowych, pustych zdjęć. Znalazł również zastosowanie w sprawach czysto matematycznych, jak obliczenia trygonometryczne bądź operacje na wektorach.


Powyższe biblioteki okazały się najbardziej pomocne i planowaliśmy wykorzystanie ich od samego początku, ale po drodze użyliśmy też jeszcze paru innych do pojedynczych zadań. Biblioteka _os_ była konieczna do znajdywania listy zdjęć w danym folderze. Z pomocą biblioteki _scipy_ mogliśmy bardzo łatwo obracać zdjęcia korzystając z modułu _ndimage.rotate()_. Natomiast biblioteka _sympy_ pomogła nam w rozwiązaniu kilku równań.
== Odnajdywanie cech zdjęć


(tu w sumie Zuza możesz coś opisać jak znajdujesz te krawędzie itp, bo ty to robiłaś)
== Przerobienie cech zdjęć

Po uzyskaniu cech każdego ze zdjęć, nie możemy ich wykorzystywać do dopasowania tak od razu. Wpierw te cechy trzeba przetransformować w coś, co jest łatwiejsze do porównywania niż ich aktualna postać.

Na tą potrzebę została stworzona klasa _Diangle_ (słowo zmyślone), która reprezentuje coś takiego:
#figure(
  image("media/diangle.png", width: 60%),
  caption: [Diangle],
)
Jest to po prostu jeden fragment uproszczonych krawędzi zdjęcia. Każdy obiekt tej klasy przechowuje współrzędne jego punktów, długości ramion, kąt pomiędzy nimi oraz typ (wklęsły bądź wypukły).

Aby przerobić cechy pojedyńczego zdjęcia na Diangle, zostaje wykorzystana funkcja _one_photo_diangle()_. Wywołuje ona również funkcję _sort_features_for_diangles()_, która porządkuje cechy zdjęcia tak, aby Diangle powstawały z punktów leżących obok siebie.

Funkcja _one_photo_diangle()_ zostaje wielokrotnie wywoływana wewnątrz funkcji _all_photos_diangles()_, która jak nazwa wskazuje, tworzy Diangle dla cech wszystkich załadowanych zdjęć.

== Dopasowywanie zdjęć

Główną funkcją, która pomaga w szukaniu dopasowań, jest _diangles_difference()_. Funkcja ta jako argumenty bierze dwa obiekty klasy Diangle i liczy jak bardzo się od siebie różnią.

Na samym początku sprawdza, czy oba Diangle nie są przypadkiem tego samego samego typu, czyli na przykład oba są wypukłe. Jeżeli tak, to od razu zwraca liczbę 9999. Nie jest ona dokładną miarą podobieństwa, ale po prostu wiemy że nie można dopasować czegoś wypukłego do czegoś innego, co też jest wypukłe. Taki przypadek jest więc bardzo szybko odrzucany.


W pozostałych przypadkach to im mniejsza liczba zostaje zwrócona, tym bardziej Diangle są do siebie podobne i pasujące.  

Funkcja oblicza względne różnice między ramionami obu obiektów (lewym pierwszego i prawym drugiego, potem prawym pierwszego i lewym drugiego) a także względną różnice ich kątów.

Każda z tych różnic ma też swoją wagę, którą można dostosowywać. Domyślnie jednak każda z różnic ma takie same znaczenie, czyli kąt, lewe i prawe ramie wszystkie mają wagi 1/3. Każda z różnic zostaje pomnożona przez swoją wagę, a wyniki tych obliczeń zostają zsumowane. Zwrócona wartość jest miarą różnicy obiektów klasy Diangle.


Korzystając z wyżej opisanej funkcji, plik _matching.py_ analizuje różnice wszystkich obiektów klasy Diangle we wszystkich zdjęciach. Liczby zwrócone przez _diangles_difference()_ zostają posortowane rosnąco, by na początku zaprezentować najbardziej obiecujące dopasowania.

Każde dopasowanie ma postać elementu słownika, który przechowuje informacje o:
- wartości liczbowej różnicy dwóch obiektów klasy Diangle

- indeksie zdjęć, które zostały dopasowane

- współrzędnych środkowych punktów, które zostały dopasowane

- całych obiektach klasy Diangle

== Wizualizacja dopasowań


Kroki potrzebne do wizualizacji każdego z dopasowań zostają wykonane wewnątrz pętli w funkcji _draw_matches()_.

Na początku zostają otwarte zdjęcia występujące w danym dopasowaniu. Ich rozmiar zostaje dostosowany funkcją _adjust_photos()_, aby oba zdjęcia były dokładnie tej samej wielkości, co umożliwia ich późniejsze łączenie.

Oba zdjęcia zostają potraktowane funkcją _cv.cvtColor()_, która zmienia ich kolory na skalę szarości. Te szare zdjęcia są oczywiście przechowywane w osobnych zmiennych by nie stracić oryginałów. Na czarno-białych zdjęciach rysuje się później dwie czerwone kropki (funkcją _draw_dot()_) w miejscach, które są punktami ich dopasowania.

Następnie zostaje wywołana funkcja _calculate_rotation_degree()_, która jako argumenty przyjmuje dwa obiekty klasy Diangle występujące w aktualnym dopasowaniu. Z pomocą paru równań, twierdzenia pitagorasa oraz funkcji trygonometrycznych oblicza ona kąt, o który należy obrócić drugie zdjęcie by dopasować je do pierwszego.

Funkcja ta ma mały problem, któego nie udało się naprawić. Mniej więcej w połowie przypadków oblicza idealny kąt, a w reszcie przypadków należy do niego dodać 180 stopni aby miał on sens. Z tego powodu zwraca obie wersje kąta, właściwa zostaje wydedukowana później.

Korzystając z funkcji  _ndimage.rotate()_ biblioteki _scipy_ otrzymujemy więc dwie wersje drugiego, szarego zdjęcia, obróconego o jakiś kąt. Z racji, że zostało obrócone, trzeba ponownie dostosować jego rozmiar względem pierwszego zdjęcia, korzystając z _adjust_photos()_.

Dla obu par dostosowanych zdjęć zostaje wywołana funkcja _calculate_vector()_. Zwraca ona wektor, o który należy przesunąć już obrócone drugie zdjęcie aby połączyć je z pierwszym. Jest on łatwy do obliczenia, ponieważ jedynym nie czarno-białym elementem obu zdjęć jest czerwona kropka, która ma je połączyć. Wystarczy znaleźć współrzędne czerwonych kropek funkcją _cv.inRange()_, która znajduje piksele w sprecyzowanych kolorach.

Kiedy wektor przesunięcia został obliczony, przygotowujemy dwie pary dopasowanych rozmiarem i odpowiednio obróconych zdjęć, tylko już w normalnej wersji kolorowej. Na obu parach wywołujemy funkcję _join_photos()_. Tworzy ona dostatecznie wielkie, puste zdjęcie, a potem umieszcza w nim dwa zdjęcia przesunięte liczbami z _calculate_vector()_ tak, aby się jak najlepiej łączyły.

Kończymy więc z dwoma wizualizacjami dopasowania, ponieważ wcześniej obliczyliśmy dwa różne kąty obrotu. W tym momencie możemy jednak jednoznacznie wybrać ten właściwy. Jeżeli zdjęcia zostały źle obrócone, to po połączeniu ich w _join_photos()_ będą na siebie w jakimś stopniu nachodzić, co nie dotyczy tych dobrze obróconych. Korzystamy z funkcji _cv.countNonZero()_, do obliczenia ile "tła" mają obie wersje dopasowania. Jako poprawną uznajemy tą, dla której _cv.countNonZero()_ zwróciło mniejszą liczbę, czyli zdjęcia mniej się nakładały.

== Dalsze etapy łączenia fragmentów
( tu możesz Zuza napisać o tych accept deny i tym stitch all)
= Podsumowanie
[Nie ma sensu tego pisać wcześniej, niż na dzień przed faktyczną prezentacją ] 





#pagebreak()


