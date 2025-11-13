from MainWindow import MainWindow
import sys
from PyQt5.QtWidgets import (QApplication)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.showFullScreen()
    mw.setFixedHeight(mw.display_height)
    app.exec_()
