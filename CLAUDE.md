# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

账单分类工具 Web 版 - 用于解析和自动分类支付宝、微信、银行账单的交易记录。

## 开发命令

```bash
# 安装后端依赖
cd backend && pip install -r requirements.txt

# 后端开发 (端口 5000)
cd backend && python app.py

# 前端开发 (端口 3000，自动代理到后端)
cd frontend && npm run dev

# 前端构建
cd frontend && npm run build

# 生产环境启动
cd backend && gunicorn -c gunicorn.conf.py wsgi:app
```

## 技术栈

- **后端**: Python 3.12 + Flask + Flask-SQLAlchemy (SQLite)
- **前端**: Vue 3 + Vite + Element Plus + Axios

## 架构

```
backend/
├── app.py              # Flask 主应用，所有 API 路由
├── database.py         # SQLAlchemy 配置
├── models.py           # 数据模型 (Record, UploadSession)
├── wsgi.py             # 生产环境入口
├── gunicorn.conf.py    # Gunicorn 配置
└── core/
    ├── parsers/        # 账单解析器 (BaseParser, AlipayParser, WechatParser, BankParser)
    ├── classifier/     # 分类器 (KeywordMatcher, RuleEngine)
    ├── exporter/       # Excel 导出器
    └── data/           # 关键词库 JSON

frontend/
├── src/
│   ├── main.js         # Vue 入口
│   ├── router.js       # 路由配置
│   ├── App.vue         # 根组件
│   ├── api/bill.js     # API 调用封装
│   └── views/          # 页面组件
└── vite.config.js      # Vite 配置 (代理 /api 到后端)
```

## 核心模块

### 解析器 (parsers)

- `BaseParser`: 基类，提供 Excel/CSV 读取、金额清理等通用方法
- `AlipayParser`, `WechatParser`, `BankParser`: 各平台解析器，通过 `can_parse()` 自动识别文件类型
- 解析后输出标准化字典: `{date, category, merchant, description, amount, type, source, raw_data}`

### 分类器 (classifier)

- `KeywordMatcher`: 基于关键词匹配分类，关键词库在 `backend/core/data/keywords.json`
- `RuleEngine`: 规则引擎，处理特殊情况
- 分类流程: 先关键词匹配，再规则引擎处理

### 数据模型

- `Record`: 交易记录 (date, category, merchant, description, amount, type, source, confidence, raw_data)
- `UploadSession`: 上传会话记录

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传账单文件 |
| `/api/records` | GET | 获取记录列表 (支持分页、筛选) |
| `/api/records/<id>` | PUT | 更新记录分类 |
| `/api/categories` | GET | 获取分类列表 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/export` | GET | 导出 Excel |
| `/api/export/original/<source>` | GET | 导出原始格式 CSV |
| `/api/clear` | POST | 清空所有记录 |

## 添加新解析器

1. 在 `backend/core/parsers/` 创建新解析器，继承 `BaseParser`
2. 实现 `can_parse()` 和 `parse()` 方法
3. 在 `backend/core/parsers/__init__.py` 导出
4. 在 `app.py` 的 `parsers` 列表中注册
