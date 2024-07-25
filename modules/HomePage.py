import sys

from PySide6.QtGui import Qt
from ruamel.yaml import YAML
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, \
    QScrollArea, QHBoxLayout, QGroupBox, QSizePolicy, QCheckBox, QComboBox

class configEditor(QWidget):
    def __init__(self, yaml_file):
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
        self.max_comment_length = self.get_max_comment_length(self.yaml_data)
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
            self.type_dict[full_key] = type(value)
            if isinstance(value, dict):
                self.create_type_dict(value, full_key + ".")
            elif isinstance(value, list):
                if value:
                    for i, item in enumerate(value):
                        item_key = f"{full_key}[{i}]"
                        self.type_dict[item_key] = type(item)
                        if isinstance(item, dict):
                            self.create_type_dict(item, item_key + ".")
                else:
                    self.type_dict[full_key] = type(None)

    def save_changes(self):
        def update_data(data, parent_key=""):
            for key in data.keys():
                full_key = parent_key + key
                if isinstance(data[key], dict):
                    update_data(data[key], full_key + ".")
                elif isinstance(data[key], list):
                    updated_list = []
                    for i in range(len(data[key])):
                        item_key = f"{full_key}[{i}]"
                        edit_widget = self.edit_fields.get(item_key)
                        if edit_widget:
                            original_value = edit_widget.text()
                            updated_value = self.convert_to_original_type(original_value, str)
                            updated_list.append(updated_value)
                        else:
                            updated_value = self.convert_to_original_type("", str)
                            updated_list.append(updated_value)
                    data[key] = updated_list
                else:
                    edit_widget = self.edit_fields.get(full_key)
                    if edit_widget:
                        if isinstance(edit_widget, QCheckBox):
                            original_value = edit_widget.isChecked()
                        else:
                            original_value = edit_widget.text()
                        data[key] = self.convert_to_original_type(original_value, self.type_dict[full_key])

        update_data(self.yaml_data)
        with open(self.yaml_file, 'w', encoding='utf-8') as file:
            self.yaml.dump(self.yaml_data, file)
        print("Changes saved.")

    def convert_to_original_type(self, value, expected_type):
        if expected_type == int:
            return int(value)
        elif expected_type == float:
            return float(value)
        elif expected_type == bool:
            return value if isinstance(value, bool) else value.lower() in ('true', 'yes', '1')
        elif expected_type == str:
            return value
        elif expected_type == list:
            return value
        return value

    def create_widgets(self, data, layout, parent_key="", level=0):
        max_label_width = 250
        max_edit_width = 300
        max_comment_width = self.max_comment_length * 6

        for key, value in data.items():
            comment = self.get_comment(data, key)

            # 添加label对应关系
            label_mapping = {
                'botName': '机器人名字',
                'botQQ': '机器人QQ',
                'master': '管理员QQ',
                'mainGroup': '主群(只填一个)',
                'vertify_key': 'mirai-api-http的key(整合包无需修改)',
                'port': 'mirai-api-http的ws端口(整合包无需修改)'
            }
            label_text = label_mapping.get(key, key)  # 如果没有找到对应的中文，则使用key本身

            if isinstance(value, dict):
                groupBox = QGroupBox(f"{label_text}: {comment}" if comment else label_text)
                groupBoxLayout = QVBoxLayout()
                self.create_widgets(value, groupBoxLayout, parent_key + key + ".", level + 1)
                groupBox.setLayout(groupBoxLayout)
                layout.addWidget(groupBox)
            elif isinstance(value, list):
                listLabel = QLabel(f"{label_text}: {comment}" if comment else label_text)
                listLabel.setMaximumWidth(max_label_width)
                layout.addWidget(listLabel)
                listLayout = QVBoxLayout()
                for i, item in enumerate(value):
                    self.create_list_item_widget(f"{parent_key}{key}", item, listLayout, i)
                addButton = QPushButton("Add Item")
                addButton.clicked.connect(
                    lambda checked=False, pk=parent_key + key: self.add_list_item(pk, len(value), listLayout))
                listLayout.addWidget(addButton)
                layout.addLayout(listLayout)
            else:
                hLayout = QHBoxLayout()
                label = QLabel(f"{label_text}:")
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
                commentLabel.setMinimumWidth(max_comment_width)

                hLayout.addWidget(label)
                hLayout.addWidget(edit)
                hLayout.addWidget(commentLabel)
                hLayout.setContentsMargins(level * 20, 0, 0, 0)
                layout.addLayout(hLayout)
                self.edit_fields[parent_key + key] = edit

    def get_comment(self, data, key):
        comment = None
        if key in data.ca.items:
            comment_items = data.ca.items[key]
            if comment_items and comment_items[2]:
                comment = comment_items[2].value
                if comment:
                    comment = comment.strip("# ").strip()
        return comment

    def add_list_item(self, parent_key, list_index, layout):
        new_item_key = f"{parent_key}.{list_index}"
        item_value = ""
        key_path = parent_key.split('.')
        target = self.yaml_data
        for key in key_path:
            if key.isdigit():
                key = int(key)
            target = target[key]
        target.append(item_value)
        self.type_dict[new_item_key] = type(item_value)
        self.edit_fields[f"{parent_key}[{list_index}]"] = item_value
        self.create_list_item_widget(new_item_key, item_value, layout, list_index)
        self.clearLayout(self.scrollLayout)
        self.create_widgets(self.yaml_data, self.scrollLayout)

    def remove_list_item(self, parent_key, list_index, layout):
        key_path = parent_key.split('.')
        target = self.yaml_data
        for key in key_path[:-1]:
            if key.isdigit():
                key = int(key)
            target = target[key]
        del target[key_path[-1]][list_index]
        item_key = f"{parent_key}.{list_index}"
        if item_key in self.type_dict:
            del self.type_dict[item_key]
        edit_field_key = f"{parent_key}[{list_index}]"
        if edit_field_key in self.edit_fields:
            del self.edit_fields[edit_field_key]
        for i in reversed(range(self.scrollLayout.count())):
            widget_to_remove = self.scrollLayout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
            else:
                self.scrollLayout.itemAt(i).layout().setParent(None)
        self.clearLayout(self.scrollLayout)
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
        itemEdit.setMinimumWidth(300)
        itemLayout.addWidget(itemLabel)
        itemLayout.addWidget(itemEdit)
        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(lambda: self.remove_list_item(parent_key, index, layout))
        itemLayout.addWidget(deleteButton)
        layout.addLayout(itemLayout)
        self.edit_fields[f"{parent_key}[{index}]"] = itemEdit


class jsonEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YAML Editor")

        self.comboBox = QComboBox()
        self.comboBox.addItem("Manyana/config.json", "基本设置")
        self.descriptionLabel = QLabel("")
        self.descriptionLabel.setWordWrap(True)

        self.editorContainer = QWidget()
        self.editorLayout = QVBoxLayout(self.editorContainer)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.comboBox)
        self.mainLayout.addWidget(self.descriptionLabel)
        self.mainLayout.addWidget(self.editorContainer)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        self.comboBox.currentIndexChanged.connect(self.onConfigSelected)
        self.comboBox.setCurrentIndex(0)
        self.onConfigSelected(0)

    def onConfigSelected(self, index):
        for i in reversed(range(self.editorLayout.count())):
            self.editorLayout.itemAt(i).widget().setParent(None)

        description = self.comboBox.itemData(index)
        self.descriptionLabel.setText(description)

        yaml_file = self.comboBox.itemText(index)
        self.yamlEditor = configEditor(yaml_file)
        self.editorLayout.addWidget(self.yamlEditor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = jsonEditor()
    window.show()
    sys.exit(app.exec())
