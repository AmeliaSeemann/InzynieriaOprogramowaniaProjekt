import cv2 as cv
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class PreviewDialog(QDialog):
    def __init__(self, cv_image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accept connection?")
        self.setFixedSize(900, 700)

        layout = QVBoxLayout(self)

        # ===== Obraz =====
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        pixmap = self.cv_to_qpixmap(cv_image)
        self.image_label.setPixmap(
            pixmap.scaled(850, 600, Qt.KeepAspectRatio)
        )

        # ===== Przyciski =====
        buttons = QHBoxLayout()

        accept_btn = QPushButton("Accept")
        reject_btn = QPushButton("Reject")

        accept_btn.clicked.connect(self.accept)
        reject_btn.clicked.connect(self.reject)

        buttons.addWidget(accept_btn)
        buttons.addWidget(reject_btn)

        layout.addLayout(buttons)

    def cv_to_qpixmap(self, img):
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        h, w, ch = img.shape
        qimg = QImage(img.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)
