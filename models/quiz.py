from datetime import datetime, timezone
from models import db

class QuizSet(db.Model):
    __tablename__ = 'quiz_sets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True, index=True)
    time_limit_minutes = db.Column(db.Integer, default=15, nullable=False)
    pass_percentage = db.Column(db.Float, default=50.0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz_set', lazy='select', cascade='all, delete-orphan', order_by='QuizQuestion.order_index')
    attempts = db.relationship('QuizAttempt', backref='quiz_set', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_title': self.topic.title if self.topic else None,
            'time_limit_minutes': self.time_limit_minutes,
            'pass_percentage': self.pass_percentage,
            'is_active': self.is_active,
            'questions_count': len(self.questions)
        }

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_set_id = db.Column(db.Integer, db.ForeignKey('quiz_sets.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    order_index = db.Column(db.Integer, default=0, nullable=False)

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quiz_set_id = db.Column(db.Integer, db.ForeignKey('quiz_sets.id'), nullable=False, index=True)
    score = db.Column(db.Float, default=0.0, nullable=False)
    total_questions = db.Column(db.Integer, default=0, nullable=False)
    correct_count = db.Column(db.Integer, default=0, nullable=False)
    wrong_count = db.Column(db.Integer, default=0, nullable=False)
    percentage = db.Column(db.Float, default=0.0, nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    answers = db.relationship('QuizAnswer', backref='attempt', lazy='select', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_set_id': self.quiz_set_id,
            'quiz_title': self.quiz_set.title if self.quiz_set else '',
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'percentage': self.percentage,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    selected_option = db.Column(db.String(1), nullable=True)  # 'A', 'B', 'C', 'D' or None if un-answered
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
