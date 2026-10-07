from datetime import datetime, timezone
from models import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    explanation = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='medium', nullable=False)  # 'easy', 'medium', 'hard'
    marks = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    quiz_questions = db.relationship('QuizQuestion', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    quiz_answers = db.relationship('QuizAnswer', backref='question', lazy='dynamic')
    mistakes = db.relationship('MistakeQuestion', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'topic_id': self.topic_id,
            'topic_title': self.topic.title if self.topic else '',
            'question_text': self.question_text,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'correct_option': self.correct_option,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'marks': self.marks,
            'is_active': self.is_active
        }
