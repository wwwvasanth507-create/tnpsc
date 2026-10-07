# TNPSC 2A MASTER

**TNPSC 2A MASTER** is a personal learning and exam-preparation platform designed specifically for TNPSC Group 2A aspirants.

---

## Tech Stack & Architecture

- **Backend Framework**: Python 3 & Flask
- **Database**: PostgreSQL (with SQLite fallback for local quick-start development & unit testing)
- **ORM**: SQLAlchemy
- **Templating**: Jinja2 HTML5
- **Frontend**: Plain HTML5, CSS3 (Vanilla CSS), Vanilla JavaScript (No Node.js, npm, npx, React, Tailwind build tools, or CDN core dependencies)
- **Security**: Werkzeug Password Hashing, Session Security, Role-Based Access Control (RBAC)

---

## Directory Structure

```
tnpsc/
├── app.py                      # Application factory & entrypoint
├── config.py                   # Environment configuration (PostgreSQL/SQLite)
├── requirements.txt            # Python dependencies (No Node.js)
├── .env.example                # Configuration template
├── README.md                   # Complete documentation
│
├── models/                     # SQLAlchemy Database Models
│   ├── __init__.py
│   ├── user.py                 # Users & roles ('student', 'admin')
│   ├── subject.py              # Exam subjects catalog
│   ├── topic.py                # Curriculum topics
│   ├── lesson.py               # Concepts, examples, key points & memory tricks
│   ├── question.py             # Question bank (MCQs with 4 options)
│   ├── quiz.py                 # Quiz sets, attempts & answers
│   ├── progress.py             # Lesson & topic progress, bookmarks, mistakes
│   ├── roadmap.py              # Month-by-month study roadmap
│   └── audit_log.py            # Admin action audit trail
│
├── routes/                     # Application Blueprints
│   ├── __init__.py             # Login & Admin access decorators
│   ├── auth.py                 # Registration, login, logout
│   ├── student.py              # Student dashboard, subjects, topics, mistakes, bookmarks, profile
│   ├── lessons.py              # Concept reader, completion, bookmarking
│   ├── quizzes.py              # Quiz set list, interactive engine, submit API, attempt review
│   ├── progress.py             # Performance stats & accuracy breakdown
│   └── admin.py                # Admin dashboard, content CRUDs, audit log
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Main layout, header, responsive navbar
│   ├── 404.html                # Not Found page
│   ├── 403.html                # Access Denied page
│   ├── 500.html                # Server Error page
│   ├── auth/                   # Login & Register views
│   ├── student/                # Student dashboard, roadmap, subjects, topics, mistakes, bookmarks, progress, profile
│   ├── lessons/                # Detailed concept reader view
│   ├── quizzes/                # List, interactive test taker, result review
│   └── admin/                  # Dashboard, subjects, topics, lessons, questions, quizzes, roadmap, audit logs
│
├── static/                     # Static Assets
│   ├── css/
│   │   ├── style.css           # Core design system & utilities
│   │   ├── student.css         # Student specific styles
│   │   └── admin.css           # Admin specific styles
│   └── js/
│       ├── app.js              # Navbar & mobile drawer logic
│       ├── quiz.js             # Interactive quiz engine (Timer, pagination, submission)
│       ├── progress.js         # Progress analytics helper
│       └── admin.js            # Admin modal dialogs & form handlers
│
├── scripts/                    # Database Scripts
│   ├── init_db.py              # Database table creation
│   └── seed_data.py            # Initial seed dataset (Admin, Student, Polity, Questions)
│
└── tests/                      # Automated Test Suite
    ├── __init__.py
    ├── test_auth.py            # Auth & RBAC unit tests
    ├── test_crud.py            # Subject, Topic, Lesson, Question CRUD tests
    └── test_quiz.py            # Quiz engine & score calculation tests
```

---

## Quick Setup Instructions

### 1. Environment & Dependencies

Activate virtual environment and install dependencies:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Initialization & Seeding

Run the database scripts:

```bash
# Initialize tables
python scripts/init_db.py

# Seed demo dataset (Indian Polity, Constitution Basics, Fundamental Rights, Quiz Set)
python scripts/seed_data.py
```

### 3. Running the Application

Start the Flask application server:

```bash
python app.py
```

Access the app in your browser at: `http://localhost:5000`

---

## Default Login Credentials

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Student** | `student` | `student123` | `student@tnpsc2a.org` |
| **Admin** | `admin` | `admin123` | `admin@tnpsc2a.org` |

---

## Running Automated Tests

Run the test suite using `pytest`:

```bash
.\venv\Scripts\pytest
```

---

## Key Features

1. **Role-Based Authentication**: Protected student & admin routes enforced on server side.
2. **Interactive Quiz Engine**: Timed MCQs, instant/final score calculation, correct/wrong breakdowns.
3. **Automatic Mistake Bank**: Wrong answers are automatically saved to student's mistake bank for revision.
4. **Structured Learning**: Subject → Topic → Lesson → Concept → Examples → Important Points → Memory Tricks → Quiz → Progress.
5. **Full Admin Control & Audit Log**: Comprehensive CRUD for all learning materials with audit logging.
