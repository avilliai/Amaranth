import sys
import subprocess
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
        install_all_btn = QPushButton('一键安装Java+Python+miniGit')
        install_java_btn = QPushButton('安装Java')
        install_python_btn = QPushButton('安装Python')
        install_git_btn = QPushButton('安装miniGit')

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
        btn_layout.addWidget(QPushButton('更新仓库'))  # 更新仓库按钮

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

        # 创建一个定时器来定期检查环境变量和更新图表
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_charts)
        self.timer.start(5000)  # 每5秒检查一次

        # 第一次启动时立即检查环境变量和更新图表
        self.check_environment()
        self.update_charts()

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
        self.install_java()
        self.install_python()
        self.install_git()

    def install_java(self):
        print("安装Java的逻辑")

    def install_python(self):
        print("安装Python的逻辑")

    def install_git(self):
        print("安装miniGit的逻辑")

    def clone_repo(self):
        repo_url = self.repo_combo.currentText()
        try:
            subprocess.check_call(f"git clone {repo_url}", shell=True)
            print(f"成功克隆仓库：{repo_url}")
        except subprocess.CalledProcessError:
            print(f"克隆仓库失败：{repo_url}")

    def install_dependencies(self):
        repo_url = self.repo_combo.currentText().split('/')[-1].replace('.git', '')
        try:
            subprocess.check_call(f"cd {repo_url} && ./deploy.bat", shell=True)
            print(f"成功安装依赖：{repo_url}")
        except subprocess.CalledProcessError:
            print(f"安装依赖失败：{repo_url}")

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