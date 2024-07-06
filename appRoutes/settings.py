
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import datetime , timedelta
import time
import re


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