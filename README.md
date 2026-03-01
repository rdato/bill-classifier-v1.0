# 账单分类工具 Web 版

一个基于 Flask + Vue 3 的个人账单管理工具，支持支付宝、微信、银行账单的自动解析和智能分类。

## 功能特性

- 📁 支持多种账单格式：支付宝、微信、银行账单 (xlsx/xls/csv)
- 🏷️ 智能分类：基于关键词匹配自动分类交易记录
- ✏️ 手动调整：支持手动修改分类结果
- 📊 统计汇总：按类别统计支出/收入情况
- 📥 数据导出：导出分类后的 Excel 文件

## 项目结构

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
└── outputs/                    # 导出文件目录
```

## 快速开始

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

## API 接口

| 接口 | 方法 | 功能 |
|-----|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/upload` | POST | 上传账单文件 |
| `/api/records` | GET | 获取交易记录列表 |
| `/api/records/<id>` | PUT | 更新单条记录 |
| `/api/classify` | POST | 批量重新分类 |
| `/api/categories` | GET | 获取分类列表 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/export` | GET | 导出 Excel |
| `/api/clear` | POST | 清空所有数据 |

## 支持的分类

- 旅行
- 住房相关
- 餐饮
- 汽车
- 日用百货
- 备婚
- 人情
- 交通
- 数码电器
- 文化休闲
- 服饰
- 通讯
- 家居家装
- 水电燃气费
- 医疗
- 美妆护肤
- 运动户外
- 学习
- 其他支出

## 技术栈

- **后端**: Flask, Flask-SQLAlchemy, openpyxl
- **前端**: Vue 3, Element Plus, Vite
- **数据库**: SQLite

## 许可证

MIT License
