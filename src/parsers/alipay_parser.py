"""
支付宝账单解析器
"""
import csv
from typing import Optional, List, Dict
from .base_parser import BaseParser


class AlipayParser(BaseParser):
    """支付宝交易流水解析器"""

    def __init__(self):
        super().__init__()
        self.source_name = '支付宝'

        # 支付宝账单列名映射
        self.column_mapping = {
            '交易时间': 'date',
            '交易分类': 'category',
            '交易对方': 'merchant',
            '对方账号': 'merchant_account',
            '商品说明': 'description',
            '收/支': 'type',
            '金额': 'amount',
            '收/付款方式': 'payment_method',
            '交易状态': 'status',
            '交易订单号': 'order_id',
            '商家订单号': 'merchant_order_id',
            '备注': 'note'
        }

    def can_parse(self, file_path: str) -> bool:
        """判断是否为支付宝账单文件"""
        try:
            # 尝试多种编码读取
            data = self._read_csv_with_encoding(file_path)

            # 检查是否有支付宝特有的列
            for row in data[:30]:  # 检查前30行
                row_str = ','.join([str(x) for x in row if x])
                # 支付宝特征：包含交易时间和收/支
                if '交易时间' in row_str and '收/支' in row_str:
                    return True
                # 或者包含支付宝标识
                if '支付宝' in row_str:
                    return True

            return False
        except:
            return False

    def _read_csv_with_encoding(self, file_path: str) -> List[List]:
        """尝试多种编码读取 CSV 文件"""
        encodings = ['gbk', 'gb18030', 'utf-8', 'utf-8-sig', 'gb2312']

        for encoding in encodings:
            try:
                data = []
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.reader(f)
                    for row in reader:
                        data.append(row)
                # 验证读取是否成功（检查是否有中文乱码）
                for row in data[:10]:
                    row_str = ''.join([str(x) for x in row if x])
                    if '交易时间' in row_str or '支付宝' in row_str:
                        return data
            except:
                continue

        raise ValueError("无法识别文件编码")

    def parse(self, file_path: str) -> List[Dict]:
        """解析支付宝账单"""
        # 读取 CSV 文件
        data = self._read_csv_with_encoding(file_path)

        # 查找表头行
        header_row = self._find_header_row(data)
        if header_row is None:
            raise ValueError("无法识别支付宝账单格式：找不到表头行")

        headers = data[header_row]
        col_indices = self._map_columns(headers)

        # 验证必要的列
        if 'date' not in col_indices or 'amount' not in col_indices:
            raise ValueError("支付宝账单缺少必要的列")

        # 解析数据
        result = []
        for row in data[header_row + 1:]:
            # 跳过空行和分隔行
            if not row or len(row) < 3:
                continue
            if row[0].startswith('-') or row[0].startswith('---'):
                continue

            record = self._parse_row(row, col_indices)
            if record and record.get('amount', 0) > 0:
                record['source'] = self.source_name
                result.append(record)

        return self._clean_data(result)

    def _find_header_row(self, data: List[List]) -> Optional[int]:
        """查找表头行"""
        for idx, row in enumerate(data):
            if not row:
                continue
            row_str = ','.join([str(x) for x in row if x])
            # 表头特征：包含"交易时间"和"收/支"
            if '交易时间' in row_str and '收/支' in row_str:
                return idx
        return None

    def _map_columns(self, headers: List) -> Dict[str, int]:
        """映射列名到索引"""
        col_indices = {}
        for idx, header in enumerate(headers):
            if not header:
                continue
            header_str = str(header).strip()
            for cn_name, std_name in self.column_mapping.items():
                if cn_name in header_str or header_str in cn_name:
                    col_indices[std_name] = idx
                    break
        return col_indices

    def _parse_row(self, row: List, col_indices: Dict[str, int]) -> Optional[Dict]:
        """解析单行数据"""
        def get_value(key: str) -> str:
            idx = col_indices.get(key)
            if idx is not None and idx < len(row):
                val = row[idx]
                return str(val).strip() if val else ''
            return ''

        # 获取金额
        amount_str = get_value('amount')
        amount = self._clean_amount(amount_str)
        if amount == 0:
            return None

        # 获取类型
        type_str = get_value('type')
        trans_type = self._standardize_alipay_type(type_str)

        # 如果是"不计收支"，跳过
        if trans_type == '不计收支':
            return None

        return {
            'date': get_value('date'),
            'category': '',  # 分类由分类器处理
            'merchant': get_value('merchant'),
            'description': get_value('description'),
            'amount': amount,
            'type': trans_type,
            'source': self.source_name
        }

    def _standardize_alipay_type(self, type_str: str) -> str:
        """标准化支付宝的交易类型"""
        if not type_str:
            return '支出'

        type_str = str(type_str).strip()

        if '收入' in type_str or '退款' in type_str:
            return '收入'
        elif '支出' in type_str:
            return '支出'
        elif '不计' in type_str:
            return '不计收支'

        return '支出'
