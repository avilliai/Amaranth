import sys

from PySide6.QtGui import Qt
from ruamel.yaml import YAML
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, \
    QScrollArea, QHBoxLayout, QGroupBox, QSizePolicy, QCheckBox, QTabWidget, QComboBox

from ruamel.yaml import YAML
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QScrollArea


class configEditor(QWidget):
    def __init__(self,yaml_file):
        super().__init__()
        self.yaml_file = yaml_file
        self.yaml = YAML()
        self.type_dict = {}
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.scrollContent = QWidget(scroll)
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.yaml_data = self.load_yaml_with_comments(self.yaml_file)
        self.edit_fields = {}
        self.max_comment_length = self.get_max_comment_length(self.yaml_data)  # 新增行
        self.create_widgets(self.yaml_data, self.scrollLayout)
        scroll.setWidget(self.scrollContent)
        self.layout.addWidget(scroll)
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(save_button)
        self.setLayout(self.layout)
        self.setWindowTitle('YAML Editor')

    def get_max_comment_length(self, data, parent_key=""):
        max_length = 0
        for key, value in data.items():
            comment = self.get_comment(data, key)
            if comment:
                max_length = max(max_length, len(comment))
            if isinstance(value, dict):
                max_length = max(max_length, self.get_max_comment_length(value, parent_key + key + "."))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        max_length = max(max_length, self.get_max_comment_length(item, parent_key + key + "."))
        return max_length
    def load_yaml_with_comments(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = self.yaml.load(file)
        self.create_type_dict(data)
        return data

    def create_type_dict(self, data, parent_key=""):
        for key, value in data.items():
            full_key = parent_key + key
            self.type_dict[full_key] = type(value)  # 记录当前键的值的类型
            if isinstance(value, dict):
                self.create_type_dict(value, full_key + ".")
            elif isinstance(value, list):
                if value:  # 确保列表不为空
                    for i, item in enumerate(value):
                        item_key = f"{full_key}[{i}]"
                        self.type_dict[item_key] = type(item)  # 为列表中每个元素添加类型信息
                        if isinstance(item, dict):
                            self.create_type_dict(item, item_key + ".")
                else:
                    # 如果列表为空，记录为NoneType
                    self.type_dict[full_key] = type(None)

    def save_changes(self):
        def update_data(data, parent_key=""):
            #print(data)
            for key in data.keys():
                full_key = parent_key + key
                if isinstance(data[key], dict):
                    update_data(data[key], full_key + ".")
                elif isinstance(data[key], list):
                    # 为列表类型的数据收集所有元素的值
                    updated_list = []
                    for i in range(len(data[key])):
                        item_key = f"{full_key}[{i}]"
                        print(item_key)
                        edit_widget = self.edit_fields.get(item_key)
                        if edit_widget:
                            original_value = edit_widget.text()
                            print(self.type_dict)
                            updated_value = self.convert_to_original_type(original_value, str)
                            updated_list.append(updated_value)
                        else:
                            updated_value = self.convert_to_original_type("", str)
                            updated_list.append(updated_value)
                    # 使用新的列表更新原始数据
                    data[key] = updated_list
                else:
                    # 对于非列表类型的数据
                    edit_widget = self.edit_fields.get(full_key)
                    if edit_widget:
                        if isinstance(edit_widget, QCheckBox):
                            original_value = edit_widget.isChecked()
                        else:
                            original_value = edit_widget.text()
                        data[key] = self.convert_to_original_type(original_value, self.type_dict[full_key])
        #print(self.yaml_data)
        update_data(self.yaml_data)
        with open(self.yaml_file, 'w', encoding='utf-8') as file:
            self.yaml.dump(self.yaml_data, file)
        print("Changes saved.")

    def convert_to_original_type(self, value, expected_type):
        # 根据 expected_type 转换 value 的类型
        if expected_type == int:
            return int(value)
        elif expected_type == float:
            return float(value)
        elif expected_type == bool:
            return value if isinstance(value, bool) else value.lower() in ('true', 'yes', '1')
        elif expected_type == str:
            return value
        elif expected_type == list:
            # 特殊处理，因为列表的具体元素类型已在 save_changes 中处理
            return value
        return value  # 默认返回原始字符串

    def create_widgets(self, data, layout, parent_key="", level=0):
        max_label_width = 150
        max_edit_width = 300
        # 计算注释标签的最大宽度
        max_comment_width = self.max_comment_length * 6

        for key, value in data.items():
            comment = self.get_comment(data, key)  # 获取当前键的注释

            if isinstance(value, dict):
                groupBox = QGroupBox(f"{key}: {comment}" if comment else key)
                groupBoxLayout = QVBoxLayout()
                self.create_widgets(value, groupBoxLayout, parent_key + key + ".", level + 1)
                groupBox.setLayout(groupBoxLayout)
                layout.addWidget(groupBox)
            elif isinstance(value, list):
                listLabel = QLabel(f"{key}: {comment}" if comment else key)
                listLabel.setMaximumWidth(max_label_width)
                layout.addWidget(listLabel)
                listLayout = QVBoxLayout()  # 创建一个新的垂直布局来容纳列表元素
                for i, item in enumerate(value):
                    self.create_list_item_widget(f"{parent_key}{key}", item, listLayout, i)

                # 在create_widgets方法中，当您为列表类型的数据创建添加按钮时
                addButton = QPushButton("Add Item")
                # 使用lambda的默认参数立即绑定parent_key的当前值
                addButton.clicked.connect(lambda checked=False, pk=parent_key+key: self.add_list_item(pk, len(value), listLayout))
                listLayout.addWidget(addButton)
                layout.addLayout(listLayout)
            else:
                hLayout = QHBoxLayout()
                label = QLabel(f"{key}:")
                label.setMaximumWidth(max_label_width)
                label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

                if isinstance(value, bool):
                    edit = QCheckBox()
                    edit.setChecked(value)
                else:
                    edit = QLineEdit(str(value))
                    edit.setMaximumWidth(max_edit_width)
                    edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

                commentLabel = QLabel(f"  # {comment}" if comment else "")
                commentLabel.setStyleSheet("color: gray;")
                commentLabel.setWordWrap(True)
                commentLabel.setMinimumWidth(max_comment_width)  # 设置最小宽度以对齐注释

                hLayout.addWidget(label)
                hLayout.addWidget(edit)
                hLayout.addWidget(commentLabel)
                hLayout.setContentsMargins(level * 20, 0, 0, 0)
                layout.addLayout(hLayout)
                self.edit_fields[parent_key + key] = edit

    def get_comment(self, data, key):
        # 从ruamel.yaml的CommentedMap或CommentedSeq获取指定键的注释
        comment = None
        if key in data.ca.items:
            comment_items = data.ca.items[key]
            if comment_items and comment_items[2]:
                comment = comment_items[2].value  # 获取行尾注释
                if comment:
                    comment = comment.strip("# ").strip()  # 清除注释符号和多余的空格
        return comment

    def add_list_item(self, parent_key, list_index, layout):
        # 构建新元素的键路径
        new_item_key = f"{parent_key}.{list_index}"

        # 这里我们假设新元素是字符串类型的，因此初始化为空字符串
        item_value = ""
        # 将 parent_key 字符串转换为路径列表
        key_path = parent_key.split('.')
        # 使用路径列表逐级访问 yaml_data 中的嵌套结构
        target = self.yaml_data
        for key in key_path:
            if key.isdigit():  # 如果键是数字，表示访问的是列表的索引
                key = int(key)  # 将键转换为整数
            target = target[key]
        # 在找到的列表中添加新元素
        target.append(item_value)
        # 更新type_dict以包含新元素的类型信息
        print(new_item_key,type(item_value))
        self.type_dict[new_item_key] = type(item_value)
        # 创建并添加对应的编辑控件
        self.edit_fields[f"{parent_key}[{list_index}]"] =item_value
        self.create_list_item_widget(new_item_key, item_value, layout, list_index)
        self.clearLayout(self.scrollLayout)

        # 根据最新的yaml_data重新构建UI
        self.create_widgets(self.yaml_data, self.scrollLayout)

    def remove_list_item(self, parent_key, list_index, layout):
        # 将 parent_key 字符串转换为路径列表
        key_path = parent_key.split('.')
        # 使用路径列表逐级访问 yaml_data 中的嵌套结构
        target = self.yaml_data
        for key in key_path[:-1]:  # 不包括最后一个元素，因为我们需要访问列表所在的父级
            if key.isdigit():  # 如果键是数字，表示访问的是列表的索引
                key = int(key)  # 将键转换为整数
            target = target[key]

        # 从目标列表中移除指定索引的元素
        del target[key_path[-1]][list_index]

        # 更新type_dict以移除该元素的类型信息
        item_key = f"{parent_key}.{list_index}"
        if item_key in self.type_dict:
            del self.type_dict[item_key]

        # 从edit_fields中移除该元素的编辑控件
        edit_field_key = f"{parent_key}[{list_index}]"
        if edit_field_key in self.edit_fields:
            del self.edit_fields[edit_field_key]

        # 清除scrollLayout中的所有子布局和控件
        for i in reversed(range(self.scrollLayout.count())):
            widget_to_remove = self.scrollLayout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
            else:
                self.scrollLayout.itemAt(i).layout().setParent(None)
        self.clearLayout(self.scrollLayout)

        # 根据最新的yaml_data重新构建UI
        self.create_widgets(self.yaml_data, self.scrollLayout)


    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clearLayout(child.layout())
    def create_list_item_widget(self, parent_key, item, layout, index):
        itemLayout = QHBoxLayout()
        itemLabel = QLabel(f"Item {index + 1}:")
        itemLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        itemEdit = QLineEdit(str(item))
        #itemEdit.setMaximumWidth(200)
        itemEdit.setMinimumWidth(300)
        itemLayout.addWidget(itemLabel)
        itemLayout.addWidget(itemEdit)
        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(lambda: self.remove_list_item(parent_key, index, layout))
        itemLayout.addWidget(deleteButton)
        layout.addLayout(itemLayout)
        #print(parent_key)
        self.edit_fields[f"{parent_key}[{index}]"] = itemEdit
class jsonEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YAML Editor")

        # 创建一个下拉选择框
        self.comboBox = QComboBox()
        self.comboBox.addItem("Manyana/config.json", "基本设置")


        # 创建一个用于显示描述信息的 QLabel
        self.descriptionLabel = QLabel("")
        self.descriptionLabel.setWordWrap(True)  # 允许换行

        # 创建一个用于放置 YamlEditor 的 QWidget 作为容器
        self.editorContainer = QWidget()
        self.editorLayout = QVBoxLayout(self.editorContainer)

        # 布局
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.comboBox)
        self.mainLayout.addWidget(self.descriptionLabel)
        self.mainLayout.addWidget(self.editorContainer)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        # 连接信号
        self.comboBox.currentIndexChanged.connect(self.onConfigSelected)

        # 默认使用 config/api.yaml 初始化
        self.comboBox.setCurrentIndex(0)  # 触发 currentIndexChanged 信号，调用 onConfigSelected 方法
        self.onConfigSelected(0)  # 手动调用一次 onConfigSelected 方法

    def onConfigSelected(self, index):
        # 清除当前的编辑器（如果有）
        for i in reversed(range(self.editorLayout.count())):
            self.editorLayout.itemAt(i).widget().setParent(None)

        # 获取当前选中的文件描述
        description = self.comboBox.itemData(index)
        self.descriptionLabel.setText(description)

        # 根据选择加载新的编辑器
        yaml_file = self.comboBox.itemText(index)
        self.yamlEditor = configEditor(yaml_file)  # 假设 YamlEditor 接受 parent 和 yaml_file 作为参数
        self.editorLayout.addWidget(self.yamlEditor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JsonEditor()
    window.show()
    sys.exit(app.exec())