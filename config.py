import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tnpsc2a-master-super-secret-key-2026')
    # Default to sqlite local db if DATABASE_URL is not set or empty
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tnpsc2a.db')}"
    )
    # Fix postgresql:// prefix if legacy postgres:// is passed
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
