import os
import sys
import threading
import webbrowser

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QFileDialog, QMessageBox

import DOKUWIKI_MAIN
import GPT
import UI


class Stats(QMainWindow, UI.Ui_MainWindow):
    # 创建信号类
    conn_dokuwiki_print = pyqtSignal(str)
    conn_search_resault_clear = pyqtSignal()
    conn_search_print = pyqtSignal(str)
    conn_log_print = pyqtSignal(str)
    conn_queue_print = pyqtSignal(list)

    def __init__(self):

        super(Stats, self).__init__()

        # 设置ui
        self.setupUi()

        # 链接按钮事件
        self.ui.SubmitButton.clicked.connect(self.handle_Submit_Button)
        self.ui.FormatSelect.currentIndexChanged.connect(self.handle_Format_Select)
        self.ui.ModelSelect.currentIndexChanged.connect(self.handle_Model_Select)
        self.ui.SearchButtom.clicked.connect(self.handle_search)
        self.ui.SearchClear.clicked.connect(self.clear_search)
        self.ui.SearchYes.clicked.connect(self.win_yes)
        self.ui.SearchNo.clicked.connect(self.win_no)

        # 链接自定义信号
        self.conn_dokuwiki_print.connect(self.DOKUWIKI_print)
        self.conn_search_resault_clear.connect(self.search_result_clear)
        self.conn_search_print.connect(self.Search_print)
        self.conn_log_print.connect(self.log_print)
        self.conn_queue_print.connect(self.queue_print)

        # 启动dokuwiki
        os.system("run_no_stop.cmd")  # 启用dokuwiki

        # 链接dokuwiki
        self.wiki = DOKUWIKI_MAIN.connect_dokuwiki()
        self.DOKUWIKI_print("DokuWiki 已启动...")
        self.DOKUWIKI_print("你的浏览器将会打开 http://localhost:8800\n")

        # openai 登录
        self.bot = GPT.openai_account_login_v3(self.ui)

        # 词语队列
        self.word_queue = list()

        # 格式文本
        self.format_text = ""
        self.format_count = 0
        self.requirements = DOKUWIKI_MAIN.get_requirements()

        # 重复判断
        self.win_choice = 0

        # temperature
        self.temperature = "0.0"

        # 单次处理标识
        self.handle_flag = False

        # 初始化模型
        self.model = "text-ada-001"

        # 初始化列表
        self.type_list_inital()
        self.model_list_inital()

        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1000)

        # 创建主线程
        loop = threading.Thread(target=self.loop_check)
        loop.daemon = True
        loop.start()

        self.log_print("\n初始化已完成\n")

        # 其他变量
        self.search_result = "xxxx"
        self.win_choice = 0
        self.parameters = ""

    # 线程相关函数
    def win_yes(self):
        try:
            if self.handle_flag:
                self.win_choice = QMessageBox.Yes
        except Exception as e:
            print(e)
        pass

    def win_no(self):
        try:
            if self.handle_flag:
                self.win_choice = QMessageBox.No
        except Exception as e:
            print(e)
        pass

    def update_label(self):
        try:
            self.queue_print(self.word_queue)
        except Exception as e:
            print(e)
        pass

    def search_result_clear(self):
        try:
            self.ui.SearchResault.clear()
        except Exception as e:
            print(e)
        pass

    # 主循环线程
    def loop_check(self):
        while True:
            if len(self.word_queue) and (self.handle_flag != True):  # 读
                self.handle_flag = True  # 写 发送信号
                # 获取输入以及格式化名称
                input_word = self.word_queue.pop(0)  # 获取弹出元素
                format_name = input_word[0] + " (" + input_word[1] + ")"
                # dokuwiki框打印输出
                self.conn_dokuwiki_print.emit("正在处理 => " + format_name + "\n模型: " + input_word[5])
                # 输出格式化
                parent_type = input_word[2]
                question = "列出{0}的中文名称 列出它的英文名称 给出它的完整定义".format(format_name) + input_word[6] + "\n此处{0}指的是{1}里的{2}\n".format(
                     format_name, parent_type,
                    format_name) + self.requirements + "输出字数不少于{0}个字\n".format(  # 读
                    input_word[4])
                if input_word[3] != "":
                    question += input_word[3] + "\n"  # 添加note
                question += input_word[7]  # 读
                # 查看是否已存在类似词条
                search_result = self.wiki.pages.search(input_word[0])  # 主函数操作 搜索
                if len(search_result) > 0:
                    result_list = "下面为已存在的关于{0}结果: \n(选择 Yes 则继续生成，选择 No 则取消生成)\n\n".format(input_word[0])
                    count = 0
                    for result in search_result:
                        result_list += result["id"] + "\n"
                        count += 1
                    self.conn_search_resault_clear.emit()  # 清除搜索框
                    self.conn_search_print.emit(result_list)
                    # 等待确认结果
                    while self.win_choice == 0:
                        temp = 0
                    if self.win_choice == QMessageBox.No:
                        self.conn_log_print.emit("结束创建\n")
                        self.conn_dokuwiki_print.emit("处理中断\n")
                        self.conn_search_resault_clear.emit()
                        self.win_choice = 0
                        self.handle_flag = False
                        continue
                    self.conn_dokuwiki_print.emit("处理继续")
                    self.conn_search_resault_clear.emit()
                respond = GPT.chatgptweb_send_message_v3(self.bot, question, float(self.temperature),
                                                         input_word[5])  # 获取 与gui无关
                respond = respond.replace("• ", "  * ")
                # 去掉废话
                index = respond.find('【')
                if index == -1:
                    index = 0
                respond = respond[index:]
                # 创建页面 与gui无关
                page_name = DOKUWIKI_MAIN.create_page(self.wiki, parent_type, input_word, respond)
                self.conn_dokuwiki_print.emit('页面"{0}"添加完成\n'.format(page_name))
                self.conn_log_print.emit("结束创建\n")
                # 打开页面
                target_url = "http://localhost:8800/doku.php?id=" + parent_type + ":" + input_word[0].replace(" ",
                                                                                                              "_").lower() + "_" + \
                             input_word[1].replace(" ", "_").lower()
                webbrowser.open(target_url, new=0, autoraise=True)
                self.conn_queue_print.emit(self.word_queue)
                # 还原设置
                self.win_choice = 0
                self.handle_flag = False

    def model_list_inital(self):
        try:
            with open("模型列表.txt", encoding='utf-8') as file:
                type_list = file.readlines()
            for filename in type_list:
                filename = filename.strip()
                self.ui.ModelSelect.addItems([filename])
            self.ui.ModelSelect.setCurrentIndex(0)
            self.model = self.ui.ModelSelect.currentText()
            self.log_print("模型列表加载完成")
            self.log_print("模型已更新为: " + self.model)
        except Exception as e:
            print(e)
        pass

    def type_list_inital(self):
        try:
            with open("格式列表.txt", encoding='utf-8') as file:
                type_list = file.readlines()
            index = 1
            for filename in type_list:
                filename = filename.strip()
                self.ui.FormatSelect.removeItem(index)
                self.ui.FormatSelect.addItems([filename, "+添加格式"])
                self.ui.FormatSelect.setCurrentIndex(index)
                index += 1
            self.ui.FormatSelect.setCurrentIndex(0)
            self.log_print("格式列表加载完成")
            self.log_print("格式已清空\n")
        except Exception as e:
            print(e)
        pass

    # 操作处理函数
    def handle_search(self):  # 搜索框函数
        try:
            self.ui.SearchResault.clear()
            word = self.ui.SearchBox.text().strip()
            search_result = self.wiki.pages.search(word)
            for result in search_result:
                self.Search_print(result["id"])
        except Exception as e:
            print(e)
        pass

    def clear_search(self):  # 搜索框清除函数
        try:
            self.ui.SearchResault.clear()
            self.ui.SearchBox.clear()
        except Exception as e:
            print(e)
        pass

    def log_print(self, _text):  # 日志框打印函数
        try:
            self.ui.LogBox.append(_text)
            self.ui.LogBox.ensureCursorVisible()
        except Exception as e:
            print(e)
        pass

    def Search_print(self, _text):  # 搜索框打印函数
        try:
            self.ui.SearchResault.append(_text)
            self.ui.SearchResault.ensureCursorVisible()
        except Exception as e:
            print(e)
        pass

    def DOKUWIKI_print(self, _text):  # dokuwiki框打印函数
        try:
            self.ui.DOKUWIKIBox.append(_text)
            self.ui.DOKUWIKIBox.ensureCursorVisible()
        except Exception as e:
            print(e)
        pass

    def queue_box_add(self, _word):  # 词语队列框添加函数
        try:
            self.ui.QueueBox.appendPlainText(_word)
            self.ui.QueueBox.ensureCursorVisible()
        except Exception as e:
            print(e)
        pass

    def queue_print(self, _queue):  # 词语队列框打印函数
        try:
            self.ui.QueueBox.clear()
            for data in _queue:
                output_form = data[2] + ": " + data[0] + " (" + data[1] + ")"  # 词条展示格式化
                self.queue_box_add(output_form)
        except Exception as e:
            print(e)
        pass

    def handle_Model_Select(self):  # 模型选择处理函数
        try:
            select = self.ui.ModelSelect.currentText()
            self.model = select
            self.log_print("模型已更新为: " + self.model)
        except Exception as e:
            print(e)
        pass

    def handle_Format_Select(self):  # 格式选择处理函数
        try:
            select = self.ui.FormatSelect.currentText()
            if self.format_count > 0:
                self.format_count -= 1
                return
            elif select == "(空)":
                self.parameters = ""
                self.format_text = ""
                self.log_print("格式已清空")
            elif select == "+添加格式":
                self.format_count = 2
                filePath, _ = QFileDialog.getOpenFileName(
                    self.ui,  # 父窗口对象
                    "选择你要添加的格式文件",  # 标题
                    r"格式",  # 起始目录
                    "文本类型 (*.txt)"  # 选择类型过滤项，过滤内容在括号中
                )
                if filePath == "":
                    self.format_text = ""
                    self.format_count = 0
                    self.ui.FormatSelect.setCurrentIndex(0)
                    return
                filename = filePath.split("/")[-1]
                index = self.ui.FormatSelect.currentIndex()
                self.ui.FormatSelect.removeItem(index)
                self.ui.FormatSelect.addItems([filename, "+添加格式"])
                self.ui.FormatSelect.setCurrentIndex(index)
                with open("格式/" + filename, 'r', encoding='utf-8') as format_file:
                    self.parameters = format_file.readline()
                    self.format_text = format_file.read()
                self.log_print("新格式已添加: " + filename)
            else:
                with open("格式/" + select, 'r', encoding='utf-8') as format_file:
                    self.parameters = format_file.readline()
                    self.format_text = format_file.read()
                self.log_print("格式已更新为: " + select)
        except Exception as e:
            print(e)
        pass

    def handle_Submit_Button(self):  # 提交按钮处理
        try:
            word = self.ui.InputBox.text().strip()  # 接收文本框输入
            word_type = self.ui.TypeBox.text().strip()  # 接收类型输入
            note = self.ui.NoteBox.text().strip()  # 接受附加文本
            model = self.model.strip()
            self.temperature = self.ui.TemperatureBox.text().strip()  # 接受temperature值
            if self.temperature == "":
                self.temperature = "0.0"
            elif float(self.temperature) < 0:
                self.temperature = "0.0"
            elif float(self.temperature) > 0:
                self.temperature = "1.0"
            word_limit = self.ui.WordLimitBox.text().strip()
            if word_limit == "":
                word_limit = 100
            word_limit = int(word_limit)
            if word_limit < 10:
                word_limit = 10

            if word == '' or word_type == '':  # 无输入
                self.log_print("输入缺失，请重新输入")
                return

            word = list(word.replace('（', '(').replace('）', ')').split('('))  # 替换中文括号
            if len(word) != 2:  # 检查格式
                self.log_print("格式不一致，请重新输入")
                return
            else:  # 格式正确
                word[0] = word[0].strip(" ").strip("\t").upper()
                word[1] = word[1].strip(')').strip(" ").title()  # 格式化英文输入
                word.append(word_type)
                word.append(note)
                word.append(str(word_limit))
                word.append(model)
                word.append(self.parameters.strip())
                word.append(self.format_text)
                output_form = word_type + ": " + word[0] + " (" + word[1] + ")"  # 词条展示格式化
                self.log_print("\n已接收输入: " + output_form)
                self.word_queue.append(word)  # 将输入传入队列，等待处理
                self.queue_print(self.word_queue)  # 更新等待列表
        except Exception as e:
            print(e)
        pass


if __name__ == "__main__":
    main_window = QApplication(sys.argv)
    main_window.setWindowIcon(QIcon('DokuGPT.ico'))
    main_stats = Stats()
    sys.exit(main_window.exec_())
