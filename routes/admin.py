from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import (
    db, User, Subject, Topic, Lesson, Question, QuizSet, QuizQuestion,
    QuizAttempt, RoadmapItem, AuditLog
)
from routes import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    admin_id = session.get('user_id')

    total_students = User.query.filter_by(role='student').count()
    active_students = User.query.filter_by(role='student', is_active=True).count()
    total_subjects = Subject.query.count()
    total_topics = Topic.query.count()
    total_lessons = Lesson.query.count()
    total_questions = Question.query.count()
    total_attempts = QuizAttempt.query.count()

    attempts = QuizAttempt.query.all()
    avg_quiz_score = round(sum(a.percentage for a in attempts) / len(attempts), 1) if attempts else 0.0

    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        active_students=active_students,
        total_subjects=total_subjects,
        total_topics=total_topics,
        total_lessons=total_lessons,
        total_questions=total_questions,
        total_attempts=total_attempts,
        avg_quiz_score=avg_quiz_score,
        recent_logs=recent_logs
    )

# ==================== SUBJECTS CRUD ====================
@admin_bp.route('/subjects', methods=['GET', 'POST'])
@admin_required
def subjects():
    admin_id = session.get('user_id')

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'book').strip()
        order_index = int(request.form.get('order_index', 0))

        if not name or not code:
            flash('Subject name and code are required.', 'danger')
            return redirect(url_for('admin.subjects'))

        existing = Subject.query.filter((Subject.name == name) | (Subject.code == code)).first()
        if existing:
            flash('Subject with this name or code already exists.', 'danger')
            return redirect(url_for('admin.subjects'))

        subject = Subject(name=name, code=code, description=description, icon=icon, order_index=order_index)
        db.session.add(subject)
        db.session.commit()

        AuditLog.log_action(admin_id, 'CREATE_SUBJECT', 'Subject', subject.id, f"Created subject '{name}' ({code})")
        flash('Subject created successfully!', 'success')
        return redirect(url_for('admin.subjects'))

    all_subjects = Subject.query.order_by(Subject.order_index.asc()).all()
    return render_template('admin/subjects.html', subjects=all_subjects)

@admin_bp.route('/subjects/<int:subject_id>/edit', methods=['POST'])
@admin_required
def edit_subject(subject_id):
    admin_id = session.get('user_id')
    subject = Subject.query.get_or_404(subject_id)

    subject.name = request.form.get('name', subject.name).strip()
    subject.code = request.form.get('code', subject.code).strip().upper()
    subject.description = request.form.get('description', subject.description).strip()
    subject.icon = request.form.get('icon', subject.icon).strip()
    subject.order_index = int(request.form.get('order_index', subject.order_index))
    subject.is_active = 'is_active' in request.form

    db.session.commit()
    AuditLog.log_action(admin_id, 'UPDATE_SUBJECT', 'Subject', subject.id, f"Updated subject '{subject.name}'")
    flash('Subject updated successfully!', 'success')
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    admin_id = session.get('user_id')
    subject = Subject.query.get_or_404(subject_id)
    name = subject.name

    db.session.delete(subject)
    db.session.commit()
    AuditLog.log_action(admin_id, 'DELETE_SUBJECT', 'Subject', subject_id, f"Deleted subject '{name}'")
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subjects'))

# ==================== TOPICS CRUD ====================
@admin_bp.route('/topics', methods=['GET', 'POST'])
@admin_required
def topics():
    admin_id = session.get('user_id')

    if request.method == 'POST':
        subject_id = int(request.form.get('subject_id'))
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        order_index = int(request.form.get('order_index', 0))

        if not title or not subject_id:
            flash('Topic title and subject selection are required.', 'danger')
            return redirect(url_for('admin.topics'))

        topic = Topic(subject_id=subject_id, title=title, description=description, order_index=order_index)
        db.session.add(topic)
        db.session.commit()

        AuditLog.log_action(admin_id, 'CREATE_TOPIC', 'Topic', topic.id, f"Created topic '{title}'")
        flash('Topic created successfully!', 'success')
        return redirect(url_for('admin.topics'))

    all_topics = Topic.query.order_by(Topic.subject_id.asc(), Topic.order_index.asc()).all()
    all_subjects = Subject.query.filter_by(is_active=True).all()
    return render_template('admin/topics.html', topics=all_topics, subjects=all_subjects)

