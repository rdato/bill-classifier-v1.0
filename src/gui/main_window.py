"""
主窗口界面
"""
import os
import sys
from typing import List, Optional
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QProgressBar, QGroupBox, QSplitter,
    QStatusBar, QMenuBar, QMenu, QAction, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers import AlipayParser, WechatParser, BankParser
from classifier import KeywordMatcher, RuleEngine
from exporter import ExcelExporter


class ProcessThread(QThread):
    """处理线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)

    def __init__(self, files: List[str], parsers, classifier, rule_engine):
        super().__init__()
        self.files = files
        self.parsers = parsers
        self.classifier = classifier
        self.rule_engine = rule_engine

    def run(self):
        try:
            all_data = []

            for file_path in self.files:
                self.progress.emit(f"正在处理: {os.path.basename(file_path)}")

                # 尝试使用不同的解析器
                df = None
                for parser in self.parsers:
                    if parser.can_parse(file_path):
                        try:
                            df = parser.parse(file_path)
                            break
                        except Exception as e:
                            continue

                if df is not None and len(df) > 0:
                    all_data.append(df)

            if not all_data:
                self.error.emit("未能解析任何有效的交易数据")
                return

            # 合并所有数据
            combined_df = pd.concat(all_data, ignore_index=True)

            self.progress.emit("正在进行分类...")

            # 先使用规则引擎分类
            combined_df = self.rule_engine.classify_dataframe(combined_df)

            # 对于规则未匹配的，使用关键词匹配
            mask = combined_df['rule_category'].isna()
            if mask.any():
                unmatched_df = combined_df[mask].copy()
                unmatched_df = self.classifier.classify_dataframe(unmatched_df)
                combined_df.loc[mask, 'category'] = unmatched_df['category']

            # 填充规则匹配的分类
            combined_df.loc[~combined_df['rule_category'].isna(), 'category'] = \
                combined_df.loc[~combined_df['rule_category'].isna(), 'rule_category']

            self.progress.emit("处理完成")
            self.finished.emit(combined_df)

        except Exception as e:
            self.error.emit(f"处理过程中出错: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DailyBill - 个人账单分类工具")
        self.setGeometry(100, 100, 1200, 800)

        # 初始化组件
        self.parsers = [AlipayParser(), WechatParser(), BankParser()]
        self.classifier = KeywordMatcher()
        self.rule_engine = RuleEngine()
        self.exporter = ExcelExporter()

        # 数据
        self.current_data: Optional[pd.DataFrame] = None
        self.processed_files: List[str] = []

        # 初始化界面
        self._init_ui()
        self._init_menu()

    def _init_ui(self):
        """初始化界面"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_group)

        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: gray;")

        btn_select = QPushButton("选择文件")
        btn_select.clicked.connect(self._select_files)

        btn_select_dir = QPushButton("选择文件夹")
        btn_select_dir.clicked.connect(self._select_directory)

        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(btn_select)
        file_layout.addWidget(btn_select_dir)

        main_layout.addWidget(file_group)

        # 分类过滤区域
        filter_group = QGroupBox("分类筛选")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("选择分类:"))

        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        self.category_combo.addItems(self.classifier.get_categories())
        self.category_combo.currentTextChanged.connect(self._filter_by_category)

        filter_layout.addWidget(self.category_combo)
        filter_layout.addStretch()

        btn_process = QPushButton("开始处理")
        btn_process.clicked.connect(self._process_files)
        btn_process.setStyleSheet("background-color: #4472C4; color: white;")

        filter_layout.addWidget(btn_process)

        main_layout.addWidget(filter_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 数据表格
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)

        main_layout.addWidget(self.table, 1)

        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QHBoxLayout(stats_group)

        self.stats_income = QLabel("收入: ¥0.00")
        self.stats_expense = QLabel("支出: ¥0.00")
        self.stats_net = QLabel("净支出: ¥0.00")
        self.stats_count = QLabel("笔数: 0")

        for label in [self.stats_income, self.stats_expense, self.stats_net, self.stats_count]:
            label.setFont(QFont("Arial", 11))
            stats_layout.addWidget(label)

        main_layout.addWidget(stats_group)

        # 导出按钮
        export_layout = QHBoxLayout()

        btn_export = QPushButton("导出 Excel")
        btn_export.clicked.connect(self._export_data)
        btn_export.setStyleSheet("background-color: #70AD47; color: white;")

        export_layout.addStretch()
        export_layout.addWidget(btn_export)

        main_layout.addLayout(export_layout)

        # 状态栏
        self.setStatusBar(QStatusBar())

    def _init_menu(self):
        """初始化菜单"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        open_action = QAction("打开文件", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._select_files)
        file_menu.addAction(open_action)

        export_action = QAction("导出", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _select_files(self):
        """选择文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择账单文件",
            "",
            "Excel/CSV 文件 (*.xlsx *.xls *.csv);;所有文件 (*)"
        )

        if files:
            self.processed_files = files
            self.file_label.setText(f"已选择 {len(files)} 个文件")
            self.file_label.setStyleSheet("color: black;")

    def _select_directory(self):
        """选择文件夹"""
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹")

        if directory:
            # 查找所有 Excel 和 CSV 文件
            files = []
            for ext in ['*.xlsx', '*.xls', '*.csv']:
                files.extend([
                    os.path.join(directory, f)
                    for f in os.listdir(directory)
                    if f.endswith(ext[1:])
                ])

            if files:
                self.processed_files = files
                self.file_label.setText(f"已选择 {len(files)} 个文件")
                self.file_label.setStyleSheet("color: black;")
            else:
                QMessageBox.warning(self, "提示", "所选文件夹中没有找到 Excel 或 CSV 文件")

    def _process_files(self):
        """处理文件"""
        if not self.processed_files:
            QMessageBox.warning(self, "提示", "请先选择要处理的文件")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度

        # 创建处理线程
        self.process_thread = ProcessThread(
            self.processed_files,
            self.parsers,
            self.classifier,
            self.rule_engine
        )
        self.process_thread.progress.connect(self.statusBar().showMessage)
        self.process_thread.finished.connect(self._on_process_finished)
        self.process_thread.error.connect(self._on_process_error)
        self.process_thread.start()

    def _on_process_finished(self, df: pd.DataFrame):
        """处理完成"""
        self.progress_bar.setVisible(False)
        self.current_data = df
        self._display_data(df)
        self._update_stats(df)
        self.statusBar().showMessage(f"处理完成，共 {len(df)} 条记录")

    def _on_process_error(self, error_msg: str):
        """处理出错"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", error_msg)

    def _display_data(self, df: pd.DataFrame):
        """显示数据"""
        # 选择要显示的列
        display_cols = ['date', 'category', 'merchant', 'description', 'amount', 'type', 'source']
        display_cols = [col for col in display_cols if col in df.columns]

        display_df = df[display_cols].copy()

        # 列名映射
        col_names = {
            'date': '日期',
            'category': '类别',
            'merchant': '交易对方',
            'description': '描述',
            'amount': '金额',
            'type': '类型',
            'source': '来源'
        }
        display_df = display_df.rename(columns=col_names)

        # 设置表格
        self.table.setRowCount(len(display_df))
        self.table.setColumnCount(len(display_df.columns))
        self.table.setHorizontalHeaderLabels(display_df.columns.tolist())

        # 填充数据
        for row_idx, row in enumerate(display_df.values):
            for col_idx, value in enumerate(row):
                # 格式化日期
                if display_df.columns[col_idx] == '日期' and pd.notna(value):
                    try:
                        value = pd.to_datetime(value).strftime('%Y-%m-%d')
                    except:
                        value = str(value)

                # 格式化金额
                if display_df.columns[col_idx] == '金额' and isinstance(value, (int, float)):
                    value = f"¥{value:,.2f}"

                item = QTableWidgetItem(str(value) if pd.notna(value) else '')
                self.table.setItem(row_idx, col_idx, item)

        # 调整列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

    def _filter_by_category(self, category: str):
        """按分类筛选"""
        if self.current_data is None:
            return

        if category == "全部":
            self._display_data(self.current_data)
        else:
            filtered_df = self.current_data[self.current_data['category'] == category]
            self._display_data(filtered_df)

    def _update_stats(self, df: pd.DataFrame):
        """更新统计信息"""
        if 'amount' not in df.columns or 'type' not in df.columns:
            return

        income = df[df['type'] == '收入']['amount'].sum()
        expense = df[df['type'] == '支出']['amount'].sum()
        net = expense - income
        count = len(df)

        self.stats_income.setText(f"收入: ¥{income:,.2f}")
        self.stats_expense.setText(f"支出: ¥{expense:,.2f}")
        self.stats_net.setText(f"净支出: ¥{net:,.2f}")
        self.stats_count.setText(f"笔数: {count}")

    def _export_data(self):
        """导出数据"""
        if self.current_data is None:
            QMessageBox.warning(self, "提示", "没有可导出的数据")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存文件",
            f"账单分类_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            "Excel 文件 (*.xlsx)"
        )

        if file_path:
            try:
                self.exporter.export(self.current_data, file_path)
                QMessageBox.information(self, "成功", f"数据已导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 DailyBill",
            "DailyBill - 个人账单分类工具\n\n"
            "版本: 1.0.0\n\n"
            "功能:\n"
            "- 支持支付宝、微信、银行账单\n"
            "- 自动分类交易记录\n"
            "- 导出分类汇总报表"
        )
