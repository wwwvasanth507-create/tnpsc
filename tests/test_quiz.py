import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
from models import db, User, Subject, Topic, Question, QuizSet, QuizQuestion, QuizAttempt, QuizAnswer, MistakeQuestion

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def quiz_setup():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create student user
            student = User(username='quizstudent', email='qs@tnpsc2a.org', full_name='Quiz Aspirant', role='student')
            student.set_password('pass123')
            db.session.add(student)

            # Create Subject, Topic, Question, QuizSet
            sub = Subject(name='Polity Test', code='POL_TEST')
            db.session.add(sub)
            db.session.commit()

            top = Topic(subject_id=sub.id, title='Const Test')
            db.session.add(top)
            db.session.commit()

            q1 = Question(
                subject_id=sub.id, topic_id=top.id,
                question_text='Question 1?',
                option_a='A1', option_b='B1', option_c='C1', option_d='D1',
                correct_option='A', explanation='Exp 1'
            )
            q2 = Question(
                subject_id=sub.id, topic_id=top.id,
                question_text='Question 2?',
                option_a='A2', option_b='B2', option_c='C2', option_d='D2',
                correct_option='C', explanation='Exp 2'
            )
            db.session.add_all([q1, q2])
            db.session.commit()

            qz = QuizSet(title='Sample Quiz', subject_id=sub.id, topic_id=top.id, time_limit_minutes=10, pass_percentage=50.0)
            db.session.add(qz)
            db.session.commit()

            qq1 = QuizQuestion(quiz_set_id=qz.id, question_id=q1.id, order_index=1)
            qq2 = QuizQuestion(quiz_set_id=qz.id, question_id=q2.id, order_index=2)
            db.session.add_all([qq1, qq2])
            db.session.commit()

            yield {
                'client': client,
                'student_id': student.id,
                'quiz_id': qz.id,
                'q1_id': q1.id,
                'q2_id': q2.id
            }

        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_quiz_submission_and_score_calculation(quiz_setup):
    client = quiz_setup['client']
    quiz_id = quiz_setup['quiz_id']
    q1_id = quiz_setup['q1_id']
    q2_id = quiz_setup['q2_id']

    # Login student
    client.post('/auth/login', data={'identifier': 'quizstudent', 'password': 'pass123'})

    # Submit answers: q1 correct ('A'), q2 wrong ('B' instead of 'C')
    res = client.post(f'/quizzes/{quiz_id}/submit', json={
        'answers': {
            str(q1_id): 'A',
            str(q2_id): 'B'
        }
    })

    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['correct_count'] == 1
    assert data['wrong_count'] == 1
    assert data['percentage'] == 50.0

    # Verify QuizAttempt DB record
    attempt = db.session.get(QuizAttempt, data['attempt_id'])
    assert attempt is not None
    assert attempt.percentage == 50.0

    # Verify MistakeQuestion DB record created for q2
    mistake = MistakeQuestion.query.filter_by(question_id=q2_id, is_resolved=False).first()
    assert mistake is not None
    assert mistake.user_wrong_option == 'B'
