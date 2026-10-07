from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from sqlalchemy import func
from models import (
    db, User, Subject, Topic, Lesson, Question, QuizSet, QuizAttempt, QuizAnswer,
    StudentProgress, StudentTopicProgress, RoadmapItem, Bookmark, MistakeQuestion
)
from routes import login_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/')
@student_bp.route('/student/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Calculate completed lessons
    completed_lessons_count = StudentProgress.query.filter_by(user_id=user_id, status='completed').count()
    total_lessons_count = Lesson.query.filter_by(is_active=True).count()

    overall_prep_pct = 0.0
    if total_lessons_count > 0:
        overall_prep_pct = round((completed_lessons_count / total_lessons_count) * 100, 1)

    # Quiz statistics
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    questions_attempted = sum(a.total_questions for a in attempts)
    avg_score = 0.0
    if attempts:
        avg_score = round(sum(a.percentage for a in attempts) / len(attempts), 1)

    recent_attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.completed_at.desc()).limit(5).all()

    # Study streak calculation
    # Count consecutive days up to today with student activity
    progress_dates = db.session.query(
        func.date(StudentProgress.last_accessed_at)
    ).filter_by(user_id=user_id).distinct().order_by(func.date(StudentProgress.last_accessed_at).desc()).all()

    attempt_dates = db.session.query(
        func.date(QuizAttempt.completed_at)
    ).filter_by(user_id=user_id).filter(QuizAttempt.completed_at.isnot(None)).distinct().order_by(func.date(QuizAttempt.completed_at).desc()).all()

    all_activity_dates = set([d[0] for d in progress_dates if d[0]] + [d[0] for d in attempt_dates if d[0]])
    
    streak = 0
    today = datetime.now(timezone.utc).date()
    check_date = today

    if check_date in all_activity_dates or (check_date - timedelta(days=1)) in all_activity_dates:
        if check_date not in all_activity_dates:
            check_date = today - timedelta(days=1)
        while check_date in all_activity_dates:
            streak += 1
            check_date = check_date - timedelta(days=1)

    # Weak topics calculation (quiz questions wrong count per topic)
    weak_topics_query = db.session.query(
        Topic.id, Topic.title, Subject.name.label('subject_name'),
        func.count(QuizAnswer.id).label('wrong_count')
    ).join(Question, Question.topic_id == Topic.id)\
     .join(Subject, Topic.subject_id == Subject.id)\
     .join(QuizAnswer, QuizAnswer.question_id == Question.id)\
     .join(QuizAttempt, QuizAnswer.attempt_id == QuizAttempt.id)\
     .filter(QuizAttempt.user_id == user_id, QuizAnswer.is_correct == False)\
     .group_by(Topic.id, Topic.title, Subject.name)\
     .order_by(func.count(QuizAnswer.id).desc())\
     .limit(3).all()

    weak_topics = [
        {'id': wt.id, 'title': wt.title, 'subject': wt.subject_name, 'wrong_count': wt.wrong_count}
        for wt in weak_topics_query
    ]

    # Weak subjects calculation
    weak_subjects_query = db.session.query(
        Subject.id, Subject.name,
        func.count(QuizAnswer.id).label('wrong_count')
    ).join(Question, Question.subject_id == Subject.id)\
     .join(QuizAnswer, QuizAnswer.question_id == Question.id)\
     .join(QuizAttempt, QuizAnswer.attempt_id == QuizAttempt.id)\
     .filter(QuizAttempt.user_id == user_id, QuizAnswer.is_correct == False)\
     .group_by(Subject.id, Subject.name)\
     .order_by(func.count(QuizAnswer.id).desc())\
     .limit(3).all()

    weak_subjects = [
        {'id': ws.id, 'name': ws.name, 'wrong_count': ws.wrong_count}
        for ws in weak_subjects_query
    ]

    # Recommended next lesson
    completed_lesson_ids = [p.lesson_id for p in StudentProgress.query.filter_by(user_id=user_id, status='completed').all()]
    next_lesson = Lesson.query.filter(
        Lesson.is_active == True,
        ~Lesson.id.in_(completed_lesson_ids) if completed_lesson_ids else True
    ).order_by(Lesson.order_index.asc()).first()

    # Current roadmap item
    current_roadmap = RoadmapItem.query.filter_by(is_active=True).order_by(RoadmapItem.order_index.asc()).first()

    # Goals calculation
    daily_goal_target = 2
    weekly_goal_target = 10
    
    start_of_today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_today - timedelta(days=start_of_today.weekday())

    today_completed = StudentProgress.query.filter(
        StudentProgress.user_id == user_id,
        StudentProgress.status == 'completed',
        StudentProgress.last_accessed_at >= start_of_today
    ).count()

    week_completed = StudentProgress.query.filter(
        StudentProgress.user_id == user_id,
        StudentProgress.status == 'completed',
        StudentProgress.last_accessed_at >= start_of_week
    ).count()

    return render_template(
        'student/dashboard.html',
        user=user,
        overall_prep_pct=overall_prep_pct,
        completed_lessons_count=completed_lessons_count,
        total_lessons_count=total_lessons_count,
        questions_attempted=questions_attempted,
        avg_score=avg_score,
        streak=streak,
        recent_attempts=recent_attempts,
        weak_topics=weak_topics,
        weak_subjects=weak_subjects,
        next_lesson=next_lesson,
        current_roadmap=current_roadmap,
        today_completed=today_completed,
        daily_goal_target=daily_goal_target,
        week_completed=week_completed,
        weekly_goal_target=weekly_goal_target
    )

