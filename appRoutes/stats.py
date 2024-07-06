from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import datetime, timedelta
import time
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Assuming User, CompletedSession models are defined in models.py

@app.route('/user_statistics', methods=['GET'])
@login_required
def userStatistics():
    time_range = request.args.get('range')

    if time_range == 'day':
        delta = timedelta(hours=24)
    elif time_range == 'week':
        delta = timedelta(days=7)
    elif time_range == 'month':
        delta = timedelta(days=30)  # assuming a month is 30 days
    elif time_range == 'year':
        delta = timedelta(days=365)
    elif time_range == 'all_time':
        delta = None  # No delta means fetch all sessions
    else:
        raise ValueError("Invalid time range")

    user_id = current_user.id

    if time_range == 'all_time':
        sessions = CompletedSession.query.filter((CompletedSession.user_id == user_id) & (CompletedSession.duration >= 0)).all()
    elif time_range == 'year':
        start_date = int(time.time()) - delta.total_seconds()
        sessions = CompletedSession.query.filter((CompletedSession.user_id == user_id) & (CompletedSession.start_time >= start_date) & (CompletedSession.duration >= 0)).all()
    else:
        start_date = int(time.time()) - delta.total_seconds()
        end_date = int(time.time())
        sessions = CompletedSession.query.filter((CompletedSession.user_id == user_id) & (CompletedSession.start_time >= start_date) & (CompletedSession.start_time <= end_date) & (CompletedSession.duration >= 0)).all()

    # Calculate the total count of each session type for the pie chart
    work_sessions_count = sum(1 for session in sessions if session.phase == 'Pomodoro')
    short_breaks_count = sum(1 for session in sessions if session.phase == 'Short Break')
    long_breaks_count = sum(1 for session in sessions if session.phase == 'Long Break')

    # Prepare data for pie chart (count distribution)
    pie_chart_data = {
        'labels': ['Work', 'Short Break', 'Long Break'],
        'datasets': [{
            'label': 'Session Distribution',
            'data': [work_sessions_count, short_breaks_count, long_breaks_count],
            'backgroundColor': [
                'rgba(30, 144, 255, 0.4)',  # Pomodoro
                'rgba(0, 128, 0, 0.2)',  # Short Break
                'rgba(238, 57, 64, 0.2)',  # Long Break
            ],
            'borderColor': [
                'rgba(30, 144, 255, 1)',  # Pomodoro
                'rgba(0, 128, 0, 1)',  # Short Break
                'rgba(238, 57, 64, 1)',  # Long Break
            ],
            'borderWidth': 1
        }]
    }

    line_chart_data = {}

    if time_range == 'day':
        line_chart_data = generateDailyLineChart(sessions)
    elif time_range == 'week':
        line_chart_data = generateWeeklyLineChart(sessions)
    elif time_range == 'month':
        line_chart_data = generateMonthlyLineChart(sessions)
    elif time_range == 'year':
        line_chart_data = generateYearlyLineChart(sessions)
    elif time_range == 'all_time':
        line_chart_data = generateAllTimeLineChart(sessions)

    fun_stats = calculateFunStats(sessions)

    return jsonify({
        'pie_chart_data': pie_chart_data,
        'line_chart_data': line_chart_data,
        'fun_stats': fun_stats,
        'time_range': time_range
    })

def generateDailyLineChart(sessions):
    # Find the latest session start time in seconds since epoch
    if sessions:
        start_time = max(session.start_time for session in sessions)
    else:
        # Default to 24 hours ago if no sessions found
        start_time = int(time.time()) - 24 * 60 * 60
    
    end_time = start_time + 24 * 60 * 60  # 24 hours after the start time
    hourly_data = {phase: [0] * 24 for phase in ['Pomodoro', 'Short Break', 'Long Break']}
    
    for session in sessions:
        session_start_hour = (session.start_time - start_time) // 3600
        if 0 <= session_start_hour < 24:
            hourly_data[session.phase][session_start_hour] += session.duration / 60  # Convert to minutes

    labels = [(datetime.fromtimestamp(start_time + i * 3600).strftime('%H:%M')) for i in range(24)]
    
    datasets = []
    colors = {
        'Pomodoro': 'rgba(30, 144, 255)',
        'Short Break': 'rgba(0, 128, 0)',
        'Long Break': 'rgba(238, 57, 64)'
    }

    for phase in hourly_data:
        datasets.append({
            'label': phase,
            'data': [round(val, 2) for val in hourly_data[phase][::-1]],  # Reverse to oldest to latest
            'borderColor': colors[phase],
            'fill': False,
            'lineTension': 0.4
        })

    return {
        'labels': labels[::-1],  # Reverse to oldest to latest
        'datasets': datasets
    }


