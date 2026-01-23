

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
Tak prezentuje się główne drzewo plików programu:
#figure(
  image("media/pliki.png", width: 60%),
  caption: [Pliki programu],
)



- main.py - odpowiada za interfejs użytkownika

- photos_opencv.py - zawiera funkcje konieczne do: wczytywania zdjęć, przycinania ich, znajdywania ich konturów i wierzchołków, a także testowej wizualizacji tych procesów

- Diangle.py - zawiera klasę Diangle (o której jest więcej w dokumentacji), oraz funkcje bezpośrednio z nią powiązane

- matching.py - odpowiada za dopasowywanie zdjęć oraz wizualizację dopasowań

- dialog_window.py - odpowiada za pomniejszy interfejs użytkownika występujący przy akceptowaniu bądź odrzucaniu dopasowań

- zdjęcia - folder z podfolderami wypełnionymi różnymi zdjęciami wykorzystywanymi do testowania programu, więcej informacji na ten temat jest w sekcji o testach

Tak prezentuje się schemat graficzny działania programu:

#figure(
  image("media/diagram.png", width: 60%),
  caption: [Schemat działania programu],
)

Główny skrypt _main.py_ przyjmuje polecenia od użytkownika, czyli wgrywanie i dopasowywanie zdjęć. Ich załadowanie odbywa się przez _photos_opencv.py_, które również znajduje ich cechy. Na podstawie tych cech (czyli wierzchołków, krawędzi, kątów...) zostają utworzone obiekty klasy Diangle wewnątrz pliku _Diangle.py_. Korzystając z tych obiektów, skrypt _matching.py_ dopasowuje wgrane zdjęcie i wizualizuje ich dopasowania. Dopasowania można później zaakceptować bądź odrzucić w oknie dialogowym tworzonym przez plik _dialog_window.py_.
= Dokumentacja wewnętrzna
== Instrukcja użytkowania
- Wczytywanie danych

  - Przycisk [_Load Photos_ ]: Po kliknięciu otworzy się eksplorator plików. Należy wskazać folder zawierający fragmenty zdjęć. Program automatycznie załaduje wszystkie obrazy z katalogu i przygotuje je do dalszej pracy.

- Przeglądanie i nawigacja
  - Wyszukiwarka [_Go to photo_ ]: Jeśli pracujemy z dużą ilością zdjęć, można wpisać numer konkretnego zdjęcia w pole tekstowe na dole ekranu. Program natychmiast wyświetli wybrany fragment, co ułatwia orientację w zestawie.

  - Przyciski [$>>$] i [$<<$]: Służą do przełączania się na następne/poprzednie zdjęcie.

  - Przycisk [_Show edges_]: Pozwala podejrzeć punkty kluczowe (zaznaczone czerwonymi kropkami) na krawędziach fragmentów. Dzięki temu widzimy, jakie miejsca program uznał za charakterystyczne i na jakiej podstawie próbuje je połączyć.

- Łączenie fragmentów (Tryb Ręczny)
  - Przycisk [_Connect Photo Manual_ ]: Uruchamia znajdywania dopasowań w sposób kontrolowany przez użytkownika. Przy każdym proponowanym dopasowaniu można je zatwierdzić lub odrzucić.

  - Weryfikacja (Okno podglądu): Po obliczeniach pojawi się dodatkowe okno z propozycją połączenia:

  - Przycisk [_Accept_]: Jeśli dopasowanie jest poprawne, fragmenty zostaną trwale złączone w jeden większy element.

  - Przycisk [_Reject_]: Jeśli dopasowanie jest błędne, można zrezygnować i spróbować innej kombinacji.



-  Łączenie automatyczne (Tryb Szybki)

  - Przycisk [_Connect All_ ]: Najszybsza opcja. Program samodzielnie analizuje wszystkie dostępne części, szuka pasujących par i składa je w całość bez konieczności ręcznego potwierdzania każdego kroku. Po zakończeniu od razu prezentowany jest finalny obraz.

- Zapisywanie efektów

  - Pobieranie wyniku: Gdy proces układania dobiegnie końca, można pobrać gotowe, połączone zdjęcie i zapisać je na swoim urządzeniu.
== O narzędziach pracy zespołowej
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

Proces ten opiera się na analizie geometrii krawędzi obiektów w celu identyfikacji ich kluczowych punktów topograficznych, określanych jako ekstrema krawędziowe. Głównym mechanizmem pozwalającym na matematyczny opis kształtu obrysu jest analiza jago krzywizny lokalnej.

