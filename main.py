#TESTOWANIE: po kliknięciu "Load Photos" dobrze wybrać któryś z folderów w "zdjęcia"
#Kolejne foldery testowe (jak chcesz je stworzyć) powinny mieć same zdjęcia z png
#Aktualnie zdjęcie "razem.png" to placeholder efektu dopasowania wszystkicg=h fragmentów

#Nie trzeba się przejmować "libpng warning: iCCP: known incorrect sRGB profile"
#To po prostu się wypisuje w konsoli i tyle, nic się nie psuje z tego co wiem

#ten plik głównie odpowiada za interfejs użytkownika
#wszystko związane z algorytmem dopasowywania fragmentów na pewno ma być w innym pliku
import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QSlider, QFileDialog, QVBoxLayout
from photos_opencv import get_crop

#rozmiary okna aplikacji, można zmieniać do testowania
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900


#Wszystko co jest w naszym oknie:
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #ustawianie tytułu i rozmiaru
        self.setWindowTitle("Test")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)

        #tworzenie layout'u, który po prostu trzyma jakieś zdjęcie
        #nie ruszać tego
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        #stworzenie ui
        self.ui_components()
        self.reset_state()

    #do wyczyszczenia listy zdjęć i zablokowania odpowiednich przycisków
    def reset_state(self):
        self.photos_list = []
        self.current_photo_index = 0
        but_con = self.findChildren(QPushButton)[1]
        but_next = self.findChildren(QPushButton)[2]
        but_prev = self.findChildren(QPushButton)[3]
        but_con.setEnabled(False)
        but_next.setEnabled(False)
        but_prev.setEnabled(False)

    #tworzenie iterfejsu
    def ui_components(self):
        #przycisk do ładowania folderu ze zdjęciami
        button_load = QPushButton("Load Photos",self)
        button_load.setCheckable(False)

        #łączy się z funckją load_photos
        button_load.clicked.connect(self.load_photos)
        button_load.setGeometry(int(WINDOW_WIDTH * 0.0625)
                                ,int(WINDOW_HEIGHT * 0.85)
                                ,int(WINDOW_WIDTH * 0.3125)
                                ,int(WINDOW_HEIGHT * 0.1))
        button_load.show()

        #przycisk do dopasowywania zdjęć
        #nie da się go kliknąć póki nie załadowano zdjęć
        button_connect = QPushButton("Connect Photos",self)
        button_connect.setCheckable(False)
        button_load.setEnabled(True)
        button_connect.setGeometry(int(WINDOW_WIDTH * 0.625)
                                , int(WINDOW_HEIGHT * 0.85)
                                , int(WINDOW_WIDTH * 0.3125)
                                , int(WINDOW_HEIGHT * 0.1))

        # łączy się z funckją connect_photos
        button_connect.clicked.connect(self.connect_photos)

        #przycisk do zobaczenia następnego zdjęcia z załadowanych
        # nie da się go kliknąć póki nie załadowano zdjęć
        button_next = QPushButton(">>",self)
        button_next.setCheckable(False)
        button_next.setEnabled(False)
        button_next.setGeometry(int(WINDOW_WIDTH * 0.85)
                                , int(WINDOW_HEIGHT * 0.4)
                                , int(WINDOW_WIDTH * 0.1)
                                , int(WINDOW_HEIGHT * 0.1))

        #łączy się z funckją see_next_photo
        button_next.clicked.connect(self.see_next_photo)

        #przycisk do zobaczenia wcześniejszego zdjęcia z załadowanych
        # nie da się go kliknąć póki nie załadowano zdjęć
        button_previous = QPushButton("<<",self)
        button_previous.setCheckable(False)
        button_previous.setEnabled(False)
        button_previous.setGeometry(int(WINDOW_WIDTH * 0.05)
                                , int(WINDOW_HEIGHT * 0.4)
                                , int(WINDOW_WIDTH * 0.1)
                                , int(WINDOW_HEIGHT * 0.1))

        # łączy się z funckją see_previous_photo
        button_previous.clicked.connect(self.see_previous_photo)

        #Suwak do ustawiania precyzji (prototypowo od 0 do 100)
        slider_decription = QLabel(self)
        slider_decription.setText("Change precision:",)
        slider_decription.setGeometry(int(WINDOW_WIDTH * 0.4125),int(WINDOW_HEIGHT * 0.85),
                                      int(WINDOW_WIDTH * 0.1625),int(WINDOW_HEIGHT * 0.05))

        precision_slider = QSlider(Qt.Horizontal,self)
        precision_slider.setRange(0,100)
        precision_slider.setValue(50)
        precision_slider.setTickPosition(QSlider.TicksBelow)
        precision_slider.setGeometry(int(WINDOW_WIDTH * 0.4375), int(WINDOW_HEIGHT * 0.917),
                                     int(WINDOW_WIDTH * 0.125), int(WINDOW_HEIGHT * 0.05))

    def load_photos(self):
        #wybór folderu
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        try:
            #dopisanie ścieżki do każdego zdjęcia w folderze do listy
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.endswith(".png"):
                    self.photos_list.append(directory + "/" + filename)

            #odblokowanie paru guzików
            but_con = self.findChildren(QPushButton)[1]
            but_con.setEnabled(True)
            but_next = self.findChildren(QPushButton)[2]
            but_next.setEnabled(True)

            #wyświetlenie pierwszego zdjęcia z folderu
            self.set_photo(self.photos_list[0])

        #do potencjalnego ulepszenia
        except Exception as e:
            print(e)

    def connect_photos(self):
        #zablokowanie przycisku "connect photos"
        #(trzeba załadować nowe by zrobić ponowne połączenie, ale można to zmienić)
        but = self.findChildren(QPushButton)[1]
        but.setEnabled(False)

        # oczywiście tylko symuluje działanie
        # w praktyce tu się wykona metoda faktycznie łącząca kawałki
        # i zwracająca tego rezultat
        self.set_photo('zdjecia/razem.png')
        self.reset_state()

        #pobiera wartośc dokładności z suwaka
        slider = self.findChildren(QSlider)[0]
        print(f"Połączono zdjęcia z domniemaną dokładnością {slider.value()} procent.")

    #zmiana na następne zdjęcie
    def see_next_photo(self):
        self.current_photo_index += 1
        self.change_viewed_photo(self.current_photo_index)

    #zmiana na poprzednie zdjęcie
    def see_previous_photo(self):
        self.current_photo_index -= 1
        self.change_viewed_photo(self.current_photo_index)

    #do zmieniania zdjęcia w środku na wybrane (index) z photo_list
    def change_viewed_photo(self, index):
        #ustawienie zdjęcia
        self.set_photo(self.photos_list[index])

        #dostanie się do przycisków
        but_next = self.findChildren(QPushButton)[2]
        but_prev = self.findChildren(QPushButton)[3]

        #jeżeli to ostatnie zdjęcie, to przycisk ">>" jest wyłączony
        #inaczej włączony
        if (index == len(self.photos_list) - 1):
            but_next.setEnabled(False)
        else:
            but_next.setEnabled(True)

        #jeżeli to pierwsze zdjęcie, to przycisk "<<" jest wyłączony
        # inaczej włączony
        if (index == 0):
            but_prev.setEnabled(False)
        else:
            but_prev.setEnabled(True)

    #ustawianie konkretnego zdjęcia jakie ma być widoczne
    #"to_what" to ścieżka do zdjęcia
    def set_photo(self, to_what):
        #tworzenie label ze zdjęciem w środku
        label = QLabel(self)
        pixmap = QPixmap(to_what)

        #zdobycie wartości do odpowiedniego przycięcia ustawianego zdjęcia
        x, y, width, height = get_crop(to_what)

        #przycięcie zdjęcia
        cropped_pixmap = pixmap.copy(x, y, width, height)

        #wsadzenie przyciętego zdjęcia do label
        label.setPixmap(cropped_pixmap)

        #usunięcie poprzedniego label ze zdjęciem z layout'u
        lay = self.findChild(QVBoxLayout)
        for i in reversed(range(lay.count())):
            if (type(lay.itemAt(i).widget()) == QLabel):
                lay.removeWidget(lay.itemAt(i).widget())
                break

        #jeżeli przycięte zdjęcie jest mniejsze niż okno programu
        #to je wyśrodkowywujemy
        if width < WINDOW_WIDTH and height < WINDOW_HEIGHT:
            lay.setContentsMargins(int((WINDOW_WIDTH-width)/2),int((WINDOW_WIDTH-width)/2),
                                   int((WINDOW_HEIGHT-height)/2),int((WINDOW_HEIGHT-height)/2))

        #jeżeli jest większe to je pomniejszamy by się zmieściło
        else:
            scale = max(width / WINDOW_WIDTH,height / WINDOW_HEIGHT)
            scaled_pixmap = cropped_pixmap.scaled(int(width/scale),int(height/scale),Qt.KeepAspectRatio)
            label.setPixmap(scaled_pixmap)
            lay.setContentsMargins(0,0,0,0)

        #dodanie aktualnego label do layout'u
        lay.addWidget(label)


#tego nie ruszać
app = QApplication(sys.argv)


#ustawianie czcionki dla label i pushbutton
label_font = QFont()
label_font.setPointSize(11)
button_font = QFont()
button_font.setPointSize(14)
QApplication.setFont(label_font,"QLabel")
QApplication.setFont(button_font,"QPushButton")

#tego nie ruszać
window = MainWindow()
window.show()
app.exec()