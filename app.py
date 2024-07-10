"""

I am really sorry for the person helping me contribute to this project, I too have to clue as to what i am doing here, 
The AI comments here are not too helpful. 

🙏 I am sorry again, even to my future self.

"""


from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import datetime , timedelta
import time
import re

from appRoutes.stats import *
from appRoutes.moveCompletedSessions import *

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

    """
    This is really temporary please remove this from the production code this shit will make you really vulnerable 
    """
    # admin = User.query.filter_by(username='admin').first()
    # if not admin:
    #     admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    #     admin = User(username='admin', password=admin_password, activate=True, role='admin', email='admin@admin.com')
    #     db.session.add(admin)
    #     db.session.commit()
    
    # Ensure all users have UsersPreferences
    users = User.query.all()
    for user in users:
        if not UsersPreferences.query.filter_by(user_id=user.id).first():
            preferences = UsersPreferences(user_id=user.id)
            db.session.add(preferences)
    db.session.commit()

# Define routes
@app.route('/', methods = ['GET', 'POST'])
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
            flash('Invalid username or email, password, or account not activated', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Validate username and password
        if not re.match(r'^[a-zA-Z0-9_]{3,}$', username):
            flash('Username must be at least 3 characters long and contain only letters, numbers, and underscores.', 'error')
            return redirect(url_for('signup'))
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            flash('Password must be at least 8 characters long and contain a letter, a number, and a special character.', 'error')
            return redirect(url_for('signup'))
        
        try:
            existing_user = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Username already exists!', 'error')
            elif existing_email:
                flash('Email already exists!', 'error')
            else:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                
                # Check if this is the first user
                is_first_user = User.query.count() == 0
                
                new_user = User(
                    username=username, 
                    password=hashed_password, 
                    activate=is_first_user,  # Activate if it's the first user
                    email=email,
                    role='admin' if is_first_user else 'user'  # Set as admin if it's the first user
                )
                db.session.add(new_user)
                db.session.commit()

                # Create default user preferences
                preferences = UsersPreferences(user_id=new_user.id)
                db.session.add(preferences)
                db.session.commit()

                if is_first_user:
                    flash('Account created successfully! You are the first user and have been set as an admin.', 'success')
                else:
                    flash('Account created successfully! Please wait for activation.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('An error occurred while creating your account. Please try again.', 'error')
            db.session.rollback()
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    preferences = UsersPreferences.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard.html', user=current_user, preferences=preferences)

@app.route('/adminDashboard')
@login_required
def adminDashboard():
    if current_user.role == 'admin':
        page = request.args.get('page', 1, type=int)
        users = User.query.filter_by(activate=False).paginate(page=page, per_page=20)
        return render_template('adminDashboard.html', users=users)
    else:
        return redirect('/')


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




@app.route('/createSession', methods=['POST'])
@login_required
def start_session():
    try:
        user_preferences = UsersPreferences.query.filter_by(user_id=current_user.id).first()
        
        if not user_preferences:
            return jsonify({"error": "User preferences not found"}), 404

        data = request.json
        phase = data['phase']
        
        if phase == 'Pomodoro':
            duration_minutes = user_preferences.pomodoro_duration
        elif phase == 'Short Break':
            duration_minutes = user_preferences.short_break_duration
        else:
            duration_minutes = user_preferences.long_break_duration
        
        start_time = int(time.time())

        new_session = CurrentSession(
            user_id=current_user.id,
            start_time=start_time,
            phase=phase,
            end_time=None  # Set end_time to None initially
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify({"message": "Session started", "session_id": new_session.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



@app.route('/updateSession', methods=['POST'])
@login_required
def updateSession():
    try:
        data = request.json
        received_end_time = data.get('client_end_time', int(time.time()))
        phase = data['phase']

        current_session = CurrentSession.query.filter_by(user_id=current_user.id, end_time=None).order_by(CurrentSession.start_time.desc()).first()

        if not current_session:
            return jsonify({"error": "No active session found"}), 200

        # Calculate expected end time based on start time and phase duration
        user_preferences = UsersPreferences.query.filter_by(user_id=current_user.id).first()
        if phase == 'Pomodoro':
            expected_duration = user_preferences.pomodoro_duration * 60
        elif phase == 'Short Break':
            expected_duration = user_preferences.short_break_duration * 60
        else:
            expected_duration = user_preferences.long_break_duration * 60

        expected_end_time = current_session.start_time + expected_duration

        # Allow for a 20-second discrepancy
        allowed_discrepancy = 80

        if abs(received_end_time - expected_end_time) > allowed_discrepancy:
            # If the discrepancy is too large, log it but still accept the data
            app.logger.warning(f"Large time discrepancy detected for user {current_user.id}. Expected: {expected_end_time}, Received: {received_end_time}, discrepancy by: {abs(received_end_time - expected_end_time)} ")

        # Use the received end_time, but ensure it's not earlier than start_time
        end_time = max(received_end_time, current_session.start_time)
        #there is some stupid bug with some zero thing 
        # Check if duration is zero or negative and handle accordingly
        if end_time <= current_session.start_time:
            return jsonify({
                "message": "Duration is zero or negative, session not updated",
                "session_id": current_session.id,
                "actual_duration": 0,
                "duration_zero_used": True
            }), 200

        # Update the current session
        current_session.end_time = end_time
        current_session.phase = phase  # Update phase in case it changed
        db.session.commit()

        return jsonify({
            "message": "Session updated",
            "session_id": current_session.id,
            "actual_duration": end_time - current_session.start_time,
            "duration_zero_used": False
        }), 200

    except Exception as e:
        print(f"Error updating session for user {current_user.id}: {e}")
        return jsonify({"error": "Failed to update session"}), 500


@app.route('/moveCompletedSessions', methods=['POST'])
@login_required
def getMoveCompletedSessions():
    return moveCompletedSessions()  

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    preferences = UsersPreferences.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        if 'update_duration' in request.form:
            # Update duration settings
            preferences.pomodoro_duration = int(request.form['pomodoro_duration'])
            preferences.short_break_duration = int(request.form['short_break_duration'])
            preferences.long_break_duration = int(request.form['long_break_duration'])
            db.session.commit()
            flash('Duration settings updated successfully', 'success')

        elif 'change_email' in request.form:
            # Change email
            new_email = request.form['new_email']
            if User.query.filter_by(email=new_email).first():
                flash('Email already in use', 'error')
            else:
                current_user.email = new_email
                db.session.commit()
                flash('Email updated successfully', 'success')

        elif 'change_password' in request.form:
            # Change password
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            if check_password_hash(current_user.password, current_password):
                current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password changed successfully', 'success')
            else:
                flash('Current password is incorrect', 'error')

        elif 'delete_account' in request.form:
            # Delete account
            db.session.delete(current_user)
            db.session.commit()
            flash('Your account has been deleted', 'success')
            return redirect(url_for('logout'))

        return redirect(url_for('settings'))

    return render_template('settings.html', user=current_user, preferences=preferences)


@app.route('/user_statistics')
@login_required
def getUserStatistics():
    return userStatistics()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

if __name__ == '__main__':
    app.run(debug=True)
