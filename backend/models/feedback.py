from datetime import datetime, timezone
from models import db

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    priority = db.Column(db.String(50), nullable=True)
    summary = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'sentiment': self.sentiment,
            'category': self.category,
            'priority': self.priority,
            'summary': self.summary,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
