from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from konfig import *

if __name__ == '__main__':
    menu = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle('Chess game')
    window.setGeometry(300, 200, WINDOW_SIZE[0], WINDOW_SIZE[1])
    window.show()
    sys.exit(menu.exec_())
