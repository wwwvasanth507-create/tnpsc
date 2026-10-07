from datetime import datetime, timezone
from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request
from models import db, Lesson, Topic, Subject, StudentProgress, Bookmark, QuizSet
from routes import login_required

lessons_bp = Blueprint('lessons', __name__, url_prefix='/lessons')

@lessons_bp.route('/<int:lesson_id>')
@login_required
def detail(lesson_id):
    user_id = session.get('user_id')
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return render_template('404.html'), 404

    # Track progress/accessed
    progress = StudentProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not progress:
        progress = StudentProgress(user_id=user_id, lesson_id=lesson_id, status='started')
        db.session.add(progress)
    else:
        progress.last_accessed_at = datetime.now(timezone.utc)
    db.session.commit()

    is_bookmarked = Bookmark.query.filter_by(user_id=user_id, lesson_id=lesson_id).first() is not None
    is_completed = progress.status == 'completed'

    # Find associated quiz set for this topic/lesson if available
    associated_quiz = QuizSet.query.filter_by(topic_id=lesson.topic_id, is_active=True).first()
    if not associated_quiz:
        associated_quiz = QuizSet.query.filter_by(subject_id=lesson.topic.subject_id, is_active=True).first()

    # Next and previous lesson navigation
    prev_lesson = Lesson.query.filter(
        Lesson.topic_id == lesson.topic_id,
        Lesson.order_index < lesson.order_index,
        Lesson.is_active == True
    ).order_by(Lesson.order_index.desc()).first()

    next_lesson = Lesson.query.filter(
        Lesson.topic_id == lesson.topic_id,
        Lesson.order_index > lesson.order_index,
        Lesson.is_active == True
    ).order_by(Lesson.order_index.asc()).first()

    return render_template(
        'lessons/detail.html',
        lesson=lesson,
        progress=progress,
        is_bookmarked=is_bookmarked,
        is_completed=is_completed,
        associated_quiz=associated_quiz,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson
    )

@lessons_bp.route('/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete(lesson_id):
    user_id = session.get('user_id')
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return render_template('404.html'), 404

    progress = StudentProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not progress:
        progress = StudentProgress(user_id=user_id, lesson_id=lesson_id, status='completed')
        db.session.add(progress)
    else:
        progress.status = 'completed'
        progress.last_accessed_at = datetime.now(timezone.utc)

    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True, 'message': 'Lesson marked as completed!'})

    flash('Congratulations on completing this lesson!', 'success')
    return redirect(url_for('lessons.detail', lesson_id=lesson_id))

@lessons_bp.route('/<int:lesson_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(lesson_id):
    user_id = session.get('user_id')
    bookmark = Bookmark.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        bookmarked = False
        message = 'Bookmark removed.'
    else:
        new_bookmark = Bookmark(user_id=user_id, lesson_id=lesson_id)
        db.session.add(new_bookmark)
        db.session.commit()
        bookmarked = True
        message = 'Lesson bookmarked successfully.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True, 'bookmarked': bookmarked, 'message': message})

    flash(message, 'info')
    return redirect(url_for('lessons.detail', lesson_id=lesson_id))