@admin_bp.route('/topics/<int:topic_id>/edit', methods=['POST'])
@admin_required
def edit_topic(topic_id):
    admin_id = session.get('user_id')
    topic = Topic.query.get_or_404(topic_id)

    topic.subject_id = int(request.form.get('subject_id', topic.subject_id))
    topic.title = request.form.get('title', topic.title).strip()
    topic.description = request.form.get('description', topic.description).strip()
    topic.order_index = int(request.form.get('order_index', topic.order_index))
    topic.is_active = 'is_active' in request.form

    db.session.commit()
    AuditLog.log_action(admin_id, 'UPDATE_TOPIC', 'Topic', topic.id, f"Updated topic '{topic.title}'")
    flash('Topic updated successfully!', 'success')
    return redirect(url_for('admin.topics'))

@admin_bp.route('/topics/<int:topic_id>/delete', methods=['POST'])
@admin_required
def delete_topic(topic_id):
    admin_id = session.get('user_id')
    topic = Topic.query.get_or_404(topic_id)
    title = topic.title

    db.session.delete(topic)
    db.session.commit()
    AuditLog.log_action(admin_id, 'DELETE_TOPIC', 'Topic', topic_id, f"Deleted topic '{title}'")
    flash('Topic deleted successfully!', 'success')
    return redirect(url_for('admin.topics'))

# ==================== LESSONS CRUD ====================
@admin_bp.route('/lessons', methods=['GET', 'POST'])
@admin_required
def lessons():
    admin_id = session.get('user_id')

    if request.method == 'POST':
        topic_id = int(request.form.get('topic_id'))
        title = request.form.get('title', '').strip()
        content_summary = request.form.get('content_summary', '').strip()
        concept_body = request.form.get('concept_body', '').strip()
        examples = request.form.get('examples', '').strip()
        important_points = request.form.get('important_points', '').strip()
        memory_tricks = request.form.get('memory_tricks', '').strip()
        estimated_minutes = int(request.form.get('estimated_minutes', 15))
        order_index = int(request.form.get('order_index', 0))

        if not title or not topic_id or not concept_body:
            flash('Title, topic, and concept body are required.', 'danger')
            return redirect(url_for('admin.lessons'))

        lesson = Lesson(
            topic_id=topic_id,
            title=title,
            content_summary=content_summary,
            concept_body=concept_body,
            examples=examples,
            important_points=important_points,
            memory_tricks=memory_tricks,
            estimated_minutes=estimated_minutes,
            order_index=order_index
        )
        db.session.add(lesson)
        db.session.commit()

        AuditLog.log_action(admin_id, 'CREATE_LESSON', 'Lesson', lesson.id, f"Created lesson '{title}'")
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('admin.lessons'))

    all_lessons = Lesson.query.order_by(Lesson.topic_id.asc(), Lesson.order_index.asc()).all()
    all_topics = Topic.query.filter_by(is_active=True).all()
    return render_template('admin/lessons.html', lessons=all_lessons, topics=all_topics)

