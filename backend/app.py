"""
账单分类工具 Web 版 - Flask 主程序
"""
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from database import db, init_db
from models import Record, UploadSession
from core.parsers import AlipayParser, WechatParser, BankParser
from core.classifier import KeywordMatcher, RuleEngine
from core.exporter import ExcelExporter

# 创建 Flask 应用
app = Flask(__name__)

# 配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "records.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, '..', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, '..', 'outputs')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大上传

# 启用 CORS
CORS(app)

# 初始化数据库
init_db(app)

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 初始化解析器和分类器
parsers = [AlipayParser(), WechatParser(), BankParser()]
keyword_matcher = KeywordMatcher(
    keywords_file=os.path.join(BASE_DIR, 'core', 'data', 'keywords.json')
)
rule_engine = RuleEngine()
exporter = ExcelExporter()

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_file_type(file_path):
    """检测文件类型"""
    for parser in parsers:
        if parser.can_parse(file_path):
            return parser
    return None


# ============== API 路由 ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传账单文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    try:
        # 保存文件 - 使用 uuid 作为文件名避免中文问题
        original_filename = file.filename
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'xlsx'
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(file_path)

        # 检测文件类型并解析
        parser = detect_file_type(file_path)
        if parser is None:
            os.remove(file_path)
            return jsonify({'error': '无法识别的账单格式，请上传支付宝、微信或银行账单'}), 400

        # 解析文件
        records = parser.parse(file_path)

        # 分类
        records = keyword_matcher.classify_records(records)
        records = rule_engine.classify_records(records)

        # 保存到数据库
        upload_session = UploadSession(
            filename=original_filename,
            file_type=parser.source_name,
            record_count=len(records)
        )
        db.session.add(upload_session)
        db.session.flush()

        for record in records:
            db_record = Record(
                date=record.get('date', ''),
                category=record.get('category', '其他支出'),
                merchant=record.get('merchant', ''),
                description=record.get('description', ''),
                amount=record.get('amount', 0),
                type=record.get('type', '支出'),
                source=record.get('source', ''),
                confidence=record.get('confidence', 0)
            )
            db.session.add(db_record)

        db.session.commit()

        return jsonify({
            'message': '上传成功',
            'filename': original_filename,
            'file_type': parser.source_name,
            'record_count': len(records),
            'session_id': upload_session.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'处理文件失败: {str(e)}'}), 500


@app.route('/api/records', methods=['GET'])
def get_records():
    """获取交易记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    category = request.args.get('category', '')
    trans_type = request.args.get('type', '')
    source = request.args.get('source', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query = Record.query

    if category:
        query = query.filter(Record.category == category)
    if trans_type:
        query = query.filter(Record.type == trans_type)
    if source:
        query = query.filter(Record.source == source)
    if start_date:
        query = query.filter(Record.date >= start_date)
    if end_date:
        query = query.filter(Record.date <= end_date)

    query = query.order_by(Record.date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'records': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@app.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """更新单条记录（修改分类）"""
    record = Record.query.get(record_id)
    if not record:
        return jsonify({'error': '记录不存在'}), 404

    data = request.get_json()
    if 'category' in data:
        record.category = data['category']
        record.confidence = 1.0  # 手动修改置信度为 1

    db.session.commit()
    return jsonify(record.to_dict())


@app.route('/api/classify', methods=['POST'])
def reclassify_records():
    """重新分类记录"""
    data = request.get_json()
    record_ids = data.get('ids', [])

    if not record_ids:
        return jsonify({'error': '请选择要重新分类的记录'}), 400

    records = Record.query.filter(Record.id.in_(record_ids)).all()
    updated = 0

    for record in records:
        category, confidence = keyword_matcher.classify(
            record.description or '',
            record.merchant or ''
        )
        record.category = category
        record.confidence = confidence
        updated += 1

    db.session.commit()
    return jsonify({'message': f'已更新 {updated} 条记录'})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    categories = keyword_matcher.get_categories()
    return jsonify({'categories': categories})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    from sqlalchemy import func

    # 总体统计
    total_expense = db.session.query(
        func.sum(Record.amount)
    ).filter(Record.type == '支出').scalar() or 0

    total_income = db.session.query(
        func.sum(Record.amount)
    ).filter(Record.type == '收入').scalar() or 0

    total_records = Record.query.count()

    # 按分类统计
    category_stats = db.session.query(
        Record.category,
        Record.type,
        func.sum(Record.amount).label('amount'),
        func.count(Record.id).label('count')
    ).group_by(Record.category, Record.type).all()

    categories = {}
    for stat in category_stats:
        cat = stat.category
        if cat not in categories:
            categories[cat] = {'expense': 0, 'income': 0, 'expense_count': 0, 'income_count': 0}

        if stat.type == '支出':
            categories[cat]['expense'] = stat.amount
            categories[cat]['expense_count'] = stat.count
        else:
            categories[cat]['income'] = stat.amount
            categories[cat]['income_count'] = stat.count

    # 按来源统计
    source_stats = db.session.query(
        Record.source,
        func.count(Record.id).label('count')
    ).group_by(Record.source).all()

    sources = {s.source: s.count for s in source_stats if s.source}

    return jsonify({
        'total_expense': total_expense,
        'total_income': total_income,
        'net_expense': total_expense - total_income,
        'total_records': total_records,
        'categories': categories,
        'sources': sources
    })


@app.route('/api/export', methods=['GET'])
def export_records():
    """导出 Excel 文件"""
    try:
        # 获取所有记录
        records = Record.query.order_by(Record.date.desc()).all()

        if not records:
            return jsonify({'error': '没有可导出的数据'}), 400

        # 转换为字典格式
        records_data = [r.to_dict() for r in records]

        # 生成导出文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'账单分类_{timestamp}.xlsx'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)

        exporter.export(records_data, output_path)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


@app.route('/api/clear', methods=['POST'])
def clear_records():
    """清空所有记录"""
    try:
        num_deleted = db.session.query(Record).delete()
        db.session.query(UploadSession).delete()
        db.session.commit()
        return jsonify({'message': f'已删除 {num_deleted} 条记录'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'清空失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
