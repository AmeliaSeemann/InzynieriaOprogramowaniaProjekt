#TESTOWANIE: po kliknięciu "Load Photos" dobrze wybrać któryś z folderów w "zdjęcia"
#Kolejne foldery testowe (jak chcesz je stworzyć) powinny mieć same zdjęcia z png

#Nie trzeba się przejmować "libpng warning: iCCP: known incorrect sRGB profile"
#To po prostu się wypisuje w konsoli i tyle, nic się nie psuje z tego co wiem

#ten plik głównie odpowiada za główny interfejs użytkownika
#(okno do akceptacji czy odrzucenia dopasowania jest w dialog_window.py)
import sys
import os
import cv2 as cv
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QSlider, QFileDialog, QVBoxLayout, \
    QMessageBox, QSpinBox, QLineEdit, QProgressDialog
from photos_opencv import open_photo, get_crop,open_photo,get_contours, detect_edge_features
from matching import true_match_all_photos,draw_matches
from dialog_window import PreviewDialog
import tempfile
import uuid


#rozmiary okna aplikacji
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900


#Wszystko co jest w naszym oknie:
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #ustawianie tytułu i rozmiaru
        self.setWindowTitle("Puzzle Solver 3000")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)

        #tworzenie layout'u, który po prostu trzyma jakieś zdjęcie
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)


        #tu będzie przetrzymywane końcowe zdjęcie połączonych fragmentów
        #konieczne do tego, by je zapisać do pliku
        #w dalszym etapie tworzenia programu, zakładamy że efekt końcowy da
        #się przełożyć na QPixMap
        self.end_result = QPixmap()

        #placeholder
        self.temporary_filepath = 'zdjecia/razem.png'

        #stworzenie ui
        self.ui_components()
        self.reset_state()

        #lista odrzuconych połączeń
        self.rejected_pairs = set()
      
    #do wyczyszczenia listy zdjęć i zablokowania odpowiednich przycisków
    def reset_state(self):
        self.photos_list = []
        self.current_photo_index = 0
        but_con = self.findChildren(QPushButton)[1]
        but_next = self.findChildren(QPushButton)[2]
        but_prev = self.findChildren(QPushButton)[3]
        but_sav = self.findChildren(QPushButton)[4]
        but_edges = self.findChildren(QPushButton)[5]
        but_all = self.findChildren(QPushButton)[6]
        but_con.setEnabled(False)
        but_next.setEnabled(False)
        but_prev.setEnabled(False)
        but_sav.setEnabled(False)
        but_edges.setEnabled(False)
        but_all.setEnabled(False)

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
        button_connect = QPushButton("Connect Photos Manual",self)
        button_connect.setCheckable(False)
        button_load.setEnabled(True)
        button_connect.setGeometry(int(WINDOW_WIDTH * 0.625)
                                , int(WINDOW_HEIGHT * 0.85)
                                , int(WINDOW_WIDTH * 0.3125)
                                , int(WINDOW_HEIGHT * 0.1))

        # łączy się z funckją connect_photos
        button_connect.clicked.connect(self.connect_photos)

        
        #przycisk do zobaczenia następnego zdjęcia z załadowanych
        #nie da się go kliknąć póki nie załadowano zdjęć
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
        button_save.setGeometry(int(WINDOW_WIDTH * 0.3825)
                                    , int(WINDOW_HEIGHT * 0.03)
                                    , int(WINDOW_WIDTH * 0.2525)
                                    , int(WINDOW_HEIGHT * 0.08))

        # łączy się z funckją save_photo
        button_save.clicked.connect(self.save_photo)

        # przycisk do wykrywania krawędzi
        # nie da się go kliknąć, póki nie załadowano zdjęć
        button_show_edges = QPushButton("Show edges", self)
        button_show_edges.setCheckable(False)
        button_show_edges.setEnabled(False)
        button_show_edges.setGeometry(int(WINDOW_WIDTH * 0.6825)
                                    , int(WINDOW_HEIGHT * 0.03)
                                    , int(WINDOW_WIDTH * 0.2825)
                                    , int(WINDOW_HEIGHT * 0.08))
        # łączy się z funckją show_edges
        button_show_edges.clicked.connect(self.show_edges)

        # === STITCH ALL ===
        self.button_stitch_all = QPushButton("Connect All", self)
        self.button_stitch_all.setCheckable(False)
        self.button_stitch_all.setEnabled(False)
        self.button_stitch_all.setGeometry(
            int(WINDOW_WIDTH * 0.0525),
            int(WINDOW_HEIGHT * 0.03),
            int(WINDOW_WIDTH * 0.2825),
            int(WINDOW_HEIGHT * 0.08)
        )
        self.button_stitch_all.clicked.connect(self.connect_all_photos)

        # #Suwak do ustawiania precyzji (prototypowo od 0 do 100)
        # slider_decription = QLabel(self)
        # slider_decription.setText("Change precision:",)
        # slider_decription.setGeometry(int(WINDOW_WIDTH * 0.4125),int(WINDOW_HEIGHT * 0.85),
        #                               int(WINDOW_WIDTH * 0.1625),int(WINDOW_HEIGHT * 0.05))

        # precision_slider = QSlider(Qt.Horizontal,self)
        # precision_slider.setRange(0,100)
        # precision_slider.setValue(50)
        # precision_slider.setTickPosition(QSlider.TicksBelow)
        # precision_slider.setGeometry(int(WINDOW_WIDTH * 0.4375), int(WINDOW_HEIGHT * 0.917),
        #                              int(WINDOW_WIDTH * 0.125), int(WINDOW_HEIGHT * 0.05))

        # #etykieta z procentami
        # precision_value_label = QSpinBox(self)
        # precision_value_label.setRange(0,100)
        # precision_value_label.setValue(50)
        # precision_value_label.setSuffix(" %")
        # precision_value_label.setGeometry(
        #     int(WINDOW_WIDTH * 0.48),
        #     int(WINDOW_HEIGHT * 0.96),  # troszkę niżej od suwaka
        #     int(WINDOW_WIDTH * 0.05),
        #     int(WINDOW_HEIGHT * 0.03)
        # )

        # #Synchronizacja: suwak -> pole tekstowe
        # precision_slider.valueChanged.connect(precision_value_label.setValue)

        # #Synchronizacja: pole tekstowe -> suwak
        # precision_value_label.valueChanged.connect(precision_slider.setValue)
        # ====== INFO O AKTUALNYM ZDJĘCIU ======
        self.photo_counter_label = QLabel(self)
        self.photo_counter_label.setText("Photo: 0 / 0")
        self.photo_counter_label.setAlignment(Qt.AlignCenter)
        self.photo_counter_label.setGeometry(
            int(WINDOW_WIDTH * 0.4),
            int(WINDOW_HEIGHT * 0.85),
            int(WINDOW_WIDTH * 0.2),
            int(WINDOW_HEIGHT * 0.05    
            )   )
        # ====== PRZEJŚCIE DO KONKRETNEGO ZDJĘCIA ======
        self.goto_photo_input = QLineEdit(self)
        self.goto_photo_input.setPlaceholderText("Go to photo #")
        self.goto_photo_input.setGeometry(
            int(WINDOW_WIDTH * 0.42),
            int(WINDOW_HEIGHT * 0.91),
            int(WINDOW_WIDTH * 0.17),
            int(WINDOW_HEIGHT * 0.05)
        )
        self.goto_photo_input.returnPressed.connect(self.go_to_photo)

    # Działa bardzo podobnie do connect photos, ale robi to automatycznie
    # dla wszystkich zdjęć
    # Niestety działa tylko dla prostych przypadków i może się zaciąć
    def connect_all_photos(self):
        try:
            # Sprawdzamy, czy mamy z czym pracować
            if len(self.photos_list) < 2:
                self.message_box("Need at least 2 photos to connect!", "Info")
                return

            # Przygotowanie okna postępu
            progress = QProgressDialog("Automatic connection... Please wait.", "Cancel", 0, len(self.photos_list), self)
            progress.setWindowTitle("Connecting process")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            steps = 0   

            
            # Pętla działa dopóki mamy więcej niż jedno zdjęcie na liście
            while len(self.photos_list) > 1:
                # Pozwala na zamknięcie okna przez "Anuluj"
                if progress.wasCanceled():
                    break

                # Szukamy wszystkich dopasowań dla aktualnej listy zdjęć
                matches = true_match_all_photos(self.photos_list)
                
                if not matches:
                    self.message_box("No more matches found. Stopping stitching.", "Finished")
                    break

                # Pobieramy najlepsze dopasowanie (zawsze pierwsze z posortowanej listy)
                # Pomijamy rysowanie diangli, interesuje nas tylko wynik połączenia
                best_image, angle, idx1, idx2 = draw_matches(
                    matches,
                    self.photos_list,
                    self.rejected_pairs
                )

                # Zapisujemy połączony fragment do pliku tymczasowego
                temp_path = os.path.join(
                    tempfile.gettempdir(),
                    f"auto_combined_{uuid.uuid4().hex}.png"
                )
                cv.imwrite(temp_path, best_image)

                # Aktualizacja listy zdjęć: usuwamy stare, wstawiamy nowe
                # Ważne: usuwamy od tyłu, żeby indeksy się nie przesuwały w trakcie
                indices_to_remove = sorted([idx1, idx2], reverse=True)
                for idx in indices_to_remove:
                    del self.photos_list[idx]

                # Wstawiamy połączone zdjęcie w miejsce, gdzie był jeden z oryginałów
                insert_idx = min(idx1, idx2)
                self.photos_list.insert(insert_idx, temp_path)
                
                # Aktualizacja UI i paska postępu
                steps += 1
                progress.setValue(steps)
                self.set_photo(temp_path)
                self.update_photo_counter()
                QApplication.processEvents() 

            progress.close() # Zamykamy okno postępu
                
                # # Opcjonalnie: aktualizacja UI na bieżąco (może spowalniać, ale daje podgląd)
                # self.set_photo(temp_path)
                # self.update_photo_counter()
                # QApplication.processEvents() # Odświeża okno, żeby nie "zamarzło"

            # gdy nam zostanie jedno zdjęcie (końcowy efekt)
            if len(self.photos_list) == 1:
                final_path = self.photos_list[0]
                self.end_result = QPixmap(final_path)
                self.set_photo(final_path)

                # Aktywujemy przycisk zapisu i blokujemy nawigację
                but_save = self.findChildren(QPushButton)[4]
                but_save.setEnabled(True)
                
                but_next = self.findChildren(QPushButton)[2]
                but_next.setEnabled(False)
                but_prev = self.findChildren(QPushButton)[3]
                but_prev.setEnabled(False)
                
                but_con = self.findChildren(QPushButton)[1]
                but_con.setEnabled(False)

                but_all = self.findChildren(QPushButton)[6]
                but_all.setEnabled(False)

                self.message_box("All photos successfully connected into one image!", "Success")

        except Exception as e:
            self.message_box(f"{str(e)}", "Error")


    def update_photo_counter(self):
        if not self.photos_list:
            self.photo_counter_label.setText("Photo: 0 / 0")
        else:
            self.photo_counter_label.setText(
                f"Photo: {self.current_photo_index + 1} / {len(self.photos_list)}"
            )
    def go_to_photo(self):
        if not self.photos_list:
            return

        try:
            index = int(self.goto_photo_input.text()) - 1
            if 0 <= index < len(self.photos_list):
                self.current_photo_index = index
                self.change_viewed_photo(index)
            else:
                self.message_box("Photo number out of range", "Error")
        except ValueError:
            self.message_box("Please enter a valid number", "Error")


    def load_photos(self):
        #przystosowanie do załadowania nowych zdjęć
        self.reset_state()

        #wybór folderu
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        #jest try catch jakby ścieżka miała złą nazwę
        try:
            #do wyświetlania realnego indeksu zdjęcia
            i = 0
            #dopisanie ścieżki do każdego zdjęcia w folderze do listy
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                #przewidujemy na razie tylko .png
                if filename.endswith(".png"):
                    print(filename, f"(REAL index: {i})")
                    i+=1
                    self.photos_list.append(directory + "/" + filename)
                    #potrzebne do przetestowania czy zdjęcie/folder nie ma złej nazwy
                    test = open_photo(self.photos_list[-1])
                    if test is None:
                        raise Exception(f"Invalid path: {self.photos_list[-1]}")

        except Exception as e:
            self.message_box(str(e),"Error")
        finally:
            #odblokowanie paru guzików
            self.set_photo(self.photos_list[0])
            self.update_photo_counter()

            but_all = self.findChildren(QPushButton)[6]
            but_all.setEnabled(True)
            but_con = self.findChildren(QPushButton)[1]
            but_con.setEnabled(True)
            if len(self.photos_list)>1:
                but_next = self.findChildren(QPushButton)[2]
                but_next.setEnabled(True)
            but_egdes = self.findChildren(QPushButton)[5]
            but_egdes.setEnabled(True)

            #wyświetlenie pierwszego zdjęcia z folderu
            self.set_photo(self.photos_list[0])


    #do łączenia zdjęć
    def connect_photos(self):
        try: 

            # jeśli mamy mniej niż 2 zdjęcia, nic nie robimy
            if len(self.photos_list) < 2:
                return
            

            # dopasowujemy wszystkie zdjęcia do siebie
            matches = true_match_all_photos(self.photos_list)

            # wybieramy najlepsze dopasowanie (zdjęcia + kąt) pomijając już odrzucone pary
            best_image, angle, idx1, idx2 = draw_matches(
                matches,
                self.photos_list,
                self.rejected_pairs
            )

            # pokazujemy okno podglądu połączonych zdjęć
            dialog = PreviewDialog(best_image, self)

            if dialog.exec():  # ACCEPT
                # zapisujemy wynik tymczasowo
                temp_path = os.path.join(
                    tempfile.gettempdir(),
                    f"combined_{uuid.uuid4().hex}.png"
                )
                cv.imwrite(temp_path, best_image)

                # usuwamy z listy stare zdjęcia, które zostały połączone
                for idx in sorted([idx1, idx2], reverse=True):
                    del self.photos_list[idx]

                # wstawiamy nowy obraz w miejsce pierwszego z połączonych
                insert_idx = min(idx1, idx2)
                self.photos_list.insert(insert_idx, temp_path)
                self.update_photo_counter()

                self.current_photo_index = insert_idx
                self.set_photo(temp_path)

                self.update_photo_counter()

        
                # po zaakceptowaniu połączenia możemy wyczyścić listę odrzuconych par,
                # nowe krawędzie = możliwe nowe połączenia
                self.rejected_pairs.clear()

                # aktywujemy zapis
                # jeśli został tylko jeden obraz, to jest to wynik końcowy
                if len(self.photos_list) == 1:
                    final_path = self.photos_list[0]
                    self.end_result = QPixmap(final_path)

                    but_save = self.findChildren(QPushButton)[4]
                    but_save.setEnabled(True)
                    but_next = self.findChildren(QPushButton)[2]
                    but_next.setEnabled(False)
                    but_con = self.findChildren(QPushButton)[1]
                    but_con.setEnabled(False)
                    but_all = self.findChildren(QPushButton)[6]
                    but_all.setEnabled(False)

                    self.message_box("All photos successfully connected into one image!", "Success")


                #self.message_box("Photos connected!", "Success")
            else:  # REJECT
                # dodajemy parę do listy odrzuconych, żeby nie pokazywać jej ponownie
                self.rejected_pairs.add(tuple(sorted((idx1, idx2))))

            # aktualizacja przycisków nawigacyjnych
            if self.current_photo_index >= 1:
                but_prev = self.findChildren(QPushButton)[3]
                but_prev.setEnabled(True)
            if self.current_photo_index == 0:
                but_prev = self.findChildren(QPushButton)[3]
                but_prev.setEnabled(False)
            if self.current_photo_index <= len(self.photos_list) - 1:
                but_next = self.findChildren(QPushButton)[2]
                but_next.setEnabled(False)
            if self.current_photo_index < len(self.photos_list) - 1:
                but_next = self.findChildren(QPushButton)[2]
                but_next.setEnabled(True)
        except Exception as e:
            self.message_box(str(e),"Brak połączeń")


    #zapisywanie końcowego efektu
    def save_photo(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Select File",
            filter="Images (*.png)"
        )

        if not filepath:
            return

        try:
            self.end_result.save(filepath, "PNG")
            self.message_box(f"Photos saved to:\n{filepath}", "Success")
        except Exception as e:
            self.message_box(str(e), "Error")

    # do pokazywania krawędzi i wierzchołków zdjęcia
    def show_edges(self):
        if not self.photos_list:
            return
        try:
            photo = self.photos_list[self.current_photo_index]

            # wykrywanie wypustek i wcięć
            features, vis = detect_edge_features(
                photo,
                k=10,
                angle_thresh_deg=15,
                min_separation=12,
                visualize=True
            )

            print("Detected features:", features)

            if vis is not None:
                cv.imshow("Detected features", vis)
                cv.waitKey(0)
                cv.destroyAllWindows()

            self.message_box(
                f"Detected {len(features)} of edges features",
                "Info"
            )
        except Exception as e:
            self.message_box(str(e),"Oopsie")

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

        self.update_photo_counter()


    #ustawianie konkretnego zdjęcia jakie ma być widoczne
    #"to_what" to ścieżka do zdjęcia
    def set_photo(self, to_what):
        #tworzenie label ze zdjęciem w środku
        label = QLabel(self)
        pixmap = QPixmap(to_what)

        #wcześniej było przycinane, teraz już nie jest
        cropped_pixmap = pixmap
        width = cropped_pixmap.width()
        height = cropped_pixmap.height()

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
        msgBox.exec()


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

