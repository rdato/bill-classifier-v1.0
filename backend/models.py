"""
数据模型
"""
from datetime import datetime
from database import db


class Record(db.Model):
    """交易记录模型"""
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), default='其他支出')
    merchant = db.Column(db.String(200))
    description = db.Column(db.String(500))
    amount = db.Column(db.Float, default=0.0)
    type = db.Column(db.String(20), default='支出')
    source = db.Column(db.String(50))
    confidence = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date,
            'category': self.category,
            'merchant': self.merchant or '',
            'description': self.description or '',
            'amount': self.amount,
            'type': self.type,
            'source': self.source or '',
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UploadSession(db.Model):
    """上传会话模型"""
    __tablename__ = 'upload_sessions'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    file_type = db.Column(db.String(50))
    record_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'record_count': self.record_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
