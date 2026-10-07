import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
from models import db, User, Subject, Topic, Lesson, Question, AuditLog

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def client_with_admin():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            admin = User(username='admin', email='admin@tnpsc2a.org', full_name='Admin User', role='admin')
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.commit()

        # Login as admin
        client.post('/auth/login', data={'identifier': 'admin', 'password': 'adminpass'})
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_subject_crud(client_with_admin):
    # Create Subject
    res = client_with_admin.post('/admin/subjects', data={
        'name': 'History of India',
        'code': 'HIST',
        'description': 'Ancient, Medieval and Modern Indian History.',
        'order_index': 1
    }, follow_redirects=True)
    assert res.status_code == 200

    sub = Subject.query.filter_by(code='HIST').first()
    assert sub is not None
    assert sub.name == 'History of India'

    # Audit log check
    log = AuditLog.query.filter_by(action='CREATE_SUBJECT').first()
    assert log is not None

    # Delete Subject
    res_del = client_with_admin.post(f'/admin/subjects/{sub.id}/delete', follow_redirects=True)
    assert res_del.status_code == 200
    assert db.session.get(Subject, sub.id) is None

def test_topic_lesson_question_crud(client_with_admin):
    # Create Subject
    sub = Subject(name='Geog', code='GEOG', order_index=1)
    db.session.add(sub)
    db.session.commit()

    # Create Topic
    res_t = client_with_admin.post('/admin/topics', data={
        'subject_id': sub.id,
        'title': 'Physical Geography',
        'description': 'Landforms & Rivers',
        'order_index': 1
    }, follow_redirects=True)
    assert res_t.status_code == 200
    top = Topic.query.filter_by(title='Physical Geography').first()
    assert top is not None

    # Create Lesson
    res_l = client_with_admin.post('/admin/lessons', data={
        'topic_id': top.id,
        'title': 'Rivers of Tamil Nadu',
        'content_summary': 'Major rivers system',
        'concept_body': '<p>Cauvery, Vaigai, Thamirabarani</p>',
        'examples': 'River basins',
        'important_points': 'Cauvery originates at Talakaveri',
        'memory_tricks': 'CVT mnemonic',
        'estimated_minutes': 15,
        'order_index': 1
    }, follow_redirects=True)
    assert res_l.status_code == 200
    les = Lesson.query.filter_by(title='Rivers of Tamil Nadu').first()
    assert les is not None

    # Create Question
    res_q = client_with_admin.post('/admin/questions', data={
        'subject_id': sub.id,
        'topic_id': top.id,
        'question_text': 'Where does the Cauvery river originate?',
        'option_a': 'Talakaveri',
        'option_b': 'Agastya Mala',
        'option_c': 'Anamudi',
        'option_d': 'Mahabaleshwar',
        'correct_option': 'A',
        'explanation': 'Originates at Talakaveri in Coorg.',
        'difficulty': 'easy',
        'marks': 1
    }, follow_redirects=True)
    assert res_q.status_code == 200
    q = Question.query.filter_by(subject_id=sub.id).first()
    assert q is not None
    assert q.correct_option == 'A'
