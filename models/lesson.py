from datetime import datetime, timezone
from models import db

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content_summary = db.Column(db.Text, nullable=True)
    concept_body = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text, nullable=True)
    important_points = db.Column(db.Text, nullable=True)
    memory_tricks = db.Column(db.Text, nullable=True)
    estimated_minutes = db.Column(db.Integer, default=15, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    progress_records = db.relationship('StudentProgress', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')
    roadmap_items = db.relationship('RoadmapItem', backref='lesson', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'topic_title': self.topic.title if self.topic else '',
            'subject_name': self.topic.subject.name if (self.topic and self.topic.subject) else '',
            'title': self.title,
            'content_summary': self.content_summary,
            'concept_body': self.concept_body,
            'examples': self.examples,
            'important_points': self.important_points,
            'memory_tricks': self.memory_tricks,
            'estimated_minutes': self.estimated_minutes,
            'order_index': self.order_index,
            'is_active': self.is_active
        }