Kluczowym elementem tego modułu jest funkcja _compute_curvature()_, która analizuje przebieg konturu punkt po punkcie i bada stopień geometrycznych załamań linii brzegowej.

Dla każdego punktu na krawędzi funkcja analizuje wektory utworzone między nim a punktami oddalonymi o parametr _k_. Na tej podstawie obliczany jest kąt oraz kierunek odchylenia.

Wynik tej funkcji pozwala sklasyfikować punkty według dwóch kategorii:
- Wartość ujemna (Kąt wypukły)
- Wartość dodatnia (Kąt wklęsły)

Następnie funkcja _find_edge_features_from_curvature()_ filtruje te dane, aby wyłonić wyłącznie punkty najbardziej charakterystyczne. System wybiera dany punkt jako cechę charakterystyczną tylko wtedy, gdy spełnia on dwa proste warunki: musi być najmocniejszym zakrętem w swojej okolicy oraz sam zakręt musi być wyraźny (domyślnie u nas jest 15°, wystarczająco mało, by wykryć łagodne łuki, i wystarczająco dużo ignorować poszarpane piksele czy drobne nierówności zdjęcia). Dodatkowo, aby uniknąć tłoku i błędów, system pilnuje, by ważne punkty nie leżały zbyt blisko siebie – jeśli znajdzie jeden silny punkt, ignoruje drobne zakłócenia w jego bezpośrednim sąsiedztwie.

#figure(
  image("media/show_krawedzie1.png"),
  caption: [gdzie uruchomić pokaz krawędzi]
)

#figure(
  image("media/show_krawedzi2.png"),
  caption: [wykryte krawędzie]
)


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
=== Tryb ręczny

W trybie ręcznym, obsługiwanym przez funkcję _connect_photos()_, system nie podejmuje decyzji za użytkownika, lecz przedstawia mu propozycję dopasowania w oknie podglądu (_PreviewDialog_). To użytkownik pełni rolę ostatecznego filtra, decydując, czy dane połączenie ma sens.

#figure(
  image("media/connect_photo_manual1.png", width: 86%),
  caption: [gdzie uruchomić]
)

#figure(
  image("media/connect_photo_manual2.png", width: 86%),
  caption: [wygląd _PreviewDialog_]
)

Oto co dzieje się po podjęciu decyzji:
- *Opcja 1: Akceptacja połączenia (_Accept_)*
Jeśli użytkownik uzna, że fragmenty pasują do siebie:
+ *Powstaje nowy obraz:* system tworzy jedno nowe zdjęcie z tych dwóch fragmentów o zapisuje je w folderze tymczasowym
+ *Sprzątanie listy:* Dwa stare kawałki znikają z listy zdjęć, w miejsce jednego z nich (który miał niższy indeks) pojawia się ten nowy, połączony. Teraz system widzi go jako pojedynczy element, który można próbować dopasować do reszty.
+ *Czyszczenie listy _rejected_pairs_:* Lista _rejected_pairs_ zostaje wyczyszczona. Skoro powstał nowy kształt krawędzi, system musi mieć szansę ponownie sprawdzić połączenia, które wcześniej mogły zostać odrzucone.
- *Opcja 2: Odrzucenie połączenia (_Reject_)*
Jeśli propozycja algorytmu jest błędna:
 + *Czarna lista (_rejected_pairs_):* Para indeksów tych zdjęć trafia do specjalnego zbioru odrzuconych połączeń.
 + *Ochrona przed powtarzalnością:* Dzięki zapisaniu tej pary, przy kolejnym kliknięciu _Connect_Photos_Manualy_, funkcja _draw_matches()_ zignoruje to konkretne dopasowanie i od razu przejdzie do kolejnego, statystycznie drugiego w kolejności najlepszego wyniku.
 + *Brak zmian w plikach:* Żadne zdjęcia nie są usuwane ani modyfikowane. Użytkownik po prostu prosi algorytm o "poszukanie czegoś innego".


 

=== Tryb automatyczny 
Niestety działa tylko na tych zbiorach prostych, niezawierających zbyt dużo elementów.

Funkcja _connect_all_photos()_ odpowiada za proces automatycznego składania wszystkich załadowanych zdjęć w jedną całość. Działa ona w sposób iteracyjny – w każdej pętli redukuje liczbę luźnych fragmentów, aż pozostanie tylko jeden, kompletny obraz.

#figure(
  image("media/connect_all_photos1.png"),
  caption: [gdzie uruchomić]
)

1. *Inicjalizacja i kontrola postępu* 

