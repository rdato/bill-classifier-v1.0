"""
规则引擎 - 支持正则表达式匹配
"""
import re
from typing import Dict, List, Optional, Tuple


class Rule:
    """分类规则"""

    def __init__(self, category: str, pattern: str, rule_type: str = 'regex'):
        self.category = category
        self.pattern = pattern
        self.rule_type = rule_type

        if rule_type == 'regex':
            try:
                self._compiled = re.compile(pattern, re.IGNORECASE)
            except re.error:
                self._compiled = None
        else:
            self._compiled = None

    def match(self, text: str) -> bool:
        """检查文本是否匹配规则"""
        if not text:
            return False

        text = str(text)

        if self.rule_type == 'regex' and self._compiled:
            return bool(self._compiled.search(text))
        elif self.rule_type == 'exact':
            return text.strip() == self.pattern.strip()
        elif self.rule_type == 'contains':
            return self.pattern.lower() in text.lower()

        return False


class RuleEngine:
    """规则引擎"""

    DEFAULT_RULES = [
        Rule('餐饮', r'美团外卖|饿了么|.*外卖.*', 'regex'),
        Rule('餐饮', r'肯德基|麦当劳|KFC|.*汉堡.*', 'regex'),
        Rule('餐饮', r'星巴克|瑞幸|.*咖啡.*', 'regex'),
        Rule('交通', r'滴滴|.*打车.*|网约车', 'regex'),
        Rule('交通', r'地铁|公交|.*出行.*', 'regex'),
        Rule('交通', r'哈啰|.*单车.*|共享单车', 'regex'),
        Rule('汽车', r'加油|中石化|中石油|壳牌', 'regex'),
        Rule('汽车', r'停车|.*停车场.*', 'regex'),
        Rule('汽车', r'ETC|高速费|过路费', 'regex'),
        Rule('服饰', r'淘宝|天猫|唯品会|得物', 'regex'),
        Rule('数码电器', r'京东|苏宁|国美', 'regex'),
        Rule('文化休闲', r'电影|影院|.*票务.*', 'regex'),
        Rule('文化休闲', r'爱奇艺|腾讯视频|优酷|B站|哔哩哔哩', 'regex'),
        Rule('通讯', r'话费|充值|移动|联通|电信', 'regex'),
        Rule('医疗', r'医院|药店|挂号|体检', 'regex'),
        Rule('学习', r'培训|课程|.*教育.*|网课', 'regex'),
    ]

    def __init__(self):
        self.rules: List[Rule] = self.DEFAULT_RULES.copy()
        self.custom_rules: List[Rule] = []

    def add_rule(self, category: str, pattern: str, rule_type: str = 'regex'):
        rule = Rule(category, pattern, rule_type)
        self.custom_rules.append(rule)

    def classify(self, description: str, merchant: str = '') -> Optional[str]:
        """使用规则进行分类"""
        text = f"{description} {merchant}"

        for rule in self.custom_rules:
            if rule.match(text):
                return rule.category

        for rule in self.rules:
            if rule.match(text):
                return rule.category

        return None

    def classify_records(self, records: List[Dict]) -> List[Dict]:
        """对记录列表进行分类"""
        for record in records:
            description = record.get('description', '')
            merchant = record.get('merchant', '')
            rule_category = self.classify(description, merchant)
            record['rule_category'] = rule_category

            # 如果规则匹配，使用规则的分类
            if rule_category:
                record['category'] = rule_category

        return records
