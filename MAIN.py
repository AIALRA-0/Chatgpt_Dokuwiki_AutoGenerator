from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

import GUI
import sys

# QT初始化
if __name__ == "__main__":
    main_window = QApplication(sys.argv)
    main_window.setWindowIcon(QIcon('DokuGPT.ico'))
    main_stats = GUI.Stats()
    sys.exit(main_window.exec_())


