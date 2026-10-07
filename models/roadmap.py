from datetime import datetime, timezone
from models import db

class RoadmapItem(db.Model):
    __tablename__ = 'roadmap_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    year = db.Column(db.Integer, default=1, nullable=False)
    month = db.Column(db.Integer, default=1, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True, index=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True, index=True)
    target_date = db.Column(db.String(50), nullable=True)
    estimated_study_time = db.Column(db.String(50), default='5 hours', nullable=False)
    priority = db.Column(db.String(20), default='medium', nullable=False)  # 'high', 'medium', 'low'
    order_index = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'year': self.year,
            'month': self.month,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_title': self.topic.title if self.topic else None,
            'lesson_id': self.lesson_id,
            'target_date': self.target_date,
            'estimated_study_time': self.estimated_study_time,
            'priority': self.priority,
            'order_index': self.order_index,
            'is_active': self.is_active
        }
