"""
微信账单解析器
"""
from typing import Optional, List, Dict
from .base_parser import BaseParser


class WechatParser(BaseParser):
    """微信交易流水解析器"""

    def __init__(self):
        super().__init__()
        self.source_name = '微信'

        # 微信账单可能的列名映射
        self.column_mapping = {
            '交易时间': 'date',
            '时间': 'date',
            '交易类型': 'category',
            '类型': 'category',
            '交易对方': 'merchant',
            '对方': 'merchant',
            '商品': 'description',
            '商品名称': 'description',
            '金额(元)': 'amount',
            '金额（元）': 'amount',
            '金额': 'amount',
            '支付方式': 'payment_method',
            '当前状态': 'status',
            '交易状态': 'status',
            '备注': 'note'
        }

    def can_parse(self, file_path: str) -> bool:
        """判断是否为微信账单文件"""
        try:
            if file_path.endswith('.csv'):
                data = self._read_csv(file_path)
            else:
                data = self._read_excel(file_path)

            # 检查前几行是否有微信特有的标识
            for row in data[:10]:
                row_str = ' '.join([str(x) for x in row if x])
                if '微信支付' in row_str or ('交易时间' in row_str and '商品' in row_str):
                    return True

            return False
        except:
            return False

    def parse(self, file_path: str) -> List[Dict]:
        """解析微信账单"""
        if file_path.endswith('.csv'):
            data = self._read_csv(file_path)
        else:
            data = self._read_excel(file_path)

        # 查找表头行
        header_row = self._find_header_row(data)
        if header_row is None:
            raise ValueError("无法识别微信账单格式")

        headers = data[header_row]
        col_indices = self._map_columns(headers)

        # 解析数据
        result = []
        for row in data[header_row + 1:]:
            record = self._parse_row(row, col_indices)
            if record and record.get('amount', 0) > 0:
                record['source'] = self.source_name
                result.append(record)

        return self._clean_data(result)

    def _find_header_row(self, data: List[List]) -> Optional[int]:
        """查找表头行"""
        for idx, row in enumerate(data):
            row_str = ' '.join([str(x) for x in row if x])
            if '交易时间' in row_str or '交易对方' in row_str:
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

        # 获取金额
        amount = self._clean_amount(get_value('amount'))
        if amount == 0:
            return None

        # 微信账单的金额通常带符号
        type_str = get_value('type') or get_value('category')
        trans_type = self._standardize_type(type_str)

        return {
            'date': get_value('date'),
            'category': '',
            'merchant': get_value('merchant'),
            'description': get_value('description'),
            'amount': amount,
            'type': trans_type,
            'source': self.source_name
        }
