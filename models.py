from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    activate = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    signup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login_time = db.Column(db.DateTime)

    def update_last_login_time(self):
        self.last_login_time = datetime.utcnow()
        db.session.commit()


class UsersPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(50), default='light')
    pomodoro_duration = db.Column(db.Integer, default=25)  # Pomodoro duration in minutes
    short_break_duration = db.Column(db.Integer, default=5)  # Short break duration in minutes
    long_break_duration = db.Column(db.Integer, default=15)  # Long break duration in minutes
    
    user = db.relationship('User', backref=db.backref('preferences', lazy=True))


class CurrentSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.String(20), nullable=False)  # e.g., 'work', 'short-break', 'long-break'
    ended = db.Column(db.Boolean, nullable=False, default=False)


    user = db.relationship('User', backref=db.backref('pomodoro_sessions', lazy=True))

