from datetime import datetime, timezone
from models import db

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lessons = db.relationship('Lesson', backref='topic', lazy='select', cascade='all, delete-orphan', order_by='Lesson.order_index')
    questions = db.relationship('Question', backref='topic', lazy='select')
    quiz_sets = db.relationship('QuizSet', backref='topic', lazy='select')
    roadmap_items = db.relationship('RoadmapItem', backref='topic', lazy='select')
    topic_progress_records = db.relationship('StudentTopicProgress', backref='topic', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'lessons_count': len(self.lessons)
        }