def generateWeeklyLineChart(sessions):
    daily_durations = {phase: {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']} for phase in ['Pomodoro', 'Short Break', 'Long Break']}
    
    for session in sessions:
        day_of_week = time.strftime("%A", time.localtime(session.start_time))
        daily_durations[session.phase][day_of_week] += session.duration / 3600  # Convert duration to hours

    datasets = []
    colors = {
        'Pomodoro': 'rgba(30, 144, 255)',
        'Short Break': 'rgba(0, 128, 0)',
        'Long Break': 'rgba(238, 57, 64)'
    }

    for phase in daily_durations:
        datasets.append({
            'label': phase,
            'data': [round(val, 2) for val in list(daily_durations[phase].values())],  # Round to 2 decimal places
            'borderColor': colors[phase],
            'fill': False,
            'lineTension': 0.4
        })

    return {
        'labels': list(daily_durations['Pomodoro'].keys()),
        'datasets': datasets
    }


def generateMonthlyLineChart(sessions):
    daily_durations = {phase: {day: 0 for day in range(1, 32)} for phase in ['Pomodoro', 'Short Break', 'Long Break']}
    
    for session in sessions:
        day_of_month = int(time.strftime("%d", time.localtime(session.start_time)))
        daily_durations[session.phase][day_of_month] += session.duration / 3600  # Convert duration to hours

    datasets = []
    colors = {
        'Pomodoro': 'rgba(30, 144, 255)',
        'Short Break': 'rgba(0, 128, 0)',
        'Long Break': 'rgba(238, 57, 64)'
    }

    for phase in daily_durations:
        datasets.append({
            'label': phase,
            'data': [round(val, 2) for val in list(daily_durations[phase].values())],  # Round to 2 decimal places
            'borderColor': colors[phase],
            'fill': False,
            'lineTension': 0.4
        })

    return {
        'labels': list(daily_durations['Pomodoro'].keys()),
        'datasets': datasets
    }


def generateYearlyLineChart(sessions):
    monthly_durations = {phase: {month: 0 for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']} for phase in ['Pomodoro', 'Short Break', 'Long Break']}
    
    for session in sessions:
        month = time.strftime("%b", time.localtime(session.start_time))
        monthly_durations[session.phase][month] += session.duration / 3600  # Convert duration to hours

    datasets = []
    colors = {
        'Pomodoro': 'rgba(30, 144, 255)',
        'Short Break': 'rgba(0, 128, 0)',
        'Long Break': 'rgba(238, 57, 64)'
    }

    for phase in monthly_durations:
        datasets.append({
            'label': phase,
            'data': [round(val, 2) for val in list(monthly_durations[phase].values())],  # Round to 2 decimal places
            'borderColor': colors[phase],
            'fill': False,
            'lineTension': 0.4
        })

    return {
        'labels': list(monthly_durations['Pomodoro'].keys()),
        'datasets': datasets
    }


def generateAllTimeLineChart(sessions):
    yearly_durations = {phase: {} for phase in ['Pomodoro', 'Short Break', 'Long Break']}
    
    for session in sessions:
        year = time.strftime("%Y", time.localtime(session.start_time))
        if year not in yearly_durations[session.phase]:
            yearly_durations[session.phase][year] = 0
        yearly_durations[session.phase][year] += session.duration / 3600  # Convert duration to hours

    datasets = []
    colors = {
        'Pomodoro': 'rgba(30, 144, 255)',
        'Short Break': 'rgba(0, 128, 0)',
        'Long Break': 'rgba(238, 57, 64)'
    }

    for phase in yearly_durations:
        datasets.append({
            'label': phase,
            'data': [round(val, 2) for val in list(yearly_durations[phase].values())],  # Round to 2 decimal places
            'borderColor': colors[phase],
            'fill': False,
            'lineTension': 0.4
        })
    return {
        'labels': list(yearly_durations['Pomodoro'].keys()),
        'datasets': datasets
    }




def calculateFunStats(sessions):
    total_duration = sum(session.duration for session in sessions if session.duration >= 0)
    work_sessions = sum(1 for session in sessions if session.phase == 'Pomodoro')
    short_breaks = sum(1 for session in sessions if session.phase == 'Short Break')
    long_breaks = sum(1 for session in sessions if session.phase == 'Long Break')

    total_hours = total_duration / 3600
    total_minutes = total_duration / 60
    total_seconds = total_duration

    books_read = total_hours / 5  # Assuming 5 hours to read a book
    movies_watched = total_hours / 2  # Assuming 2 hours to watch a movie
    marathons_run = total_hours / 4  # Assuming 4 hours to run a marathon
    articles_read = total_hours / 1  # Assuming 1 hour to read an article
    blog_posts_written = total_hours / 2  # Assuming 2 hours to write a blog post
    songs_listened = total_hours * 20  # Assuming 20 songs per hour
    podcasts_listened = total_hours / 1.5  # Assuming 1.5 hours to listen to a podcast
    naps_taken = total_hours / 0.5  # Assuming 0.5 hours to take a nap
    cups_of_coffee = total_hours / 0.25  # Assuming 15 minutes per cup of coffee
    miles_walked = total_hours * 3  # Assuming 3 miles per hour
    steps_taken = total_hours * 2000  # Assuming 2000 steps per hour


    fun_stats = {
        'total_hours': round(total_hours, 2),
        'total_minutes': round(total_minutes, 2),
        'total_seconds': round(total_seconds, 0),
        'work_sessions': work_sessions,
        'short_breaks': short_breaks,
        'long_breaks': long_breaks,
        'books_read': round(books_read, 2),
        'movies_watched': round(movies_watched, 2),
        'marathons_run': round(marathons_run, 2),
        'articles_read': round(articles_read, 2),
        'blog_posts_written': round(blog_posts_written, 2),
        'songs_listened': round(songs_listened, 0),
        'podcasts_listened': round(podcasts_listened, 2),
        'naps_taken': round(naps_taken, 2),
        'cups_of_coffee': round(cups_of_coffee, 2),
        'miles_walked': round(miles_walked, 2),
        'steps_taken': round(steps_taken, 2),
    }

    return fun_stats
