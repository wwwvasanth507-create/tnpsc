import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
from models import db, User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_registration(client):
    response = client.post('/auth/register', data={
        'full_name': 'Test Aspirant',
        'username': 'teststudent',
        'email': 'test@tnpsc2a.org',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data or b'Sign In' in response.data

    user = User.query.filter_by(username='teststudent').first()
    assert user is not None
    assert user.role == 'student'
    assert user.check_password('password123') is True

def test_login_and_role_protection(client):
    # Create student & admin
    with client.application.app_context():
        st = User(username='st1', email='st1@tnpsc2a.org', full_name='Student 1', role='student')
        st.set_password('st1pass')
        ad = User(username='ad1', email='ad1@tnpsc2a.org', full_name='Admin 1', role='admin')
        ad.set_password('ad1pass')
        db.session.add_all([st, ad])
        db.session.commit()

    # Login as student
    response = client.post('/auth/login', data={
        'identifier': 'st1',
        'password': 'st1pass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back' in response.data

    # Try to access admin dashboard -> Expect redirect / access denied flash
    response_admin = client.get('/admin/dashboard', follow_redirects=True)
    assert b'Access denied' in response_admin.data or b'Student Dashboard' in response_admin.data

    # Logout
    client.get('/auth/logout')

    # Login as admin
    response_admin_login = client.post('/auth/login', data={
        'identifier': 'ad1',
        'password': 'ad1pass'
    }, follow_redirects=True)
    assert response_admin_login.status_code == 200
    assert b'Administrator Control Center' in response_admin_login.data
