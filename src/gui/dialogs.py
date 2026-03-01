"""
对话框组件
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt


class CategoryEditDialog(QDialog):
    """分类编辑对话框"""

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.setWindowTitle("编辑分类")
        self.setMinimumWidth(400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 分类列表
        list_group = QGroupBox("分类列表")
        list_layout = QVBoxLayout(list_group)

        self.category_list = QListWidget()
        self.category_list.addItems(self.categories)
        list_layout.addWidget(self.category_list)

        # 按钮行
        btn_layout = QHBoxLayout()

        btn_add = QPushButton("添加")
        btn_add.clicked.connect(self._add_category)
        btn_remove = QPushButton("删除")
        btn_remove.clicked.connect(self._remove_category)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)

        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)

        # 新分类输入
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("新分类名称:"))
        self.new_category_input = QLineEdit()
        input_layout.addWidget(self.new_category_input)
        layout.addLayout(input_layout)

        # 确定取消按钮
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _add_category(self):
        name = self.new_category_input.text().strip()
        if name and name not in self.categories:
            self.category_list.addItem(name)
            self.categories.append(name)
            self.new_category_input.clear()
        elif name in self.categories:
            QMessageBox.warning(self, "提示", "该分类已存在")

    def _remove_category(self):
        current_item = self.category_list.currentItem()
        if current_item:
            self.category_list.takeItem(self.category_list.row(current_item))
            self.categories.remove(current_item.text())

    def get_categories(self):
        return self.categories


class KeywordEditDialog(QDialog):
    """关键词编辑对话框"""

    def __init__(self, category, keywords, parent=None):
        super().__init__(parent)
        self.category = category
        self.keywords = list(keywords)
        self.setWindowTitle(f"编辑关键词 - {category}")
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 关键词列表
        list_group = QGroupBox("关键词列表")
        list_layout = QVBoxLayout(list_group)

        self.keyword_list = QListWidget()
        self.keyword_list.addItems(self.keywords)
        list_layout.addWidget(self.keyword_list)

        # 按钮行
        btn_layout = QHBoxLayout()

        btn_add = QPushButton("添加")
        btn_add.clicked.connect(self._add_keyword)
        btn_remove = QPushButton("删除")
        btn_remove.clicked.connect(self._remove_keyword)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)

        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)

        # 新关键词输入
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("新关键词:"))
        self.new_keyword_input = QLineEdit()
        input_layout.addWidget(self.new_keyword_input)
        layout.addLayout(input_layout)

        # 确定取消按钮
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _add_keyword(self):
        keyword = self.new_keyword_input.text().strip()
        if keyword and keyword not in self.keywords:
            self.keyword_list.addItem(keyword)
            self.keywords.append(keyword)
            self.new_keyword_input.clear()
        elif keyword in self.keywords:
            QMessageBox.warning(self, "提示", "该关键词已存在")

    def _remove_keyword(self):
        current_item = self.keyword_list.currentItem()
        if current_item:
            self.keyword_list.takeItem(self.keyword_list.row(current_item))
            self.keywords.remove(current_item.text())

    def get_keywords(self):
        return self.keywords