Na początku system sprawdza, czy na liście znajdują się co najmniej dwa zdjęcia. Jeśli tak, uruchamiane jest okno postępu (_QProgressDialog_). Jest to kluczowe, ponieważ proces dopasowywania jest wymagający obliczeniowo, a okno to pozwala użytkownikowi monitorować postęp lub przerwać operację przyciskiem _Cancel_.

#figure(
  image("media/connect_all_photos2.png"),
  caption: [działanie programu _connect_all_]
)

2. *Pętla głównego algorytmu*

Główna logika zamknięta jest w pętli , która wykonuje się, dopóki na liście _photos_list_ jest więcej niż jeden element. Każda iteracja to następujące kroki:
- *Analiza globalna:* Funkcja _true_match_all_photos()_ przeszukuje wszystkie możliwe pary dostępnych zdjęć i znajduje najbardziej obiecujące dopasowanie.
- *Generowanie połączenia:* Najlepsza para jest przekazywana do _draw_matches()_, która wykonuje rotację i przesunięcie, tworząc nowy, połączony obraz.
- *Zarządzanie pamięcią tymczasową:* Ponieważ połączony fragment nie istnieje jeszcze jako stały plik, zostaje on zapisany w katalogu tymczasowym systemu pod unikalną nazwą wygenerowaną przez uuid. Dzięki temu unikamy nadpisywania plików przy kolejnych krokach.

W skrócie mówiąc, program automatycznie wykonuje nam działanie _connect_photos_manual_ i akceptuje wszystkie uzyskane wyniki, aż pozostanie jeden element.

#figure(
  image("media/connect_all_photos3.png"),
  caption: [efekt końcowy]
)

== Zapisywanie efektu końcowego

#figure(
  image("media/save.png"),
  caption: [gdzie znaleźć]
)

Gdy wszystkie fragmenty zostaną połączone w jeden obraz system umożliwia trwałe zapisanie pracy na dysku poprzez funkcję _save_photo()_.

Jak przebiega proces zapisu?
+ *Wybór lokalizacji:* Po kliknięciu przycisku _Save photo_, system otwiera standardowe okno dialogowe wyboru pliku (_QFileDialog.getSaveFileName_). Użytkownik może wtedy wskazać folder oraz nadać nazwę swojemu plikowi.
+ *Format pliku:* Program domyślnie sugeruje format PNG. Jest to wybór strategiczny, ponieważ format ten obsługuje przezroczystość (kanał alfa), co jest kluczowe, jeśli wokół ułożonych puzzli ma pozostać puste tło.
+ *Finalizacja:* Jeśli użytkownik zatwierdzi wybór, obiekt _end_result_ (przechowujący końcową grafikę) zostaje przetworzony i zapisany fizycznie na dysku.
 - Po udanej operacji wyświetla się komunikat "Success" z dokładną ścieżką do pliku.
 - W przypadku błędu (np. brak uprawnień do zapisu w danym folderze), system wyświetli okno z informacją o problemie.

= Testy
== Przeprowadzone testy jednostkowe
W projekcie przeprowadzono systematyczne testy jednostkowe kluczowych modułów aplikacji.
Testy zostały zaimplementowane z wykorzystaniem biblioteki _pytest_ i miały charakter testów automatycznych.
Ich celem była weryfikacja poprawności działania poszczególnych funkcji oraz odporności kodu na nietypowe dane wejściowe.

== Testy modułu `test_diangle.py`

Plik `test_diangle.py` zawiera testy jednostkowe klasy `Diangle` oraz funkcji `diangles_difference`, odpowiedzialnych za reprezentację oraz porównywanie tzw. dwójkątów.

=== Zakres testów

- weryfikację poprawności inicjalizacji obiektu `Diangle` przez konstruktor,
- sprawdzenie poprawności obliczania długości ramion dwójkąta,
- test metody obliczającej odległość pomiędzy punktami,
- sprawdzenie poprawności działania funkcji porównującej dwójkąty tego samego oraz różnych typów,
- weryfikację odporności funkcji na wartości zerowe i zabezpieczenie przed błędami dzielenia przez zero.

Wszystkie testy w module `test_diangle.py` zakończyły się powodzeniem, co potwierdza poprawność implementacji logiki geometrycznej oraz stabilność funkcji pomocniczych.



== Testy modułu `test_matching.py`

Plik `test_matching.py` zawiera testy jednostkowe funkcji odpowiedzialnych za przetwarzanie obrazów, dopasowywanie fragmentów oraz obliczenia geometryczne wykorzystywane w procesie dopasowywania obrazów.