@student_bp.route('/student/roadmap')
@login_required
def roadmap():
    user_id = session.get('user_id')
    items = RoadmapItem.query.filter_by(is_active=True).order_by(RoadmapItem.year.asc(), RoadmapItem.month.asc(), RoadmapItem.order_index.asc()).all()
    
    # Group items by year and month
    grouped_roadmap = {}
    for item in items:
        yr = item.year
        mo = item.month
        if yr not in grouped_roadmap:
            grouped_roadmap[yr] = {}
        if mo not in grouped_roadmap[yr]:
            grouped_roadmap[yr][mo] = []
        grouped_roadmap[yr][mo].append(item)

    # Check progress per lesson in roadmap
    completed_lesson_ids = set([
        p.lesson_id for p in StudentProgress.query.filter_by(user_id=user_id, status='completed').all()
    ])

    return render_template(
        'student/roadmap.html',
        grouped_roadmap=grouped_roadmap,
        completed_lesson_ids=completed_lesson_ids
    )

@student_bp.route('/student/subjects')
@login_required
def subjects():
    user_id = session.get('user_id')
    active_subjects = Subject.query.filter_by(is_active=True).order_by(Subject.order_index.asc()).all()
    
    subject_data = []
    for sub in active_subjects:
        topics_count = len(sub.topics)
        total_lessons = sum(len(t.lessons) for t in sub.topics)
        completed_lessons = StudentProgress.query.join(Lesson).join(Topic)\
            .filter(Topic.subject_id == sub.id, StudentProgress.user_id == user_id, StudentProgress.status == 'completed')\
            .count()
        progress_pct = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0.0

        subject_data.append({
            'subject': sub,
            'topics_count': topics_count,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_pct': progress_pct
        })

    return render_template('student/subjects.html', subject_data=subject_data)

@student_bp.route('/student/topics/<int:subject_id>')
@login_required
def topics(subject_id):
    user_id = session.get('user_id')
    subject = Subject.query.get_or_404(subject_id)
    active_topics = Topic.query.filter_by(subject_id=subject_id, is_active=True).order_by(Topic.order_index.asc()).all()

    completed_lesson_ids = set([
        p.lesson_id for p in StudentProgress.query.filter_by(user_id=user_id, status='completed').all()
    ])

    return render_template(
        'student/topics.html',
        subject=subject,
        topics=active_topics,
        completed_lesson_ids=completed_lesson_ids
    )

@student_bp.route('/student/mistakes')
@login_required
def mistakes():
    user_id = session.get('user_id')
    unresolved_mistakes = MistakeQuestion.query.filter_by(user_id=user_id, is_resolved=False)\
        .order_by(MistakeQuestion.created_at.desc()).all()
    resolved_mistakes = MistakeQuestion.query.filter_by(user_id=user_id, is_resolved=True)\
        .order_by(MistakeQuestion.created_at.desc()).limit(10).all()

    return render_template(
        'student/mistakes.html',
        unresolved_mistakes=unresolved_mistakes,
        resolved_mistakes=resolved_mistakes
    )

@student_bp.route('/student/mistakes/<int:mistake_id>/resolve', methods=['POST'])
@login_required
def resolve_mistake(mistake_id):
    user_id = session.get('user_id')
    mistake = MistakeQuestion.query.filter_by(id=mistake_id, user_id=user_id).first_or_404()
    mistake.is_resolved = True
    db.session.commit()
    flash('Mistake marked as resolved!', 'success')
    return redirect(url_for('student.mistakes'))

@student_bp.route('/student/bookmarks')
@login_required
def bookmarks():
    user_id = session.get('user_id')
    user_bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.created_at.desc()).all()

    return render_template('student/bookmarks.html', bookmarks=user_bookmarks)

@student_bp.route('/student/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if full_name:
            user.full_name = full_name
            session['full_name'] = full_name

        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('student/profile.html', user=user)
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('student/profile.html', user=user)
            user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', user=user)
