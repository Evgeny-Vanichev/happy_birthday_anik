from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QFont
from pirate_test import *
import sys

SCREEN_SIZE = [500, 500]


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(432, 134, *SCREEN_SIZE)
        self.setWindowTitle('Задание')

        self.pixmap = QPixmap('data/pirate.jpg')
        self.image = QLabel(self)
        self.image.move(120, 120)
        self.image.resize(256, 256)
        self.image.setPixmap(self.pixmap)

        self.test_btn = QPushButton('Начать тест', self)
        self.test_btn.resize(200, 40)
        self.test_btn.move(160, 390)

        self.hello_label = QLabel(self)
        self.hello_label.move(50, 20)
        self.hello_label.setText('Пройди тест, чтобы выжить!')
        self.hello_label.setFont(QFont("Times", 20, QFont.Bold))

        self.test_btn.clicked.connect(self.click)

    def click(self):
        self.close()
        self.application = thorpy.Application(size=(500, 500), caption="Guess the number")
        self.test = PirateTest(0)
        self.test.launch_game()
        self.application.quit()