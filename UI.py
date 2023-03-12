from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


class Ui_MainWindow(object):
    def __init__(self):
        self.ui = None

    def setupUi(self):
        try:
            # 从文件中加载UI定义
            qfile_stats = QFile('ui/主界面.ui')
            qfile_stats.open(QFile.ReadOnly)
            qfile_stats.close()

            # 导入ui定义，创建对象
            self.ui = QUiLoader().load('ui/主界面.ui')
            self.ui.show()
        except Exception as e:
            print(e)
        pass

