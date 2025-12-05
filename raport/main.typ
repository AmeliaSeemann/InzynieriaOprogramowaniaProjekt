#import "@preview/outrageous:0.4.0"
#import "@preview/lovelace:0.3.0": *
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#show: codly-init.with()

#codly(languages: codly-languages)

// #import "@preview/zero:0.5.0": num, set-round
// Potrzebny https://github.com/Mc-Zen/zero/pull/45
#import "typst-pkg/zero-06b9cfa/zero.typ": num, set-round

#set-round(mode: "figures", precision: 3, pad: false)

#import "@preview/lilaq:0.5.0" as lq
#set text(size: 12pt, lang: "pl", font: "New Computer Modern")
#set page(margin: 3.5cm)
#set par(justify: true)
#set heading(numbering: "1.1  ")
#show heading: set block(below: 1em)
#show outline.entry: outrageous.show-entry.with(font: ("New Computer Modern", auto))
#show bibliography: set heading(numbering: "1.1  ")
#show figure: set block(breakable: true)
#show figure.where(kind: table): set figure.caption(position: top)

#align(center)[
  #image("media/ps-logo.svg", width: 33%)

  #v(3em)

  Wykorzystanie narzędzi pracy zespołowej i harmonogramowanie w projekcie

  #v(1em)

  #text(size: 1.5em)[
    *Automatyczne dopasowanie fragmentów 2D o 
    nieregularnych krawędziach*

    _Inżynieria Oprogramowania_
  ]
]

#v(1em)

#align(right)[
  Kierunek: Informatyka

  Członkowie zespołu: #linebreak()
  _Amelia Seemann_ #linebreak()
  _Yana Ivanyna_ #linebreak()
  _Zuzanna Zięba_
]

#v(1fr)

#align(center)[Gliwice, 2025/2026]

#pagebreak()

#counter(page).update(1)
#set page(numbering: "1")

#outline()

#pagebreak()
#show link: underline

= Wprowadzenie
== Dokumentacja Czasu Pracy

Zarządzanie czasem w projekcie polegało na regularnym zapisywaniu informacji w arkuszu Microsoft Excel. Za każdym razem, gdy zabieraliśmy się za kolejną część projektu lub pojawiał się nowy pomysł do realizacji, zapisywaliśmy go w arkuszu wraz z estymowanym czasem wykonania. Po zakończeniu zadania uzupełnialiśmy te dane o rzeczywisty czas pracy.

\
W arkuszu uwzględnialiśmy następujące informacje:
- *Zadanie* – opis tego, co zamierzaliśmy zrobić w ramach projektu,

- *Wykonawca* - kto odpowiada za daną część,

- *Estymowany czas* – przewidywany czas potrzebny na wykonanie zadania,

- *Rzeczywisty czas* – faktyczny czas poświęcony na jego realizację,

- *Procentowy wkład* – obliczany na bieżąco udział danej osoby w projekcie,

- *Łączny czas* – suma rzeczywistego czasu pracy, przedstawiona w godzinach.


Taka forma dokumentacji umożliwiała nam kontrolowanie postępów oraz analizę różnic pomiędzy planowanym a rzeczywistym czasem realizacji zadań.

#figure(image("media/wykres procentowy.png"))

== Opracowanie Projektu na platformie trello
Trello służyło nam jako główne narzędzie do organizowania prac nad projektem automatycznego dopasowania fragmentów 2D o nieregularnych krawędziach. Dzięki platformie mogliśmy sprawnie definiować zadania oraz utrzymywać jasną strukturę działań potrzebnych do realizacji projektu.

#pagebreak()
= Realizacja zadania
== Analiza postępów pracy

Analizując naszą pracę, można stwierdzić, że dokonaliśmy zauważalnych postępów w realizacji projektu. Zdobyliśmy znaczną część wiedzy potrzebnej do jego wykonania, a także wykonaliśmy pierwsze elementy praktyczne, w tym prace nad modułami związanymi z przetwarzaniem obrazu i wykrywaniem krawędzi. Do tej pory większość działań miała charakter przygotowawszy i teoretyczny, jednak coraz większą rolę zaczyna odgrywać część praktyczna, bezpośrednio związana z rozwojem aplikacji.

#pagebreak()
== Analiza czasu pracy

Analizując zestawienia całkowitego czasu estymowanego i rzeczywistego dla poszczególnych członków zespołu można zauważyć niewielkie różnice między zaplanowanym a faktycznym czasem pracy. Jednym z najważniejszych wniosków jest fakt, że w większości przypadków rzeczywisty czas wykonania zadania okazywał się dłuższy niż czas estymowany, co wskazuje na częste niedoszacowanie nakładu pracy. Z kolei sytuacje, w których czas został przeszacowany, pojawiały się znacznie rzadziej i miały mniejszą skalę. Ogólnie rzecz biorąc, różnice te nie są duże, co sugeruje, że estymacja czasu pracy w zespole była dość trafna, choć w przyszłości warto nadal doskonalić proces planowania, aby jeszcze bardziej zminimalizować rozbieżności między zaplanowanym czasem a rzeczywistym.

