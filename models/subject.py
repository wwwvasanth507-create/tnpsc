from datetime import datetime, timezone
from models import db

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='book')
    order_index = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    topics = db.relationship('Topic', backref='subject', lazy='select', cascade='all, delete-orphan', order_by='Topic.order_index')
    questions = db.relationship('Question', backref='subject', lazy='select')
    quiz_sets = db.relationship('QuizSet', backref='subject', lazy='select')
    roadmap_items = db.relationship('RoadmapItem', backref='subject', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'icon': self.icon,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'topics_count': len(self.topics)
        }
