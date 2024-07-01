from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key man!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize SQLAlchemy and LoginManager
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all tables
with app.app_context():
    db.create_all()
    
    # Create admin user if it doesn't exist 
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        admin = User(username='admin', password=admin_password, activate=True, role='admin', email='admin@admin.com')
        db.session.add(admin)
        db.session.commit()
    
    # Ensure all users have UsersPreferences
    users = User.query.all()
    for user in users:
        if not UsersPreferences.query.filter_by(user_id=user.id).first():
            preferences = UsersPreferences(user_id=user.id)
            db.session.add(preferences)
    db.session.commit()

# Define routes
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and check_password_hash(user.password, password) and user.activate:
            login_user(user)
            user.last_login_time = datetime.utcnow()  
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or email, password, or account not activated')
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password, activate=False, email=email)
            db.session.add(new_user)
            db.session.commit()

            # Create default user preferences
            preferences = UserPreferences(user_id=new_user.id)
            db.session.add(preferences)
            db.session.commit()

            flash('Account created successfully! Please wait for activation.')
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello'))

@app.route('/dashboard')
@login_required
def dashboard():
    preferences = UsersPreferences.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard.html', user=current_user, preferences=preferences)



@app.route('/activate_user/<int:user_id>', methods=['POST'])
@login_required
def activate_user(user_id):
    if current_user.role != 'admin':
        flash('Permission denied. Only admin can activate users.', 'error')
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if user:
        user.activate = True
        db.session.commit()
        flash(f'User {user.username} has been activated.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('dashboard'))



@app.route('/update/stat', methods=['GET'])
@login_required
def stat():
    print("The current user is:", current_user.username)
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

if __name__ == '__main__':
    app.run(debug=True)
