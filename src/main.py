"""
DailyBill - 个人账单分类管理工具
主程序入口 - 使用 tkinter
"""
import sys
import os
import threading
from typing import List, Dict, Optional

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from parsers import AlipayParser, WechatParser, BankParser
from classifier import KeywordMatcher, RuleEngine
from exporter import ExcelExporter


class DailyBillApp:
    """主应用程序类"""

    def __init__(self, root):
        self.root = root
        self.root.title("DailyBill - 个人账单分类工具")
        self.root.geometry("1000x700")

        # 初始化组件
        self.parsers = [AlipayParser(), WechatParser(), BankParser()]
        self.classifier = KeywordMatcher()
        self.rule_engine = RuleEngine()
        self.exporter = ExcelExporter()

        # 数据
        self.current_data: List[Dict] = []
        self.processed_files: List[str] = []

        # 创建界面
        self._create_ui()

    def _create_ui(self):
        """创建用户界面"""
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.root, text="文件选择", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)

        self.file_label = ttk.Label(file_frame, text="未选择文件", foreground='gray')
        self.file_label.pack(side='left', fill='x', expand=True)

        ttk.Button(file_frame, text="选择文件", command=self._select_files).pack(side='right', padx=5)
        ttk.Button(file_frame, text="选择文件夹", command=self._select_directory).pack(side='right', padx=5)

        # 操作区域
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(action_frame, text="分类筛选:").pack(side='left')

        self.category_var = tk.StringVar(value="全部")
        self.category_combo = ttk.Combobox(action_frame, textvariable=self.category_var, width=15)
        self.category_combo['values'] = ['全部'] + self.classifier.get_categories()
        self.category_combo.pack(side='left', padx=5)
        self.category_combo.bind('<<ComboboxSelected>>', self._filter_by_category)

        ttk.Button(action_frame, text="开始处理", command=self._process_files).pack(side='right', padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=5)

        # 数据表格
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ['date', 'category', 'merchant', 'description', 'amount', 'type', 'source']
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        # 设置列
        col_names = {'date': '日期', 'category': '类别', 'merchant': '交易对方',
                     'description': '描述', 'amount': '金额', 'type': '类型', 'source': '来源'}
        for col in columns:
            self.tree.heading(col, text=col_names[col])
            self.tree.column(col, width=100)

        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 统计信息
        stats_frame = ttk.LabelFrame(self.root, text="统计信息", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)

        self.stats_income = ttk.Label(stats_frame, text="收入: ¥0.00")
        self.stats_income.pack(side='left', padx=20)

        self.stats_expense = ttk.Label(stats_frame, text="支出: ¥0.00")
        self.stats_expense.pack(side='left', padx=20)

        self.stats_net = ttk.Label(stats_frame, text="净支出: ¥0.00")
        self.stats_net.pack(side='left', padx=20)

        self.stats_count = ttk.Label(stats_frame, text="笔数: 0")
        self.stats_count.pack(side='left', padx=20)

        # 导出按钮区域 - 居中显示，更加醒目
        export_frame = ttk.Frame(self.root, padding=15)
        export_frame.pack(fill='x', padx=10, pady=10)

        # 使用普通 Button 可以设置背景色
        self.export_btn = tk.Button(
            export_frame,
            text="📤  导 出 Excel  ",
            command=self._export_data,
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief='raised',
            padx=20,
            pady=8,
            cursor='hand2',
            state='disabled'
        )
        self.export_btn.pack(side='right', padx=10)

        ttk.Label(export_frame, text="提示：选择文件 → 开始处理 → 导出Excel", font=('Microsoft YaHei', 9), foreground='#666666').pack(side='left', padx=10)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief='sunken').pack(fill='x', side='bottom')

    def _select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择账单文件",
            filetypes=[("Excel/CSV 文件", "*.xlsx *.xls *.csv"), ("所有文件", "*.*")]
        )

        if files:
            self.processed_files = list(files)
            self.file_label.config(text=f"已选择 {len(files)} 个文件", foreground='black')

    def _select_directory(self):
        """选择文件夹"""
        directory = filedialog.askdirectory(title="选择文件夹")

        if directory:
            files = []
            for ext in ['*.xlsx', '*.xls', '*.csv']:
                pattern = os.path.join(directory, ext[1:])
                for f in os.listdir(directory):
                    if f.endswith(ext[2:]):
                        files.append(os.path.join(directory, f))

            if files:
                self.processed_files = files
                self.file_label.config(text=f"已选择 {len(files)} 个文件", foreground='black')
            else:
                messagebox.showwarning("提示", "所选文件夹中没有找到 Excel 或 CSV 文件")

    def _process_files(self):
        """处理文件"""
        if not self.processed_files:
            messagebox.showwarning("提示", "请先选择要处理的文件")
            return

        self.status_var.set("正在处理...")
        self.progress_bar['value'] = 0

        # 在新线程中处理
        thread = threading.Thread(target=self._do_process)
        thread.daemon = True
        thread.start()

    def _do_process(self):
        """执行处理（在后台线程中）"""
        try:
            all_data = []
            total_files = len(self.processed_files)

            for i, file_path in enumerate(self.processed_files):
                self.status_var.set(f"正在处理: {os.path.basename(file_path)}")
                self.progress_bar['value'] = (i / total_files) * 80

                df = None
                for parser in self.parsers:
                    if parser.can_parse(file_path):
                        try:
                            records = parser.parse(file_path)
                            if records:
                                all_data.extend(records)
                            break
                        except Exception as e:
                            continue

            if not all_data:
                self.root.after(0, lambda: messagebox.showerror("错误", "未能解析任何有效的交易数据"))
                return

            # 分类
            self.status_var.set("正在进行分类...")
            self.progress_bar['value'] = 90

            # 先使用规则引擎
            all_data = self.rule_engine.classify_records(all_data)

            # 再使用关键词匹配（只对未分类的）
            for record in all_data:
                if not record.get('category'):
                    category, _ = self.classifier.classify(
                        record.get('description', ''),
                        record.get('merchant', '')
                    )
                    record['category'] = category

            self.current_data = all_data

            # 更新界面
            self.root.after(0, self._on_process_finished)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出错: {str(e)}"))

    def _on_process_finished(self):
        """处理完成回调"""
        self.progress_bar['value'] = 100
        self._display_data(self.current_data)
        self._update_stats(self.current_data)
        self.status_var.set(f"处理完成，共 {len(self.current_data)} 条记录")
        # 启用导出按钮
        self.export_btn.config(state='normal')

    def _display_data(self, records: List[Dict]):
        """显示数据"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 填充数据
        for record in records:
            date_str = str(record.get('date', ''))[:10]
            values = (
                date_str,
                record.get('category', ''),
                record.get('merchant', ''),
                record.get('description', ''),
                f"¥{record.get('amount', 0):.2f}",
                record.get('type', ''),
                record.get('source', '')
            )
            self.tree.insert('', 'end', values=values)

    def _filter_by_category(self, event=None):
        """按分类筛选"""
        category = self.category_var.get()

        if not self.current_data:
            return

        if category == "全部":
            self._display_data(self.current_data)
            self._update_stats(self.current_data)
        else:
            filtered = [r for r in self.current_data if r.get('category') == category]
            self._display_data(filtered)
            self._update_stats(filtered)

    def _update_stats(self, records: List[Dict]):
        """更新统计信息"""
        income = sum(r.get('amount', 0) for r in records if r.get('type') == '收入')
        expense = sum(r.get('amount', 0) for r in records if r.get('type') == '支出')
        net = expense - income
        count = len(records)

        self.stats_income.config(text=f"收入: ¥{income:,.2f}")
        self.stats_expense.config(text=f"支出: ¥{expense:,.2f}")
        self.stats_net.config(text=f"净支出: ¥{net:,.2f}")
        self.stats_count.config(text=f"笔数: {count}")

    def _export_data(self):
        """导出数据"""
        if not self.current_data:
            messagebox.showwarning("提示", "没有可导出的数据")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".xlsx",
            initialfile=f"账单分类_{datetime.now().strftime('%Y%m%d')}.xlsx",
            filetypes=[("Excel 文件", "*.xlsx")]
        )

        if file_path:
            try:
                self.exporter.export(self.current_data, file_path)
                messagebox.showinfo("成功", f"数据已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = DailyBillApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
