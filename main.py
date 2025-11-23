import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QSlider

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(WINDOW_HEIGHT)
        self.ui_components()


    def ui_components(self):
        button_load = QPushButton("Load Photos",self)
        button_load.setCheckable(False)
        button_load.clicked.connect(self.load_photos)
        button_load.setGeometry(int(WINDOW_WIDTH * 0.0625)
                                ,int(WINDOW_HEIGHT * 0.85)
                                ,int(WINDOW_WIDTH * 0.3125)
                                ,int(WINDOW_HEIGHT * 0.1))
        button_load.show()

        button_connect = QPushButton("Connect Photos",self)
        button_connect.setCheckable(False)
        button_connect.setGeometry(int(WINDOW_WIDTH * 0.625)
                                , int(WINDOW_HEIGHT * 0.85)
                                , int(WINDOW_WIDTH * 0.3125)
                                , int(WINDOW_HEIGHT * 0.1))
        button_connect.clicked.connect(self.connect_photos)


        button_next = QPushButton(">>",self)
        button_next.setCheckable(False)
        button_next.setGeometry(int(WINDOW_WIDTH * 0.85)
                                , int(WINDOW_HEIGHT * 0.4)
                                , int(WINDOW_WIDTH * 0.1)
                                , int(WINDOW_HEIGHT * 0.1))
        button_next.clicked.connect(self.see_next_photo)

        button_previous = QPushButton("<<",self)
        button_previous.setCheckable(False)
        button_previous.setGeometry(int(WINDOW_WIDTH * 0.05)
                                , int(WINDOW_HEIGHT * 0.4)
                                , int(WINDOW_WIDTH * 0.1)
                                , int(WINDOW_HEIGHT * 0.1))
        button_previous.clicked.connect(self.see_previous_photo)


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
        print("(Loading Photos)")

    def connect_photos(self):
        print("(Connecting Photos)")

    def see_next_photo(self):
        print(">>")

    def see_previous_photo(self):
        print("<<")

app = QApplication(sys.argv)

label_font = QFont()
label_font.setPointSize(11)
button_font = QFont()
button_font.setPointSize(14)
QApplication.setFont(label_font,"QLabel")
QApplication.setFont(button_font,"QPushButton")

window = MainWindow()
window.show()
app.exec()