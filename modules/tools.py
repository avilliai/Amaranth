import asyncio
import os
import sys
import subprocess
import threading

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, \
    QGridLayout, QComboBox, QTextEdit, QScrollArea, QInputDialog
from PySide6.QtCore import QTimer, QSize, Qt, QEvent
from PySide6.QtGui import QColor, QPalette, QTextCursor

from modules.aiRep import modelRep


class EnvironmentChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.prompt=None
    def initUI(self):
        main_layout = QVBoxLayout()

        # 创建聊天框和滚动条
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)  # 设置为只读模式
        self.chat_box.setPlainText("Welcome to Environment Checker Chat!\n")
        #self.chat_box.setPlainText("Welcome to Environment Checker Chat!\n")
        self.chat_box.setStyleSheet("QTextEdit { background-image: url('./images/chatbox.jpg'); }")
        #self.chat_box.setObjectName("chatBox")
        #self.chat_box.setStyleSheet("#chatBox { background-image: url('images/chatbox.jpg'); }")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.chat_box)

        # 创建输入框布局
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(40)  # 设置输入框的最大高度
        send_button = QPushButton('发送')

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_button)

        # 创建按钮布局
        btn_layout = QVBoxLayout()

        # 创建克隆仓库部分
        clone_layout = QHBoxLayout()
        clone_repo_btn = QPushButton('克隆仓库')
        pull_repo_btn = QPushButton('更新仓库(更新后需要重启启动器)')
        self.repo_combo = QComboBox()
        repo_sources = [
            "https://github.com/avilliai/Manyana.git",
            "https://mirror.ghproxy.com/https://github.com/avilliai/Manyana",
            "https://github.moeyy.xyz/https://github.com/avilliai/Manyana",
            "https://www.gitlink.org.cn/lux-QAQ/Manyana"
        ]
        self.repo_combo.addItems(repo_sources)
        self.repo_combo.setCurrentIndex(3)  # 设置第四个源为默认选择项

        clone_layout.addWidget(clone_repo_btn)
        clone_layout.addWidget(self.repo_combo)

        # 将聊天框和滚动条添加到主布局
        #main_layout.addWidget(scroll_area)

        # 将输入框布局添加到主布局
        #main_layout.addLayout(input_layout)

        # 将按钮添加到布局
        btn_layout.addLayout(clone_layout)
        btn_layout.addWidget(pull_repo_btn)  # 更新仓库按钮

        # 将按钮布局添加到主布局
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Environment Checker')

        # 连接按钮点击事件
        clone_repo_btn.clicked.connect(self.clone_repo)
        pull_repo_btn.clicked.connect(self.pull_repo)
        send_button.clicked.connect(self.send_message)  # 连接发送按钮的点击事件
        self.input_box.installEventFilter(self)  # 安装事件过滤器，以便捕获回车键事件

    def reply(self, text):
        self.chat_box.setTextColor(Qt.black)

        self.chat_box.append(text)
        r=asyncio.run(self.replyMe(text))
        self.chat_box.append(f"\nbot: {r}")
    async def replyMe(self,text):
        if self.prompt==None:
            self.prompt=[{"role": "user", "content": text}]
        else:
            self.prompt.append({"role": "user", "content": text})
        rep=await modelRep(self.prompt)
        self.prompt.append(rep)
        print(self.prompt)
        return rep["content"]
    def send_message(self):
        message = self.input_box.toPlainText().strip()
        if message:
            self.reply(f"用户输入: {message}")
            self.input_box.clear()

    def eventFilter(self, obj, event):
        if obj is self.input_box and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def pull_repo(self):
        pull_thread = threading.Thread(target=self.pull_repo1)
        pull_thread.start()

    def pull_repo1(self):
        SCRIPT_DIR = os.getcwd()
        Manyana_DIR = os.path.join(SCRIPT_DIR, "Manyana")
        PYTHON_EXE = os.path.join(SCRIPT_DIR, "environments", "Python39", "python.exe")
        setup_script = os.path.join(Manyana_DIR, "setUp.py")

        os.chdir(Manyana_DIR)  # 改变当前工作目录到Manyana所在目录

        command = f'start cmd /k "{PYTHON_EXE} {setup_script}"'  # 启动一个新的命令提示符窗口执行Python脚本

        subprocess.Popen(command, shell=True)

        # 回到原来的工作目录
        os.chdir(SCRIPT_DIR)

        self.reply("Successfully ran setUp.py for: Manyana")

    def set_label_color(self, label, color):
        palette = label.palette()
        palette.setColor(QPalette.WindowText, color)
        label.setPalette(palette)

    def get_version(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            version = output.decode().split('\n')[0]
            return version
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            return None

    def clone_repo(self):
        clone_thread = threading.Thread(target=self.clone)
        clone_thread.start()

    def clone(self):
        repo_url = self.repo_combo.currentText()
        script_dir = os.getcwd()  # 获取脚本所在目录的绝对路径
        git_path = os.path.join(script_dir, "environments", "MinGit", "cmd", "git.exe")  # 构建git.exe的绝对路径
        if os.path.exists(git_path):
            pass
        else:
            git_path = "git"
        # 使用双引号包裹整个命令，并启动一个新的命令提示符窗口执行命令
        command = f'start cmd /k "{git_path}" clone --depth 1 {repo_url}'

        # 启动一个新的命令提示符窗口执行命令
        subprocess.Popen(command, shell=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EnvironmentChecker()
    ex.show()
    sys.exit(app.exec())
