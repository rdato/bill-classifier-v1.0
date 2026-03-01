"""
关键词匹配分类器
"""
import json
import os
from typing import Dict, List, Optional, Tuple


class KeywordMatcher:
    """基于关键词的分类匹配器"""

    # 默认分类
    DEFAULT_CATEGORY = '其他支出'

    # 预定义的分类关键词库
    DEFAULT_KEYWORDS = {
        '旅行': [
            '机票', '航空', '酒店', '民宿', '宾馆', '旅馆', '旅游', '旅行社', '景点', '门票',
            '火车票', '高铁', '动车', '携程', '去哪儿', '飞猪', '马蜂窝', '途牛',
            '租车', '接机', '送机', '签证', '护照', '行李', '景区', '乐园', '度假'
        ],
        '住房相关': [
            '房租', '物业', '维修', '装修', '中介', '房产', '房屋', '住房', '住宅',
            '押金', '水电', '宽带', '燃气', '暖气', '保洁', '开锁', '换锁'
        ],
        '餐饮': [
            '外卖', '美团', '饿了么', '肯德基', '麦当劳', '星巴克', '瑞幸', '奶茶',
            '餐厅', '饭店', '食堂', '小吃', '美食', '火锅', '烧烤', '日料', '西餐',
            '早餐', '午餐', '晚餐', '夜宵', '饮品', '咖啡', '蛋糕', '面包', '甜品',
            '食材', '蔬菜', '水果', '肉类', '海鲜'
        ],
        '汽车': [
            '加油', '中石化', '中石油', '壳牌', '停车', '洗车', '保养', '维修', '4S',
            '过路费', '高速', 'ETC', '违章', '罚款', '车险', '车检', '代驾', '滴滴',
            '汽车', '汽配', '轮胎', '机油', '刹车', '车饰', '车载'
        ],
        '日用百货': [
            '超市', '便利店', '百货', '商场', '购物中心', '沃尔玛', '家乐福', '大润发',
            '永辉', '华润', '盒马', '日用品', '洗涤', '清洁', '纸巾', '洗护', '卫生'
        ],
        '备婚': [
            '婚纱', '婚庆', '婚礼', '婚宴', '结婚', '钻石', '戒指', '首饰', '彩礼',
            '婚戒', '喜糖', '请柬', '婚照', '摄影', '跟拍', '司仪', '化妆', '婚车'
        ],
        '人情': [
            '红包', '礼金', '份子钱', '随礼', '请客', '送礼', '生日礼物', '节日礼物',
            '结婚礼金', '满月酒', '祝寿', '探病', '慰问', '感谢', '人情'
        ],
        '交通': [
            '打车', '滴滴', '网约车', '出租车', '公交', '地铁', '共享单车', '单车',
            '哈啰', '摩拜', '青桔', '高德打车', 'T3出行', '曹操出行',
            '火车票', '汽车票', '客运站', '轮渡'
        ],
        '数码电器': [
            '手机', '电脑', '笔记本', '平板', 'iPad', 'iPhone', '华为', '小米', 'OPPO',
            'vivo', '联想', '戴尔', '惠普', '苹果', '耳机', '音箱', '键盘', '鼠标',
            '显示器', '电视', '冰箱', '洗衣机', '空调', '京东', '天猫', '苏宁'
        ],
        '文化休闲': [
            '电影', '影院', '演出', '演唱会', '音乐会', '话剧', '展览', '博物馆',
            '游戏', 'Steam', 'Nintendo', '书籍', '图书', '书店', '阅读', 'Kindle',
            '会员', 'VIP', '爱奇艺', '优酷', '腾讯视频', 'B站', '哔哩哔哩', 'Netflix'
        ],
        '服饰': [
            '衣服', '服装', '鞋', '包', '帽子', '围巾', '手套', '袜子', '皮带',
            '淘宝', '天猫', '唯品会', '得物', '优衣库', 'ZARA', 'H&M',
            '耐克', '阿迪达斯', '李宁', '安踏', '特步'
        ],
        '通讯': [
            '话费', '充值', '流量', '移动', '联通', '电信', '手机卡', '宽带',
            '通讯', '短信', '套餐', '漫游', '固话'
        ],
        '家居家装': [
            '家具', '沙发', '床', '床垫', '桌椅', '衣柜', '书柜', '电视柜',
            '装修', '建材', '涂料', '地板', '瓷砖', '门窗', '吊顶',
            '灯具', '灯泡', '开关', '插座', '窗帘', '地毯'
        ],
        '水电燃气费': [
            '水费', '电费', '燃气费', '天然气', '自来水', '供电', '供电局', '水务',
            '燃气公司', '公用事业', '能源费'
        ],
        '医疗': [
            '医院', '诊所', '药店', '药房', '挂号', '门诊', '住院', '手术',
            '体检', '检查', '化验', '药品', '治疗', '牙科', '眼科', '医保'
        ],
        '美妆护肤': [
            '化妆品', '护肤', '面膜', '口红', '粉底', '眼影', '眉笔', '睫毛',
            '香水', '防晒', '洁面', '爽肤水', '乳液', '精华', '面霜', '眼霜',
            '美容', '美甲', '美睫', 'SPA', '屈臣氏', '丝芙兰'
        ],
        '运动户外': [
            '健身', '健身房', '运动', '瑜伽', '跑步', '游泳', '羽毛球', '篮球',
            '足球', '乒乓球', '网球', '高尔夫', '骑行', '登山', '露营', '户外',
            '运动服', '运动鞋', '健身器材', '哑铃', '跑步机', '瑜伽垫'
        ],
        '学习': [
            '培训', '课程', '学习', '教育', '考试', '报名费', '学费', '书费',
            '在线教育', '网课', '付费课程', '知识付费', '得到', '知乎', '喜马拉雅',
            '英语', '编程', '考研', '考公', '证书', '职业技能'
        ],
        '其他支出': []
    }

    def __init__(self, keywords_file: Optional[str] = None):
        self.keywords = self.DEFAULT_KEYWORDS.copy()

        # 尝试加载默认关键词文件
        default_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'keywords.json')
        default_file = os.path.abspath(default_file)
        if os.path.exists(default_file):
            self._load_keywords(default_file)

        # 加载用户指定的关键词文件
        if keywords_file and os.path.exists(keywords_file):
            self._load_keywords(keywords_file)

    def _load_keywords(self, file_path: str):
        """加载自定义关键词库"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_keywords = json.load(f)
                for category, words in custom_keywords.items():
                    if category in self.keywords:
                        self.keywords[category] = list(set(self.keywords[category] + words))
                    else:
                        self.keywords[category] = words
        except Exception as e:
            print(f"加载关键词库失败: {e}")

    def classify(self, description: str, merchant: str = '') -> Tuple[str, float]:
        """对交易进行分类"""
        text = f"{description} {merchant}".lower()

        best_match = self.DEFAULT_CATEGORY
        best_score = 0

        for category, keywords in self.keywords.items():
            if not keywords:
                continue

            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += len(keyword)

            if score > best_score:
                best_score = score
                best_match = category

        confidence = min(best_score / 100, 1.0) if best_score > 0 else 0.0
        return best_match, confidence

    def classify_records(self, records: List[Dict]) -> List[Dict]:
        """对记录列表进行分类"""
        for record in records:
            description = record.get('description', '')
            merchant = record.get('merchant', '')
            category, confidence = self.classify(description, merchant)
            record['category'] = category
            record['confidence'] = confidence
        return records

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return list(self.keywords.keys())
