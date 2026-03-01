# 🧾 账单分类工具 Web 版

一个基于 Flask + Vue 3 的个人账单管理工具，支持支付宝、微信、银行账单的自动解析和智能分类。

## ✨ 功能特点

- 📁 **多平台支持** - 支持支付宝、微信、银行账单格式 (xlsx/xls/csv)
- 🔍 **自动识别** - 智能识别文件来源，无需手动选择
- 🏷️ **智能分类** - 基于19个预定义类别自动分类交易记录
- ✏️ **手动调整** - 支持手动修改分类结果
- 📊 **分类汇总** - 按类别统计支出/收入情况
- 📥 **Excel导出** - 导出标准化的 Excel 报表（含分类汇总和明细）
- 🌐 **Web界面** - 清新淡雅的 Web UI，支持手机和电脑访问
- 🔒 **本地运行** - 数据本地存储，保护隐私安全

## 🚀 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 http://localhost:5000 运行。

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务将在 http://localhost:3000 运行。

### 5. 访问应用

打开浏览器访问 http://localhost:3000

## 📂 支持的账单格式

| 平台 | 格式 | 说明 |
|-----|------|------|
| 支付宝 | .csv/.xlsx | 支付宝导出的交易明细 |
| 微信 | .xlsx | 微信支付导出的账单流水 |
| 银行 | .xlsx/.csv | 各银行导出的交易记录 |

## 🏷️ 分类类别

| 类别 | 说明 | 类别 | 说明 |
|-----|------|-----|------|
| 🧳 旅行 | 机票、酒店、门票 | 🏠 住房相关 | 房租、物业费 |
| 🍜 餐饮 | 外卖、餐厅、食材 | 🚗 汽车 | 加油、停车、保养 |
| 🛒 日用百货 | 超市、日用品 | 💒 备婚 | 婚庆相关支出 |
| 🧧 人情 | 红包、礼金 | 🚌 交通 | 打车、公交、地铁 |
| 📱 数码电器 | 手机、电脑、家电 | 🎬 文化休闲 | 电影、游戏、书籍 |
| 👔 服饰 | 服装、鞋帽 | 📞 通讯 | 话费、宽带 |
| 🛋️ 家居家装 | 家具、装修 | 💡 水电燃气费 | 水费、电费、燃气费 |
| 💊 医疗 | 药品、挂号费 | 💄 美妆护肤 | 化妆品、护肤品 |
| 🏃 运动户外 | 健身、运动装备 | 📚 学习 | 课程、培训 |
| ❓ 其他支出 | 无法归类的支出 | | |

## 📁 项目结构

```
bill-classifier-web/
├── backend/                    # 后端 (Flask)
│   ├── app.py                  # Flask 主程序
│   ├── models.py               # 数据模型
│   ├── database.py             # 数据库配置
│   ├── requirements.txt        # Python 依赖
│   └── core/                   # 核心模块
│       ├── parsers/            # 文件解析器
│       ├── classifier/         # 分类引擎
│       ├── exporter/           # 导出模块
│       └── data/               # 关键词库
│
├── frontend/                   # 前端 (Vue 3)
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API 调用
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
│
├── uploads/                    # 上传文件临时目录
├── outputs/                    # 导出文件目录
└── README.md
```

## 🔧 API 接口

| 接口 | 方法 | 功能 |
|-----|------|------|
| `/api/upload` | POST | 上传账单文件 |
| `/api/records` | GET | 获取交易记录列表 |
| `/api/records/<id>` | PUT | 更新单条记录分类 |
| `/api/categories` | GET | 获取分类列表 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/export` | GET | 导出 Excel |
| `/api/clear` | POST | 清空所有数据 |

## ⚙️ 技术栈

- **后端**: Flask, Flask-SQLAlchemy, openpyxl
- **前端**: Vue 3, Element Plus, Vite
- **数据库**: SQLite

## 📄 许可证

[MIT License](LICENSE)

---

如果这个项目对你有帮助，欢迎 ⭐ Star 支持！
