import os
import sys

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from modules.HomePage import jsonEditor

from modules.YamlEditor import YamlMainWindow
from modules.cmdRunner import ScriptRunner
from modules.tools import EnvironmentChecker

os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "PyDracula - Modern GUI"
        description = "Manyana"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)
        try:
            #yaml页面
            self.yamlEditorPage1 = YamlMainWindow()
            self.ui.stackedWidget.addWidget(self.yamlEditorPage1)
            self.yamlEditorPage1.setStyleSheet(self.styleSheet())
        except:
            self.yamlEditorPage1=widgets.home
        self.cmdRunner=ScriptRunner()
        self.ui.stackedWidget.addWidget(self.cmdRunner)
        #工具页面
        self.setUpTools=EnvironmentChecker()
        self.ui.stackedWidget.addWidget(self.setUpTools)
        # 工具页面
        try:
            self.HomeP= jsonEditor()
            self.ui.stackedWidget.addWidget(self.HomeP)
        except:
            CustomDialog.showMessage("未搭建Manyana，请在拉取源码并完成搭建后重启本启动器.")
            self.HomeP=self.setUpTools
        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()


        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////

        widgets.stackedWidget.setCurrentWidget(self.HomeP)

        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(self.HomeP)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            index = self.ui.stackedWidget.indexOf(self.cmdRunner)
            # Set the current widget of stackedWidget to YamlEditorPage
            self.ui.stackedWidget.setCurrentIndex(index)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            index = self.ui.stackedWidget.indexOf(self.yamlEditorPage1)
            # Set the current widget of stackedWidget to YamlEditorPage
            self.ui.stackedWidget.setCurrentIndex(index)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "btn_save":
            index = self.ui.stackedWidget.indexOf(self.setUpTools)
            # Set the current widget of stackedWidget to YamlEditorPage
            self.ui.stackedWidget.setCurrentIndex(index)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
    def closeEvent(self, event: QEvent):
        print("Main Window 关闭")
        # 手动调用子页面的清理逻辑
        self.cmdRunner.cleanup()
        event.accept()  # 接受关闭事件，正常关闭窗口
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class CustomDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("Custom Dialog")
        layout = QVBoxLayout()
        label = QLabel(message)
        layout.addWidget(label)
        okButton = QPushButton("OK")
        okButton.clicked.connect(self.accept)  # Close the dialog when OK button is clicked
        layout.addWidget(okButton)
        self.setLayout(layout)

    @staticmethod
    def showMessage(message):
        dialog = CustomDialog(message)
        dialog.exec()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec_())

