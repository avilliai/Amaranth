import re
import signal
import sys
import os
import psutil
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QStackedWidget, QHBoxLayout
from PySide6.QtCore import QProcess, QEvent, QTimer

class ScriptRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.processes = []  # 用于存储 QProcess 对象
        self.current_index = None  # 用于存储当前显示的页面索引
        self.output_buffers = ['', '', '']  # 缓存每个页面的输出内容
        self.output_limit = 90000  # 设置输出缓存的最大长度

        # 定期检查缓存长度，超出限制时清除
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_output_length)
        self.timer.start(5000)  # 每5秒检查一次

    def initUI(self):
        main_layout = QVBoxLayout()

        # 创建QStackedWidget对象
        self.stackedWidget = QStackedWidget()

        # 创建三个文本编辑器并添加到QStackedWidget
        self.textEdit1 = QTextEdit()
        self.set_text_edit_style(self.textEdit1)
        self.stackedWidget.addWidget(self.textEdit1)

        self.textEdit2 = QTextEdit()
        self.set_text_edit_style(self.textEdit2)
        self.stackedWidget.addWidget(self.textEdit2)

        self.textEdit3 = QTextEdit()
        self.set_text_edit_style(self.textEdit3)
        self.stackedWidget.addWidget(self.textEdit3)

        # 创建一个水平布局的按钮，并连接到启动脚本及切换视图的槽函数
        btn_layout = QHBoxLayout()
        self.button1 = QPushButton('启动overflow')
        self.button1.clicked.connect(lambda: self.handle_button_click(0, './overflow/start.bat'))
        btn_layout.addWidget(self.button1)

        self.button2 = QPushButton('启动Manyana')
        self.button2.clicked.connect(lambda: self.handle_button_click(1, './Manyana/main.py', python=True))
        btn_layout.addWidget(self.button2)

        self.button3 = QPushButton('启动bing_dalle3')
        self.button3.clicked.connect(lambda: self.handle_button_click(2, './Manyana/bing_image_creator.py', python=True))
        btn_layout.addWidget(self.button3)

        # 将按钮布局和QStackedWidget添加到主布局
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.stackedWidget)

        self.setLayout(main_layout)
        self.setWindowTitle('Script Runner')

    def set_text_edit_style(self, text_edit):
        text_edit.setStyleSheet("background-color: gray; color: black;")

    def handle_button_click(self, index, script_path, python=False):
        if self.current_index == index:
            # 如果当前显示的页面就是点击的按钮对应的页面，则重启脚本
            self.restart_script(index, script_path, python)
        else:
            # 否则，只切换页面
            self.stackedWidget.setCurrentIndex(index)
            self.current_index = index

    def restart_script(self, index, script_path, python):
        # 终止当前页面的脚本
        if len(self.processes) > index and self.processes[index].state() != QProcess.NotRunning:
            pid = self.processes[index].processId()
            self.kill_proc_tree(pid)
            self.kill_process(self.processes[index])

        # 重新启动脚本
        self.run_script(index, script_path, python)

    def run_script(self, index, script_path, python):
        text_edit = self.stackedWidget.widget(index)
        process = QProcess(self)
        if len(self.processes) > index:
            self.processes[index] = process  # 更新现有的 QProcess 对象
        else:
            self.processes.append(process)  # 添加新的 QProcess 对象
        process.errorOccurred.connect(lambda: self.handle_process_error(process))

        # 设置工作目录
        working_directory = os.path.dirname(script_path)
        process.setWorkingDirectory(working_directory)

        if python:
            process.setProgram("./environments/Python39/python.exe")
            process.setArguments([os.path.basename(script_path)])
        else:
            process.setProgram("cmd.exe")
            process.setArguments(['/c', os.path.basename(script_path)])

        process.readyReadStandardOutput.connect(lambda: self.read_output(process, text_edit, index))
        process.readyReadStandardError.connect(lambda: self.read_output(process, text_edit, index))
        process.start()

    def read_output(self, process, text_edit, index):
        output = process.readAllStandardOutput().data()
        error_output = process.readAllStandardError().data()

        decoded_output = self.try_decode_output(output)
        decoded_error_output = self.try_decode_output(error_output)

        text_edit.append(decoded_output)
        text_edit.append(decoded_error_output)

        # 将输出保存到缓存
        self.output_buffers[index] += decoded_output + decoded_error_output

    def check_output_length(self):
        # 检查每个页面的输出缓存长度，超过限制则清除
        for index, buffer in enumerate(self.output_buffers):
            if len(buffer) > self.output_limit:
                self.output_buffers[index] = ''
                self.stackedWidget.widget(index).clear()
                print(f"页面 {index} 的输出缓存已清除")

    def clear_logs(self):
        # 清除所有页面的输出
        for i in range(self.stackedWidget.count()):
            self.stackedWidget.widget(i).clear()
            self.output_buffers[i] = ''
        print("所有页面的输出缓存已清除")

    def clean_output(self, text):
        # 移除 ANSI 转义序列
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        text = ansi_escape.sub('', text)
        # 移除多余的空白行
        text = "\n".join([ll.rstrip() for ll in text.splitlines() if ll.strip()])
        return text

    def try_decode_output(self, data):
        for encoding in ['utf-8', 'gbk', 'cp850']:
            try:
                return self.clean_output(data.decode(encoding))
            except UnicodeDecodeError:
                continue
        return self.clean_output(data.decode('utf-8', errors='ignore'))  # 如果都不行，忽略错误

    def handle_process_error(self, process):
        error = process.error()
        if error == QProcess.FailedToStart:
            print("脚本启动失败，请检查脚本路径是否正确。")
        else:
            print(f"发生错误：{error}")

    def kill_process(self, process):
        try:
            process.terminate()
            os.kill(process.processId(), signal.CTRL_C_EVENT)
        except Exception as e:
            print(f"Error terminating process: {e}")
            try:
                os.kill(process.processId(), signal.CTRL_C_EVENT)
            except Exception as e:
                print(f"Error sending CTRL_C_EVENT: {e}")

    def kill_proc_tree(self, pid, including_parent=True):
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.kill()
            psutil.wait_procs(children, timeout=5)
            if including_parent:
                parent.kill()
                parent.wait(5)
        except psutil.NoSuchProcess:
            pass

    def cleanup(self):
        print("ScriptRunner cleanup")
        # 遍历并终止所有子进程
        for process in self.processes:
            if process.state() != QProcess.NotRunning:
                pid = process.processId()
                self.kill_proc_tree(pid)  # 使用 kill_proc_tree 方法来结束进程及其子进程
                self.kill_process(process)

    def closeEvent(self, event: QEvent):
        print("关闭")
        self.cleanup()
        event.accept()  # 接受关闭事件，正常关闭窗口

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScriptRunner()
    ex.show()
    sys.exit(app.exec())
