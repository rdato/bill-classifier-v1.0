"""
配置管理模块
"""
import os
import json
import yaml
from typing import Dict, List, Any, Optional


class Config:
    """配置管理类"""

    DEFAULT_CONFIG = {
        'categories': [
            '旅行', '住房相关', '餐饮', '汽车', '日用百货',
            '备婚', '人情', '交通', '数码电器', '文化休闲',
            '服饰', '通讯', '家居家装', '水电燃气费', '医疗',
            '美妆护肤', '运动户外', '学习', '其他支出'
        ],
        'input_formats': ['xlsx', 'csv'],
        'output_format': 'xlsx',
        'default_category': '其他支出',
        'confidence_threshold': 0.5
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path

        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

    def _load_config(self, file_path: str):
        """加载配置文件"""
        try:
            _, ext = os.path.splitext(file_path)

            if ext.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)

            if user_config:
                self._merge_config(user_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    def _merge_config(self, user_config: Dict):
        """合并用户配置"""
        for key, value in user_config.items():
            if key in self.config:
                if isinstance(self.config[key], dict) and isinstance(value, dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
            else:
                self.config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value

    def get_categories(self) -> List[str]:
        """获取分类列表"""
        return self.config.get('categories', self.DEFAULT_CONFIG['categories'])

    def save(self, file_path: Optional[str] = None):
        """保存配置到文件"""
        path = file_path or self.config_path
        if not path:
            return

        _, ext = os.path.splitext(path)

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if ext.lower() in ['.yaml', '.yml']:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def to_dict(self) -> Dict:
        """转换为字典"""
        return self.config.copy()
