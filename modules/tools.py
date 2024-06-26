import os
import sys
import subprocess
import threading

import psutil
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QGridLayout, QComboBox
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCharts import QChart, QChartView, QPieSeries

class EnvironmentChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 创建顶部布局
        top_layout = QHBoxLayout()

        # 创建环境变量检查组
        env_group = QGroupBox("环境变量检查")
        env_layout = QVBoxLayout()

        self.java_status_label = QLabel("Java: Checking...")
        self.python_status_label = QLabel("Python: Checking...")
        self.git_status_label = QLabel("Git: Checking...")

        # 设置标签颜色
        self.set_label_color(self.java_status_label, QColor('red'))
        self.set_label_color(self.python_status_label, QColor('red'))
        self.set_label_color(self.git_status_label, QColor('red'))

        # 添加标签到布局
        env_layout.addWidget(self.java_status_label)
        env_layout.addWidget(self.python_status_label)
        env_layout.addWidget(self.git_status_label)

        env_group.setLayout(env_layout)

        # 创建图表组
        chart_group = QGroupBox("系统监测")
        chart_layout = QHBoxLayout()

        # 创建内存占用饼状图
        self.memory_chart_view = QChartView()
        self.memory_chart_view.setFixedSize(200, 200)
        chart_layout.addWidget(self.memory_chart_view)
        self.update_memory_chart()

        # 创建CPU利用率饼状图
        self.cpu_chart_view = QChartView()
        self.cpu_chart_view.setFixedSize(200, 200)
        chart_layout.addWidget(self.cpu_chart_view)
        self.update_cpu_chart()

        # 创建IO统计饼状图
        self.io_chart_view = QChartView()
        self.io_chart_view.setFixedSize(200, 200)
        chart_layout.addWidget(self.io_chart_view)
        self.update_io_chart()

        chart_group.setLayout(chart_layout)

        # 将环境变量检查组和图表组添加到顶部布局
        top_layout.addWidget(env_group)
        top_layout.addWidget(chart_group)

        # 创建按钮布局
        btn_layout = QVBoxLayout()

        # 创建"一键安装"按钮及其子按钮
        install_all_btn = QPushButton('一键安装Java+Python+minGit')
        install_java_btn = QPushButton('安装Java')
        install_python_btn = QPushButton('安装Python')
        install_git_btn = QPushButton('安装minGit')

        # 将子按钮添加到一个嵌套布局中
        nested_install_layout = QVBoxLayout()
        nested_install_layout.addWidget(install_java_btn)
        nested_install_layout.addWidget(install_python_btn)
        nested_install_layout.addWidget(install_git_btn)

        # 将"一键安装"按钮和嵌套布局添加到一个组框中
        install_group = QGroupBox()
        install_layout = QVBoxLayout()
        install_layout.addWidget(install_all_btn)
        install_layout.addLayout(nested_install_layout)
        install_group.setLayout(install_layout)

        # 创建克隆仓库部分
        clone_layout = QHBoxLayout()
        clone_repo_btn = QPushButton('克隆仓库')
        pull_repo_btn=QPushButton('更新仓库')
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

        # 创建自动安装依赖按钮
        install_deps_btn = QPushButton('自动安装依赖')

        # 将按钮添加到布局
        btn_layout.addWidget(install_group)
        btn_layout.addLayout(clone_layout)
        btn_layout.addWidget(install_deps_btn)
        btn_layout.addWidget(pull_repo_btn)  # 更新仓库按钮

        # 将顶部布局和按钮布局添加到主布局
        main_layout.addLayout(top_layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Environment Checker')

        # 连接按钮点击事件
        install_all_btn.clicked.connect(self.install_all)
        install_java_btn.clicked.connect(self.install_java)
        install_python_btn.clicked.connect(self.install_python)
        install_git_btn.clicked.connect(self.install_git)
        clone_repo_btn.clicked.connect(self.clone_repo)
        install_deps_btn.clicked.connect(self.install_dependencies)
        pull_repo_btn.clicked.connect(self.pull_repo)

        # 创建一个定时器来定期检查环境变量和更新图表
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_charts)
        self.timer.start(5000)  # 每5秒检查一次

        # 第一次启动时立即检查环境变量和更新图表
        self.check_environment()
        self.update_charts()
    def pull_repo(self):
        pull_thread = threading.Thread(target=self.pull_repo1())
        pull_thread.start()
    def pull_repo1(self):
        SCRIPT_DIR = os.getcwd()
        Manyana_DIR = os.path.join(SCRIPT_DIR, "Manyana")
        setup_bat = os.path.join(Manyana_DIR, "更新脚本.bat")

        os.chdir(Manyana_DIR)  # 改变当前工作目录到Manyana所在目录

        command = f'start cmd /k "{setup_bat}"'  # 启动一个新的命令提示符窗口执行setup.bat脚本

        subprocess.Popen(command, shell=True)

        # 回到原来的工作目录
        os.chdir(SCRIPT_DIR)

        print(f"Successfully ran setup.bat for: Manyana")
    def set_label_color(self, label, color):
        palette = label.palette()
        palette.setColor(QPalette.WindowText, color)
        label.setPalette(palette)

    def check_environment(self):
        self.check_java()
        self.check_python()
        self.check_git()

    def check_java(self):
        version = self.get_version("java -version")
        if version:
            self.java_status_label.setText(f"Java: Installed ({version})")
            self.set_label_color(self.java_status_label, QColor('green'))
        else:
            self.java_status_label.setText("Java: Not Installed")
            self.set_label_color(self.java_status_label, QColor('red'))

    def check_python(self):
        version = self.get_version("python --version")
        if version:
            self.python_status_label.setText(f"Python: Installed ({version})")
            self.set_label_color(self.python_status_label, QColor('green'))
        else:
            self.python_status_label.setText("Python: Not Installed")
            self.set_label_color(self.python_status_label, QColor('red'))

    def check_git(self):
        version = self.get_version("git --version")
        if version:
            self.git_status_label.setText(f"Git: Installed ({version})")
            self.set_label_color(self.git_status_label, QColor('green'))
        else:
            self.git_status_label.setText("Git: Not Installed")
            self.set_label_color(self.git_status_label, QColor('red'))

    def get_version(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            version = output.decode().split('\n')[0]
            return version
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            return None

    def install_all(self):
        java_thread = threading.Thread(target=self.install_java)
        python_thread = threading.Thread(target=self.install_python)
        git_thread = threading.Thread(target=self.install_git)

        # 启动线程
        java_thread.start()
        python_thread.start()
        git_thread.start()

    def install_java(self):
        SCRIPT_DIR = os.getcwd()
        JAVA_ZIP_PATH = os.path.join(SCRIPT_DIR, "environments","openjdk-21.0.2_windows-x64_bin.zip")
        JAVA_INSTALL_DIR = os.path.join(SCRIPT_DIR, "environments","Java")

        # 如果Java安装目录不存在，则创建该目录
        if not os.path.exists(JAVA_INSTALL_DIR):
            os.mkdir(JAVA_INSTALL_DIR)

        # 构建PowerShell脚本内容
        ps_script_content = f"""
        Write-Output "Unpacking Java..."
        Expand-Archive -LiteralPath '{JAVA_ZIP_PATH}' -DestinationPath '{JAVA_INSTALL_DIR}' -Force
        """

        # 将PowerShell脚本内容写入文件
        ps_script_path = os.path.join(SCRIPT_DIR, "install_java.ps1")
        with open(ps_script_path, 'w') as ps_script_file:
            ps_script_file.write(ps_script_content)

        # 执行PowerShell脚本并保持窗口打开
        subprocess.run(["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps_script_path])
        os.remove(ps_script_path)
        # 删除下载的文件
        #os.remove(JAVA_ZIP_PATH)

    def install_python(self):
        SCRIPT_DIR = os.getcwd()
        PYTHON_INSTALL_DIR = os.path.join(SCRIPT_DIR, "environments", "Python39")
        Python_zip = os.path.join(SCRIPT_DIR, "environments", "python-3.9.0-embed-amd64.zip")

        # 如果安装目录不存在，则创建该目录
        if not os.path.exists(PYTHON_INSTALL_DIR):
            os.mkdir(PYTHON_INSTALL_DIR)

        # 构建PowerShell脚本内容
        ps_script_content = f"""
        Write-Output "Unpacking Python..."
        Expand-Archive -LiteralPath '{Python_zip}' -DestinationPath '{PYTHON_INSTALL_DIR}' -Force

        # 复制python39._pth文件到Python安装目录
        Copy-Item '{os.path.join(SCRIPT_DIR, "environments", "python39._pth")}' '{PYTHON_INSTALL_DIR}'

        Write-Output "Installing pip..."
        & '{PYTHON_INSTALL_DIR}\\python.exe' '{os.path.join(SCRIPT_DIR, "environments", "get-pip.py")}'

        # 更新系统环境变量操作需要在PowerShell脚本外部执行
        """

        # 将PowerShell脚本内容写入临时文件
        ps_script_path = os.path.join(SCRIPT_DIR, "install_python.ps1")
        with open(ps_script_path, "w") as ps_script_file:
            ps_script_file.write(ps_script_content)
        subprocess.run(["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps_script_path])
        # 在cmd中执行PowerShell脚本
        #subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], shell=True)

        # 删除临时PowerShell脚本文件
        os.remove(ps_script_path)

    def install_git(self):
        SCRIPT_DIR = os.getcwd()
        # 定义MinGit下载URL和本地路径
        MINGIT_ZIP_PATH = os.path.join(SCRIPT_DIR, "environments", "MinGit-2.24.1.2-64-bit.zip")
        MINGIT_INSTALL_DIR = os.path.join(SCRIPT_DIR, "environments", "MinGit")

        # 构建PowerShell脚本内容
        ps_script_content = f"""
        Write-Output "Unpacking MinGit..."
        Expand-Archive -LiteralPath '{MINGIT_ZIP_PATH}' -DestinationPath '{MINGIT_INSTALL_DIR}' -Force

        Remove-Item -Path '{MINGIT_ZIP_PATH}'
        """

        # 将PowerShell脚本内容写入临时文件
        ps_script_path = os.path.join(SCRIPT_DIR, "install_git.ps1")
        with open(ps_script_path, "w") as ps_script_file:
            ps_script_file.write(ps_script_content)
        subprocess.run(["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps_script_path])
        # 在cmd中执行PowerShell脚本
        #subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], shell=True)

        # 删除临时PowerShell脚本文件
        os.remove(ps_script_path)

    def clone_repo(self):
        clone_thread = threading.Thread(target=self.clone())
        clone_thread.start()

    def clone(self):
        repo_url = self.repo_combo.currentText()
        script_dir = os.getcwd()  # 获取脚本所在目录的绝对路径
        git_path = os.path.join(script_dir, "environments","MinGit", "cmd", "git.exe")  # 构建git.exe的绝对路径

        # 使用双引号包裹整个命令，并启动一个新的命令提示符窗口执行命令
        command = f'start cmd /k "{git_path}" clone --depth 1 {repo_url}'

        # 启动一个新的命令提示符窗口执行命令
        subprocess.Popen(command, shell=True)



        # 使用引号和&运算符执行命令

    def install_dependencies(self):
        de_thread = threading.Thread(target=self.install_dependencies1())
        de_thread.start()

    def install_dependencies1(self):
        SCRIPT_DIR = os.getcwd()
        Manyana_DIR = os.path.join(SCRIPT_DIR, "Manyana")
        pip_path = os.path.join(SCRIPT_DIR, "environments", "Python39", "Scripts", "pip.exe")
        PYTHON_dir=os.path.join(SCRIPT_DIR,"environments", "Python39", "python.exe")
        venv_activate = os.path.join(SCRIPT_DIR, "Manyana","venv", "Scripts", "activate.bat")

        # 创建PowerShell脚本内容
        ps_script_content = f"""
        cd '{Manyana_DIR}'

        # 设置全局镜像源
        & '{pip_path}' config set global.index-url https://mirrors.aliyun.com/pypi/simple/

        # 升级 pip
        & '{pip_path}' install --user --upgrade pip

        # 安装 virtualenv
        & '{pip_path}' install virtualenv

        # 创建虚拟环境
        & '{PYTHON_dir}' -m virtualenv -p '{PYTHON_dir}' venv

        # 激活虚拟环境
        & '{venv_activate}'

        # 设置虚拟环境内的镜像源
        & '{pip_path}' config set global.index-url https://mirrors.aliyun.com/pypi/simple/

        # 回到上一级目录

        # 使用指定的 pip 安装依赖
        & venv\\Scripts\\pip.exe install -r requirements.txt

        cd '{SCRIPT_DIR}'
        """

        # 将PowerShell脚本内容写入文件
        ps_script_path = os.path.join(SCRIPT_DIR, "install_dependencies.ps1")
        with open(ps_script_path, 'w') as ps_script_file:
            ps_script_file.write(ps_script_content)

        # 执行PowerShell脚本并保持窗口打开
        subprocess.run(["powershell", "-NoExit", "-File", ps_script_path])

        # 清理脚本文件
        os.remove(ps_script_path)  # 注意：如果您希望在执行后手动检查脚本，可以暂时注释掉这行代码

        # 回到上级目录
        os.chdir(SCRIPT_DIR)

        print(f"Successfully installed dependencies for: Manyana")
    def update_charts(self):
        self.update_memory_chart()
        self.update_cpu_chart()
        self.update_io_chart()

    def update_memory_chart(self):
        memory_info = psutil.virtual_memory()
        series = QPieSeries()
        series.append("Used", memory_info.used)
        series.append("Free", memory_info.free)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Memory Usage")
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundRoundness(0)
        self.memory_chart_view.setChart(chart)

    def update_cpu_chart(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        series = QPieSeries()
        series.append("Used", cpu_usage)
        series.append("Free", 100 - cpu_usage)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("CPU Usage")
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundRoundness(0)
        self.cpu_chart_view.setChart(chart)
    def update_io_chart(self):
        io_counters = psutil.disk_io_counters()
        series = QPieSeries()
        series.append("Read", io_counters.read_bytes)
        series.append("Write", io_counters.write_bytes)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Disk IO")
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundRoundness(0)
        self.io_chart_view.setChart(chart)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EnvironmentChecker()
    ex.show()