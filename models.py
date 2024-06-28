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
