from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import datetime , timedelta
import time
import re

def moveCompletedSessions():
    try:
        # Fetch all sessions for the current user
        current_user_sessions = CurrentSession.query.filter_by(user_id=current_user.id).all()
        
        moved_count = 0
        deleted_count = 0
        non_completed_count = 0
        
        for session in current_user_sessions:
            if session.end_time is not None:  # Check if the session has ended
                # Create a new CompletedSession
                completed_session = CompletedSession(
                    user_id=session.user_id,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    phase=session.phase,
                    duration=session.end_time - session.start_time,
                    date=datetime.fromtimestamp(session.start_time)
                )
                db.session.add(completed_session)
                db.session.delete(session)
                moved_count += 1
                deleted_count += 1
            else:
                # For non-ended sessions, we'll just count them
                non_completed_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Moved {moved_count} completed sessions to CompletedSession and deleted {deleted_count} sessions",
            "non_completed_count": non_completed_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
