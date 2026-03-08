"""
银行账单解析器（通用）
"""
from typing import Optional, List, Dict
from .base_parser import BaseParser


class BankParser(BaseParser):
    """银行交易流水解析器（通用）"""

    def __init__(self):
        super().__init__()
        self.source_name = '银行'

        # 银行账单可能的列名映射
        self.column_mapping = {
            '交易日期': 'date',
            '交易时间': 'date',
            '日期': 'date',
            '时间': 'date',
            '摘要': 'description',
            '交易摘要': 'description',
            '用途': 'description',
            '对方户名': 'merchant',
            '对方名称': 'merchant',
            '收款人': 'merchant',
            '付款人': 'merchant',
            '交易金额': 'amount',
            '金额': 'amount',
            '发生额': 'amount',
            '借方发生额': 'debit',
            '贷方发生额': 'credit',
            '支出': 'debit',
            '收入': 'credit',
            '借/贷': 'type',
            '交易类型': 'type',
            '记账类型': 'type',
            '账户余额': 'balance',
            '余额': 'balance',
            '备注': 'note',
            '附言': 'note'
        }

    def can_parse(self, file_path: str) -> bool:
        """判断是否为银行账单文件"""
        try:
            if file_path.endswith('.csv'):
                data = self._read_csv(file_path)
            else:
                data = self._read_excel(file_path)

            # 银行账单特征：通常有借/贷、摘要、对方户名等
            bank_indicators = ['借', '贷', '摘要', '对方户名', '发生额', '账户余额']

            for row in data[:10]:
                row_str = ' '.join([str(x) for x in row if x])
                for indicator in bank_indicators:
                    if indicator in row_str:
                        return True

            return False
        except:
            return False

    def parse(self, file_path: str) -> List[Dict]:
        """解析银行账单"""
        if file_path.endswith('.csv'):
            data = self._read_csv(file_path)
        else:
            data = self._read_excel(file_path)

        # 查找表头行
        header_row = self._find_header_row(data)
        if header_row is None:
            raise ValueError("无法识别银行账单格式")

        headers = data[header_row]
        col_indices = self._map_columns(headers)

        # 解析数据
        result = []
        for row in data[header_row + 1:]:
            record = self._parse_row(row, col_indices)
            if record and record.get('amount', 0) > 0:
                result.append(record)

        return self._clean_data(result)

    def _find_header_row(self, data: List[List]) -> Optional[int]:
        """查找表头行"""
        for idx, row in enumerate(data):
            row_str = ' '.join([str(x) for x in row if x])
            if '交易日期' in row_str or '摘要' in row_str or '对方户名' in row_str:
                return idx
        return None

    def _map_columns(self, headers: List) -> Dict[str, int]:
        """映射列名到索引"""
        col_indices = {}
        for idx, header in enumerate(headers):
            if not header:
                continue
            header_str = str(header)
            for cn_name, std_name in self.column_mapping.items():
                if cn_name in header_str:
                    col_indices[std_name] = idx
                    break
        return col_indices

    def _parse_row(self, row: List, col_indices: Dict[str, int]) -> Optional[Dict]:
        """解析单行数据"""
        if not row or len(row) < 3:
            return None

        def get_value(key: str) -> str:
            idx = col_indices.get(key)
            if idx is not None and idx < len(row):
                val = row[idx]
                return str(val) if val else ''
            return ''

        # 处理借贷金额
        debit = self._clean_amount(get_value('debit'))
        credit = self._clean_amount(get_value('credit'))

        if credit > 0:
            amount = credit
            trans_type = '收入'
        elif debit > 0:
            amount = debit
            trans_type = '支出'
        else:
            amount = self._clean_amount(get_value('amount'))
            if amount == 0:
                return None
            # 根据借/贷列判断类型
            type_str = get_value('type')
            trans_type = self._standardize_type(type_str)

        # 构建原始数据字典（保存所有原始列）
        raw_data = {}
        for cn_name, std_name in self.column_mapping.items():
            idx = col_indices.get(std_name)
            if idx is not None and idx < len(row):
                val = row[idx]
                raw_data[cn_name] = str(val).strip() if val else ''

        return {
            'date': get_value('date'),
            'category': '',
            'merchant': get_value('merchant'),
            'description': get_value('description'),
            'amount': amount,
            'type': trans_type,
            'source': self.source_name,
            'raw_data': raw_data
        }
