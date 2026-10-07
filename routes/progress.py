from flask import Blueprint, render_template, session
from sqlalchemy import func
from models import db, Subject, Topic, Lesson, StudentProgress, QuizAttempt, QuizAnswer, Question
from routes import login_required

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

@progress_bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')

    # Subject performance & completion breakdown
    subjects = Subject.query.filter_by(is_active=True).order_by(Subject.order_index.asc()).all()
    subject_stats = []

    for sub in subjects:
        total_lessons = Lesson.query.join(Topic).filter(Topic.subject_id == sub.id, Lesson.is_active == True).count()
        completed_lessons = StudentProgress.query.join(Lesson).join(Topic)\
            .filter(Topic.subject_id == sub.id, StudentProgress.user_id == user_id, StudentProgress.status == 'completed')\
            .count()
        
        # Accuracy calculation per subject
        subject_answers = QuizAnswer.query.join(Question).join(QuizAttempt)\
            .filter(Question.subject_id == sub.id, QuizAttempt.user_id == user_id).all()
        
        total_ans = len(subject_answers)
        correct_ans = sum(1 for a in subject_answers if a.is_correct)
        accuracy = round((correct_ans / total_ans * 100), 1) if total_ans > 0 else 0.0

        lesson_pct = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0.0

        subject_stats.append({
            'subject': sub,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'lesson_pct': lesson_pct,
            'total_ans': total_ans,
            'correct_ans': correct_ans,
            'accuracy': accuracy
        })

    # Global accuracy & metrics
    all_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    total_quizzes = len(all_attempts)
    total_q_attempted = sum(a.total_questions for a in all_attempts)
    total_q_correct = sum(a.correct_count for a in all_attempts)
    overall_accuracy = round((total_q_correct / total_q_attempted * 100), 1) if total_q_attempted > 0 else 0.0

    return render_template(
        'student/progress.html',
        subject_stats=subject_stats,
        total_quizzes=total_quizzes,
        total_q_attempted=total_q_attempted,
        total_q_correct=total_q_correct,
        overall_accuracy=overall_accuracy
    )
