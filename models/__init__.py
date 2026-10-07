from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.subject import Subject
from models.topic import Topic
from models.lesson import Lesson
from models.question import Question
from models.quiz import QuizSet, QuizQuestion, QuizAttempt, QuizAnswer
from models.progress import StudentProgress, StudentTopicProgress, Bookmark, MistakeQuestion
from models.roadmap import RoadmapItem
from models.audit_log import AuditLog

__all__ = [
    'db',
    'User',
    'Subject',
    'Topic',
    'Lesson',
    'Question',
    'QuizSet',
    'QuizQuestion',
    'QuizAttempt',
    'QuizAnswer',
    'StudentProgress',
    'StudentTopicProgress',
    'Bookmark',
    'MistakeQuestion',
    'RoadmapItem',
    'AuditLog'
]