@admin_bp.route('/lessons/<int:lesson_id>/edit', methods=['POST'])
@admin_required
def edit_lesson(lesson_id):
    admin_id = session.get('user_id')
    lesson = Lesson.query.get_or_404(lesson_id)

    lesson.topic_id = int(request.form.get('topic_id', lesson.topic_id))
    lesson.title = request.form.get('title', lesson.title).strip()
    lesson.content_summary = request.form.get('content_summary', lesson.content_summary).strip()
    lesson.concept_body = request.form.get('concept_body', lesson.concept_body).strip()
    lesson.examples = request.form.get('examples', lesson.examples).strip()
    lesson.important_points = request.form.get('important_points', lesson.important_points).strip()
    lesson.memory_tricks = request.form.get('memory_tricks', lesson.memory_tricks).strip()
    lesson.estimated_minutes = int(request.form.get('estimated_minutes', lesson.estimated_minutes))
    lesson.order_index = int(request.form.get('order_index', lesson.order_index))
    lesson.is_active = 'is_active' in request.form

    db.session.commit()
    AuditLog.log_action(admin_id, 'UPDATE_LESSON', 'Lesson', lesson.id, f"Updated lesson '{lesson.title}'")
    flash('Lesson updated successfully!', 'success')
    return redirect(url_for('admin.lessons'))

@admin_bp.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@admin_required
def delete_lesson(lesson_id):
    admin_id = session.get('user_id')
    lesson = Lesson.query.get_or_404(lesson_id)
    title = lesson.title

    db.session.delete(lesson)
    db.session.commit()
    AuditLog.log_action(admin_id, 'DELETE_LESSON', 'Lesson', lesson_id, f"Deleted lesson '{title}'")
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('admin.lessons'))