Różnice między czasem szacowanym a rzeczywistym mogą wynikać z kilku czynników, takich jak:

- *Nieprzewidziane trudności i problemy techniczne* – w trakcie pracy mogą pojawić się błędy, komplikacje lub utrudnienia, które opóźniają wykonanie zadania.
- *Niedokładna ocena stopnia trudności* – zadania, które wydają się prostsze na etapie planowania, w praktyce okazują się bardziej czasochłonne.
- *Nieuwzględnianie przerw i zmęczenia* – podczas szacowania często pomija się krótkie przerwy oraz spadek koncentracji, co wpływa na wydłużenie czasu realizacji zadania.
- *Brak łatwo dostępnych informacji na dany temat* – w niektórych przypadkach odnalezienie potrzebnych, wiarygodnych materiałów wymagało długiego przeszukiwania internetu oraz porównywania różnych źródeł, co znacząco wydłużało czas realizacji zadania.

#figure(image("media/estymata_a_rzeczywisty.png"), caption: [Wykres przedstawiający czas szacowany, a czas przepracowany dla jednej osoby])


#pagebreak()
== Analiza przepracowanych godzin

W ramach projektu przeprowadzono analizę rzeczywistego czasu pracy w porównaniu z wcześniejszymi estymacjami. Dane zestawiono w tabeli, uwzględniając liczbę wpisów, szacowany czas pracy, faktycznie przepracowane godziny oraz łączną liczbę dni roboczych.

#figure(image("media/tabelka_godziny.png"))

Z analizy wynika, że całkowity rzeczywisty czas poświęcony na realizację projektu wyniósł 63,25 godziny (stan na 4 grudnia 2025), co odpowiada około 9,25 dnia roboczego. W porównaniu do estymowanego czasu (61,75 godziny), różnica jest niewielka, co świadczy o stosunkowo trafnym oszacowaniu zakresu pracy.

#pagebreak()
= Dalszy rozwój pracy

W kontekście dalszego rozwoju projektu, skupimy się w szczególności na powiązaniu ze sobą zaimplementowanych funkcji, takich jak dopasowywanie cech zdjęć i wstępne sortowanie fragmentów. Większość tych funkcji istnieje w formie raczej odklejonej od siebie, połączymy je ze sobą oraz z funkcjami dostępnymi z interfejsu użytkownika. Sam interfejs użytkownika również zostanie dopracowany pod względem estetytycznym, a z czasem niektóre guziki oraz okna, przydatne wyłącznie w testowaniu, zostaną schowane. Wraz ze wzrostem rozmiaru projektu trzeba będzie również rozdzielić go na dobrze uporządkowany zestaw plików, ponieważ dwa to już powoli za mało. Warto też wspomnieć, że zajmiemy się zagadanieniem optymalizacji naszych rozwiązań oraz ich obszernym testowaniem na różnych zestawach zdjęć, aby mieć pewność do do ich poprawności. Podsumowując zestaw naszych dalszych planów, skupimy się na: przerzuceniu teoretycznie istniejących funkcji w strefę praktyczną, powiązaniu tego co dzieje się "za kulisami" z interfejsem użytkownika, dopracowaniem samego interfejsu oraz optymalizacją i testowaniem tego, co jak dotąd stworzyliśmy.

\
= Podsumowanie

W trakcie realizacji projektu przeprowadziliśmy dokładną analizę czasu pracy oraz postępów związanych z tworzeniem systemu automatycznego dopasowania fragmentów 2D o nieregularnych krawędziach. Systematyczne zapisywanie estymacji i rzeczywistych godzin pozwoliło nam lepiej kontrolować przebieg prac i zidentyfikować główne przyczyny rozbieżności - przede wszystkim nieprzewidziane przerwy oraz problemy techniczne.

Zgromadzone dane umożliwiły wskazanie obszarów wymagających usprawnień oraz dokładniejsze planowanie kolejnych etapów projektu. Zaobserwowaliśmy również widoczny rozwój projektu, zwłaszcza w zakresie tworzenia narzędzi do analizy obrazu oraz zdobywania informacji niezbędnych do opracowania algorytmów dopasowania elementów 2D.

Podsumowując, projekt rozwija się w stabilnym tempie, stopniowo przechodząc od zagadnień teoretycznych do zadań praktycznych. Regularne monitorowanie postępów i czasu pracy pozwala nam skuteczniej zarządzać projektem i sprawnie realizować kolejne cele.