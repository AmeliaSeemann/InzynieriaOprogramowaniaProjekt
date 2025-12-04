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
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QSlider, QFileDialog, QVBoxLayout, \
    QMessageBox
from photos_opencv import get_crop,open_photo,get_contours

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


        #tu będzie przetrzymywane końcowe zdjęcie połączonych fragmentów
        #konieczne do tego, by je zapisać do pliku
        #w dalszym etapie tworzenia programu, zakładamy że efekt końcowy da
        #się przełożyć na QPixMap
        self.end_result = QPixmap()

        #"łączenie" jest na razie udawane, wczytujemy gotowca tu sprecyzowanego:
        self.temporary_filepath = 'zdjecia/razem.png'

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
        but_sav = self.findChildren(QPushButton)[4]
        but_con.setEnabled(False)
        but_next.setEnabled(False)
        but_prev.setEnabled(False)
        but_sav.setEnabled(False)

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
        
        # przycisk do zapisywania efektu końcowego do wybranego pliku
        button_save= QPushButton("Save photo", self)
        button_save.setCheckable(False)
        button_save.setEnabled(False)
        button_save.setGeometry(int(WINDOW_WIDTH * 0.3525)
                                    , int(WINDOW_HEIGHT * 0.03)
                                    , int(WINDOW_WIDTH * 0.3125)
                                    , int(WINDOW_HEIGHT * 0.08))

        # łączy się z funckją save_photo
        button_save.clicked.connect(self.save_photo)

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
        #przystosowanie do załadowania nowych zdjęć
        self.reset_state()

        #wybór folderu
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(directory)

        #jest try catch jakby ścieżka miała złą nazwę
        try:
            #dopisanie ścieżki do każdego zdjęcia w folderze do listy
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                #przewidujemy na razie tylko .png
                if filename.endswith(".png"):
                    self.photos_list.append(directory + "/" + filename)
                    #potrzebne do przetestowania czy zdjęcie/folder nie ma złej nazwy
                    test = open_photo(self.photos_list[-1])
                    if test is None:
                        raise Exception(f"Invalid path: {self.photos_list[-1]}")


            #odblokowanie paru guzików
            but_con = self.findChildren(QPushButton)[1]
            but_con.setEnabled(True)
            if len(self.photos_list)>1:
                but_next = self.findChildren(QPushButton)[2]
                but_next.setEnabled(True)

            #wyświetlenie pierwszego zdjęcia z folderu
            self.set_photo(self.photos_list[0])
        except Exception as e:
            self.message_box(str(e),"Error")


    def connect_photos(self):

        # pobranie wartosci z suwaka(w senise moze na przyszlosc ? )
        slider = self.findChildren(QSlider)[0]
        precision = slider.value()  # 0–100

        # Im większa precyzja, tym mniejsza tolerancja
        dir_tolerance = int(60 - (precision * 0.5))  # np: od 60 do 10
        len_tolerance = int(80 - (precision * 0.7))

        #zablokowanie przycisku "connect photos"
        #(trzeba załadować nowe by zrobić ponowne połączenie, ale można to zmienić)
        but = self.findChildren(QPushButton)[1]
        but.setEnabled(False)



        #pokazuje gotowe (tymczasowe) zdjęcie połączonych fragmentów
        self.set_photo(self.temporary_filepath)
        self.reset_state()

        #przetrzymuje je jako QPixMap
        self.end_result = QPixmap(self.temporary_filepath)

        #pobiera wartośc dokładności z suwaka i wyświetla odpowiednią informację
        slider = self.findChildren(QSlider)[0]
        self.message_box(f"Photos connected with a {slider.value()}% precision.","Info")

        #można odblokować przycisk do zapisywania efektu końcowego
        but_sav = self.findChildren(QPushButton)[4]
        but_sav.setEnabled(True)

    #zapisywanie końcowego efektu
    def save_photo(self):
        #użytkownik może wybrać gdzie zapisać
        directory = QFileDialog.getSaveFileName(self, "Select File",filter="Images (*.png)")[0]
        #albo się zapisze
        try:
            self.end_result.save(directory[0],"PNG")
            self.message_box(f"Photos saved to {directory[0]}","Success")
        #albo nie
        except Exception as e:
            self.message_box("Something went wrong with saving...","Error")

    #zmiana na następne zdjęcie
    def see_next_photo(self):
        if self.current_photo_index < len(self.photos_list) - 1:
            self.current_photo_index += 1
            self.change_viewed_photo(self.current_photo_index)

    #zmiana na poprzednie zdjęcie
    def see_previous_photo(self):
        if self.current_photo_index > 0:
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

    #żeby wyskakiwało okienko z informacją
    def message_box(self,text,title):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(text)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok)
        returnValue = msgBox.exec()


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
