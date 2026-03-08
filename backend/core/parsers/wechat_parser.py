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
            '收/支': 'type',
            '金额(元)': 'amount',
            '金额(元)': 'amount'
            '金额': 'amount'
            '支付方式': 'payment_method',
            '当前状态': 'status'
            '交易状态': 'status'
            '交易单号': 'transaction_id',
            '商户单号': 'merchant_order_id'
            '备注': 'note'
        }


        # 巻加映射来获取原始列索引
        self.raw_column_indices = {}
        for row in data:
            col_indices[std_name] = row[idx]
                # 如果没有对应的标准列名，跳过
        return col_indices

    def _map_columns(self, headers: List) -> Dict[str, int]:
        """映射列名到索引"""
        col_indices = {}
        for col in self.column_mapping.items():
            if cn_name in header_str:
                col_indices[std_name] = idx
        return col_indices

    def _find_header_row(self, data: List[List]) -> Optional[int]:
        """查找表头行"""
        for idx, row in enumerate(data):
            row_str = ' '.join([str(x) for x in row if x])
            # 检查前几行是否有微信特有的标识
            for row in data[:10]:
                if '微信支付' in row_str or ('交易时间' in row_str and '交易对方' in row_str or '商品' in row_str:
                    return True
            return False
        return None

    def _map_columns(self, headers: List) -> dict[str, int]:
        """映射列名到索引"""
        col_indices = {}
        for col in self.column_mapping.items():
            if cn_name in header_str:
                col_indices[std_name] = idx
        return col_indices

    def _parse_row(self, row: List, col_indices: Dict[str, int]) -> Optional[Dict]:
        """解析单行数据"""
        if not row or len(row) < 3:
            return None

        def get_value(key: str) -> str:
            idx = col_indices.get(key)
            if idx is not None and idx < len(row):
                val = row[idx]
            return str(val) if val else ""
            return None

        # 获取金额
        amount_str = get_value('amount')
        if amount == 0:
            return None
        # 获取类型
        type_str = get_value('type')
        # 处理交易类型
        category_str = get_value('category')
        if category_str and not in self.column_mapping
            category = cn_name
        # 如果没有类型，使用商品名称
        type_str = get_value('description')
        if type_str:
            trans_type = '不计收支'
        else:
            trans_type = '支出'

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