# ==================== QUESTIONS CRUD ====================
@admin_bp.route('/questions', methods=['GET', 'POST'])
@admin_required
def questions():
    admin_id = session.get('user_id')

    if request.method == 'POST':
        subject_id = int(request.form.get('subject_id'))
        topic_id = int(request.form.get('topic_id'))
        question_text = request.form.get('question_text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_option = request.form.get('correct_option', 'A').strip().upper()
        explanation = request.form.get('explanation', '').strip()
        difficulty = request.form.get('difficulty', 'medium')
        marks = int(request.form.get('marks', 1))

        if not question_text or not option_a or not option_b or not option_c or not option_d:
            flash('Question text and all four options are required.', 'danger')
            return redirect(url_for('admin.questions'))

        question = Question(
            subject_id=subject_id,
            topic_id=topic_id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            explanation=explanation,
            difficulty=difficulty,
            marks=marks
        )
        db.session.add(question)
        db.session.commit()

        AuditLog.log_action(admin_id, 'CREATE_QUESTION', 'Question', question.id, f"Created question: '{question_text[:40]}...'")
        flash('Question created successfully!', 'success')
        return redirect(url_for('admin.questions'))

    all_questions = Question.query.order_by(Question.id.desc()).all()
    all_subjects = Subject.query.filter_by(is_active=True).all()
    all_topics = Topic.query.filter_by(is_active=True).all()
    return render_template('admin/questions.html', questions=all_questions, subjects=all_subjects, topics=all_topics)

@admin_bp.route('/questions/<int:question_id>/edit', methods=['POST'])
@admin_required
def edit_question(question_id):
    admin_id = session.get('user_id')
    question = Question.query.get_or_404(question_id)

    question.subject_id = int(request.form.get('subject_id', question.subject_id))
    question.topic_id = int(request.form.get('topic_id', question.topic_id))
    question.question_text = request.form.get('question_text', question.question_text).strip()
    question.option_a = request.form.get('option_a', question.option_a).strip()
    question.option_b = request.form.get('option_b', question.option_b).strip()
    question.option_c = request.form.get('option_c', question.option_c).strip()
    question.option_d = request.form.get('option_d', question.option_d).strip()
    question.correct_option = request.form.get('correct_option', question.correct_option).strip().upper()
    question.explanation = request.form.get('explanation', question.explanation).strip()
    question.difficulty = request.form.get('difficulty', question.difficulty)
    question.marks = int(request.form.get('marks', question.marks))
    question.is_active = 'is_active' in request.form

    db.session.commit()
    AuditLog.log_action(admin_id, 'UPDATE_QUESTION', 'Question', question.id, f"Updated question #{question.id}")
    flash('Question updated successfully!', 'success')
    return redirect(url_for('admin.questions'))

@admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    admin_id = session.get('user_id')
    question = Question.query.get_or_404(question_id)

    db.session.delete(question)
    db.session.commit()
    AuditLog.log_action(admin_id, 'DELETE_QUESTION', 'Question', question_id, f"Deleted question #{question_id}")
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.questions'))

# ==================== QUIZ SETS CRUD ====================
@admin_bp.route('/quizzes', methods=['GET', 'POST'])
@admin_required
def quizzes():
    admin_id = session.get('user_id')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject_id = request.form.get('subject_id')
        topic_id = request.form.get('topic_id')
        time_limit_minutes = int(request.form.get('time_limit_minutes', 15))
        pass_percentage = float(request.form.get('pass_percentage', 50.0))

        quiz_set = QuizSet(
            title=title,
            description=description,
            subject_id=int(subject_id) if subject_id else None,
            topic_id=int(topic_id) if topic_id else None,
            time_limit_minutes=time_limit_minutes,
            pass_percentage=pass_percentage
        )
        db.session.add(quiz_set)
        db.session.commit()

        AuditLog.log_action(admin_id, 'CREATE_QUIZ_SET', 'QuizSet', quiz_set.id, f"Created quiz set '{title}'")
        flash('Quiz set created successfully!', 'success')
        return redirect(url_for('admin.quizzes'))

    all_quizzes = QuizSet.query.order_by(QuizSet.id.desc()).all()
    all_subjects = Subject.query.filter_by(is_active=True).all()
    all_topics = Topic.query.filter_by(is_active=True).all()
    return render_template('admin/quizzes.html', quizzes=all_quizzes, subjects=all_subjects, topics=all_topics)

@admin_bp.route('/quizzes/<int:quiz_id>/edit', methods=['POST'])
@admin_required
def edit_quiz(quiz_id):
    admin_id = session.get('user_id')
    quiz = QuizSet.query.get_or_404(quiz_id)

    quiz.title = request.form.get('title', quiz.title).strip()
    quiz.description = request.form.get('description', quiz.description).strip()
    quiz.time_limit_minutes = int(request.form.get('time_limit_minutes', quiz.time_limit_minutes))
    quiz.pass_percentage = float(request.form.get('pass_percentage', quiz.pass_percentage))
    quiz.is_active = 'is_active' in request.form

    db.session.commit()
    AuditLog.log_action(admin_id, 'UPDATE_QUIZ_SET', 'QuizSet', quiz.id, f"Updated quiz set '{quiz.title}'")
    flash('Quiz set updated successfully!', 'success')
    return redirect(url_for('admin.quizzes'))

@admin_bp.route('/quizzes/<int:quiz_id>/delete', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    admin_id = session.get('user_id')
    quiz = QuizSet.query.get_or_404(quiz_id)
    title = quiz.title

    db.session.delete(quiz)
    db.session.commit()
    AuditLog.log_action(admin_id, 'DELETE_QUIZ_SET', 'QuizSet', quiz_id, f"Deleted quiz set '{title}'")
    flash('Quiz set deleted successfully!', 'success')
    return redirect(url_for('admin.quizzes'))

# ==================== ROADMAP CRUD ====================
@admin_bp.route('/roadmap', methods=['GET', 'POST'])
@admin_required
def roadmap():
    admin_id = session.get('user_id')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        year = int(request.form.get('year', 1))
        month = int(request.form.get('month', 1))
        subject_id = request.form.get('subject_id')
        topic_id = request.form.get('topic_id')
        lesson_id = request.form.get('lesson_id')
        target_date = request.form.get('target_date', '').strip()
        estimated_study_time = request.form.get('estimated_study_time', '5 hours').strip()
        priority = request.form.get('priority', 'medium')
        order_index = int(request.form.get('order_index', 0))

        item = RoadmapItem(
            title=title,
            description=description,
            year=year,
            month=month,
            subject_id=int(subject_id) if subject_id else None,
            topic_id=int(topic_id) if topic_id else None,
            lesson_id=int(lesson_id) if lesson_id else None,
            target_date=target_date,
            estimated_study_time=estimated_study_time,
            priority=priority,
            order_index=order_index
        )
        db.session.add(item)
        db.session.commit()

        AuditLog.log_action(admin_id, 'CREATE_ROADMAP_ITEM', 'RoadmapItem', item.id, f"Created roadmap item '{title}'")
        flash('Roadmap item created successfully!', 'success')
        return redirect(url_for('admin.roadmap'))

    items = RoadmapItem.query.order_by(RoadmapItem.year.asc(), RoadmapItem.month.asc(), RoadmapItem.order_index.asc()).all()
    all_subjects = Subject.query.filter_by(is_active=True).all()
    all_topics = Topic.query.filter_by(is_active=True).all()
    all_lessons = Lesson.query.filter_by(is_active=True).all()

    return render_template(
        'admin/roadmap.html',
        items=items,
        subjects=all_subjects,
        topics=all_topics,
        lessons=all_lessons
    )

@admin_bp.route('/roadmap/<int:item_id>/edit', methods=['POST'])
@admin_required
def edit_roadmap(item_id):
    admin_id = session.get('user_id')
    item = RoadmapItem.query.get_or_404(item_id)

    item.title = request.form.get('title', item.title).strip()
    item.description = request.form.get('description', item.description).strip()
    item.year = int(request.form.get('year', item.year))
    item.month = int(request.form.get('month', item.month))
    item.estimated_study_time = request.form.get('estimated_study_time', item.estimated_study_time).strip()
    item.priority = request.form.get('priority', item.priority)
    item.order_index = int(request.form.get('order_index', item.order_index))
    item.is_active = 'is_active' in request.form

    db.session.commit()
    AuditLog.log_action(admin_id, 'UPDATE_ROADMAP_ITEM', 'RoadmapItem', item.id, f"Updated roadmap item '{item.title}'")
    flash('Roadmap item updated successfully!', 'success')
    return redirect(url_for('admin.roadmap'))

@admin_bp.route('/roadmap/<int:item_id>/delete', methods=['POST'])
@admin_required
def delete_roadmap(item_id):
    admin_id = session.get('user_id')
    item = RoadmapItem.query.get_or_404(item_id)
    title = item.title

    db.session.delete(item)
    db.session.commit()
    AuditLog.log_action(admin_id, 'DELETE_ROADMAP_ITEM', 'RoadmapItem', item_id, f"Deleted roadmap item '{title}'")
    flash('Roadmap item deleted successfully!', 'success')
    return redirect(url_for('admin.roadmap'))

# ==================== STUDENTS MANAGEMENT ====================
@admin_bp.route('/students')
@admin_required
def students():
    students_list = User.query.filter_by(role='student').order_by(User.created_at.desc()).all()
    return render_template('admin/students.html', students=students_list)

@admin_bp.route('/students/<int:student_id>/toggle', methods=['POST'])
@admin_required
def toggle_student(student_id):
    admin_id = session.get('user_id')
    student = User.query.get_or_404(student_id)
    student.is_active = not student.is_active
    db.session.commit()

    status_str = "activated" if student.is_active else "deactivated"
    AuditLog.log_action(admin_id, 'TOGGLE_STUDENT_STATUS', 'User', student.id, f"{status_str.capitalize()} student '{student.username}'")
    flash(f"Student account {status_str}!", 'info')
    return redirect(url_for('admin.students'))

# ==================== CURRENT AFFAIRS & ANALYTICS & AUDIT LOGS ====================
@admin_bp.route('/current_affairs')
@admin_required
def current_affairs():
    return render_template('admin/current_affairs.html')

@admin_bp.route('/analytics')
@admin_required
def analytics():
    return render_template('admin/analytics.html')

@admin_bp.route('/audit_logs')
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('admin/audit_logs.html', logs=logs)
