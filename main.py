import sys
import os
from PyQt5.QtWidgets import QApplication
import scripts.gui as gui

if __name__ == '__main__':
    gui.c4.set_dirpath(os.path.dirname(os.path.realpath(__file__)))
    app = QApplication(sys.argv)
    ex = gui.App()
    sys.exit(app.exec_())