=== Zakres testów

- `adjust_photos` – sprawdzenie poprawnego wyrównywania rozmiarów obrazów wejściowych,
- `rotate_and_clean` – weryfikację poprawności obrotu obrazu oraz zachowania liczby kanałów kolorów,
- `calculate_rotation_degree` – sprawdzenie poprawności obliczania kątów obrotu na podstawie danych geometrycznych,
- `calculate_vector` – test obliczania wektora przesunięcia na podstawie wykrytych punktów charakterystycznych,
- `join_photos` – sprawdzenie poprawnego łączenia dwóch obrazów w jeden wynikowy.



== Niepowodzenia testów – analiza błędów

Podczas testowania funkcji `calculate_vector` wystąpił błąd:
Funkcja zakładała, że wykryta czerwona kropka na obrazie składa się z co najmniej trzech pikseli. Założenie to było niejawne i nie zostało wcześniej zabezpieczone w kodzie.  
Początkowy przypadek testowy zawierał pojedynczy piksel, co ujawniło to ograniczenie algorytmu.




== Przykłady

Test „adjust_photos” – dopasowanie rozmiaru i proporcji puzzli przed porównywaniem
Funkcja adjust_photos(img1, img2) ma za zadanie przygotować dwa obrazy tak, aby miały taki sam rozmiar i proporcje, zanim algorytm zacznie szukać punktów wspólnych / dopasowań krawędzi / cech.


Test pokazuje, że po wywołaniu funkcji oba obrazy mają taki sam rozmiar (np. obie mają wysokość 100 px lub obie 200 px – w zależności od implementacji)
proporcje są zachowane kształt puzzla jest nadal widoczny – nie został zniekształcony

#image("before 1.png")
#image("after 1.png")
#image("before 2.png")
#image("after 2.png")

Test integracyjny ujawnił brak obsługi przypadku, w którym algorytm nie wykrywa punktów charakterystycznych. Funkcja _calculate_vector()_ nie posiada zabezpieczenia przed pustym zbiorem punktów, co prowadzi do wyjątku wykonania.


Podczas testu integracyjnego stwierdzono, że funkcja _calculate_vector()_ nie obsługuje przypadku braku wykrytych punktów charakterystycznych. Test ujawnił wyjątek wykonania, co pozwoliło na wprowadzenie mechanizmu zabezpieczającego. Po dodaniu warunku sprawdzającego poprawność danych wejściowych, test zakończył się poprawnie.
= Podsumowanie
Podsumowując ostatnie miesiące pracy nad projektem, to udało nam się spełnić 
podstawowe wymagania i założenia. Przygotowany przez nas program dopasowuje nieregularne
kształty 2D, takie jak fragmenty obrazów czy fresków. Skupiliśmy się wyłącznie na łączeniu
kawałków według kształtów, potencjalne opcjonalne porównywanie kolorów dość szybko odrzuciliśmy.

Nasz program jest w stanie tworzyć pojedyncze dopasowania 
i segregować je według jakości w pełni automatycznie. Przy prostszych przykładach, gdzie 
fragmenty nie są zbyt mocno obrócone i występuje ich mała liczba, cały proces rekonstrukcji
początkowego obrazka przechodzi automatycznie. W pozostałych wypadkach program potrzebuje
odrobinę ludzkiej ingerencji, co jest rozwiązane prostym w obsłudze oknie dialogowym do
akceptowania bądź odrzucania dopasowań.

W trakcie pracy nie nastąpiły żadne radykalne zmiany wykorzystywanego
języka (cały czas trzymaliśmy się Pythona) ani bibliotek (poza paroma dodatkowymi które
musieliśmy zaimportować do pojedynczych funkcji). Jedynie narzędzia pracy zespołowej odrobinę
się zmieniły, ponieważ przeszliśmy z platformy Trello całkowicie na arkusz w Excel'u. 

Realizacja tego projektu stanowiła dla nas praktyczne doświadczenie pracy nad czymś tak rozbudowanym i skomplikowanym. Poznaliśmy lepiej biblioteki do przetwarzania obrazów i niewątpliwie wzmocniliśmy umiejętności rozwiązywania logicznych problemów. Mimo, że nasz program nie jest idealny, to efekt końcowy przerósł nasze oczekiwania ponieważ jeszcze kilka miesięcy wcześniej rekonstrukcja fresków wydawała się dla nas tematem abstrakcyjnym i niemożliwym do zrealizowania. Jednak teraz, po różnych wzlotach i upadkach podczas pracy w zespole, możemy być z siebie zadowoleni.

