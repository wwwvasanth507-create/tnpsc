// Interactive Quiz Engine - Pure Vanilla JS
document.addEventListener('DOMContentLoaded', () => {
    const quizContainer = document.getElementById('quiz-container');
    if (!quizContainer) return;

    const quizId = quizContainer.dataset.quizId;
    const timeLimitMins = parseInt(quizContainer.dataset.timeLimit || '15', 10);
    const questions = document.querySelectorAll('.question-card');
    const totalQuestions = questions.length;

    let currentIndex = 0;
    let timerInterval = null;
    let secondsLeft = timeLimitMins * 60;

    const timerDisplay = document.getElementById('quiz-timer');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-quiz-btn');
    const navPills = document.querySelectorAll('.q-nav-pill');
    const quizForm = document.getElementById('quiz-form');

    // 1. Timer Countdown
    function updateTimerDisplay() {
        const mins = Math.floor(secondsLeft / 60);
        const secs = secondsLeft % 60;
        if (timerDisplay) {
            timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            if (secondsLeft <= 60) {
                timerDisplay.classList.remove('text-amber-400');
                timerDisplay.classList.add('text-rose-400', 'animate-pulse');
            }
        }
    }

    function startTimer() {
        updateTimerDisplay();
        timerInterval = setInterval(() => {
            secondsLeft--;
            updateTimerDisplay();
            if (secondsLeft <= 0) {
                clearInterval(timerInterval);
                alert('Time is up! Submitting your quiz now.');
                submitQuiz();
            }
        }, 1000);
    }

    startTimer();

    // 2. Question View Navigation
    function showQuestion(index) {
        if (index < 0 || index >= totalQuestions) return;

        questions.forEach((q, i) => {
            if (i === index) {
                q.classList.remove('hidden');
            } else {
                q.classList.add('hidden');
            }
        });

        // Update Nav Pills
        navPills.forEach((pill, i) => {
            if (i === index) {
                pill.classList.add('active', 'border-indigo-500', 'text-indigo-400', 'bg-indigo-950/40');
            } else {
                pill.classList.remove('active', 'border-indigo-500', 'text-indigo-400', 'bg-indigo-950/40');
            }
        });

        currentIndex = index;

        // Button states
        if (prevBtn) prevBtn.disabled = (currentIndex === 0);
        if (nextBtn) {
            if (currentIndex === totalQuestions - 1) {
                nextBtn.textContent = 'Review All Questions';
            } else {
                nextBtn.textContent = 'Next Question →';
            }
        }
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            showQuestion(currentIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentIndex < totalQuestions - 1) {
                showQuestion(currentIndex + 1);
            }
        });
    }

    navPills.forEach((pill) => {
        pill.addEventListener('click', () => {
            const targetIdx = parseInt(pill.dataset.target, 10);
            showQuestion(targetIdx);
        });
    });

    // 3. Option Selection Card Highlight
    document.querySelectorAll('.option-radio').forEach((radio) => {
        radio.addEventListener('change', (e) => {
            const label = radio.closest('.option-card');
            const parentCard = radio.closest('.question-card');
            parentCard.querySelectorAll('.option-card').forEach(card => card.classList.remove('selected'));
            if (label) label.classList.add('selected');

            // Highlight pill if answered
            const qIndex = parseInt(parentCard.dataset.index, 10);
            if (navPills[qIndex]) {
                navPills[qIndex].classList.add('bg-emerald-950/40', 'border-emerald-500/50', 'text-emerald-400');
            }
        });
    });

    // 4. Submit Quiz Handler
    function submitQuiz() {
        clearInterval(timerInterval);

        const answers = {};
        questions.forEach((qCard) => {
            const qId = qCard.dataset.questionId;
            const checkedRadio = qCard.querySelector(`input[name="q_${qId}"]:checked`);
            if (checkedRadio) {
                answers[qId] = checkedRadio.value;
            }
        });

        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting Results...';

        fetch(quizForm.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ answers: answers })
        })
        .then(res => res.json())
        .then(data => {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                alert('Quiz submitted! Score: ' + data.percentage + '%');
                window.location.href = '/quizzes';
            }
        })
        .catch(err => {
            console.error('Submission error:', err);
            // Fallback to standard form submit
            quizForm.submit();
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
            const answeredCount = document.querySelectorAll('.option-radio:checked').length;
            if (confirm(`You have answered ${answeredCount} of ${totalQuestions} questions. Are you ready to submit your quiz?`)) {
                submitQuiz();
            }
        });
    }
});
