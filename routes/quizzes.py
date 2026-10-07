from datetime import datetime, timezone
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from models import db, QuizSet, QuizQuestion, Question, QuizAttempt, QuizAnswer, MistakeQuestion, Subject, Topic
from routes import login_required

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')

@quizzes_bp.route('/')
@login_required
def list_quizzes():
    user_id = session.get('user_id')
    active_quizzes = QuizSet.query.filter_by(is_active=True).all()
    user_attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.completed_at.desc()).all()

    # Map latest attempt per quiz
    attempt_map = {}
    for att in user_attempts:
        if att.quiz_set_id not in attempt_map:
            attempt_map[att.quiz_set_id] = att

    return render_template(
        'quizzes/list.html',
        quizzes=active_quizzes,
        attempt_map=attempt_map
    )

@quizzes_bp.route('/<int:quiz_id>/take')
@login_required
def take_quiz(quiz_id):
    quiz = QuizSet.query.get_or_404(quiz_id)
    if not quiz.is_active:
        flash('This quiz is currently unavailable.', 'warning')
        return redirect(url_for('quizzes.list_quizzes'))

    # Fetch questions mapped to this quiz
    qq_list = QuizQuestion.query.filter_by(quiz_set_id=quiz_id).order_by(QuizQuestion.order_index.asc()).all()
    questions = [qq.question for qq in qq_list if qq.question and qq.question.is_active]

    if not questions:
        # Fallback: get questions from subject/topic if quiz set questions not explicitly populated
        if quiz.topic_id:
            questions = Question.query.filter_by(topic_id=quiz.topic_id, is_active=True).limit(10).all()
        elif quiz.subject_id:
            questions = Question.query.filter_by(subject_id=quiz.subject_id, is_active=True).limit(10).all()

    return render_template('quizzes/take.html', quiz=quiz, questions=questions)

@quizzes_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    user_id = session.get('user_id')
    quiz = QuizSet.query.get_or_404(quiz_id)

    data = request.get_json() or request.form
    # Expecting user answers formatted as dict: { "question_id": "selected_option" }
    answers = data.get('answers', {})

    qq_list = QuizQuestion.query.filter_by(quiz_set_id=quiz_id).order_by(QuizQuestion.order_index.asc()).all()
    questions = [qq.question for qq in qq_list if qq.question and qq.question.is_active]
    
    if not questions:
        if quiz.topic_id:
            questions = Question.query.filter_by(topic_id=quiz.topic_id, is_active=True).limit(10).all()
        elif quiz.subject_id:
            questions = Question.query.filter_by(subject_id=quiz.subject_id, is_active=True).limit(10).all()

    total_questions = len(questions)
    correct_count = 0
    wrong_count = 0

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_set_id=quiz_id,
        total_questions=total_questions,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc)
    )
    db.session.add(attempt)
    db.session.flush()  # get attempt.id

    for q in questions:
        q_id_str = str(q.id)
        selected_option = answers.get(q_id_str, '').upper() if isinstance(answers, dict) else None
        
        is_correct = (selected_option == q.correct_option)
        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1
            # Save to mistake questions if wrong option selected
            existing_mistake = MistakeQuestion.query.filter_by(
                user_id=user_id, question_id=q.id, is_resolved=False
            ).first()
            if not existing_mistake:
                mistake = MistakeQuestion(
                    user_id=user_id,
                    question_id=q.id,
                    attempt_id=attempt.id,
                    user_wrong_option=selected_option
                )
                db.session.add(mistake)

        quiz_answer = QuizAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=selected_option,
            is_correct=is_correct
        )
        db.session.add(quiz_answer)

    percentage = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0
    attempt.correct_count = correct_count
    attempt.wrong_count = wrong_count
    attempt.score = float(correct_count * 1)
    attempt.percentage = percentage

    db.session.commit()

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'attempt_id': attempt.id,
            'percentage': percentage,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'total_questions': total_questions,
            'redirect_url': url_for('quizzes.view_attempt', attempt_id=attempt.id)
        })

    flash(f'Quiz completed! Score: {percentage}%', 'success')
    return redirect(url_for('quizzes.view_attempt', attempt_id=attempt.id))

@quizzes_bp.route('/attempts/<int:attempt_id>')
@login_required
def view_attempt(attempt_id):
    user_id = session.get('user_id')
    attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=user_id).first_or_404()
    answers = QuizAnswer.query.filter_by(attempt_id=attempt_id).all()

    return render_template(
        'quizzes/result.html',
        attempt=attempt,
        answers=answers
    )
