from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from datetime import datetime , timedelta
import time
import re


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

    # Prepare data for pie chart (time distribution)
    pie_chart_data = {
        'labels': ['Work', 'Short Break', 'Long Break'],
        'datasets': [{
            'label': 'Time Distribution',
            'data': [work_sessions, short_breaks, long_breaks],
            'backgroundColor': [
                'rgba(238, 57, 64, 0.4)',  # var(--primary-red) with opacity
                'rgba(30, 144, 255, 0.2)',  # var(--accent-blue) with opacity
                'rgba(0, 128, 0, 0.2)',  # var(--secondary-green) with opacity
            ],
            'borderColor': [
                'rgba(238, 57, 64, 0.4)',  # var(--primary-red)
                'rgba(30, 144, 255, 1)',  # var(--accent-blue)
                'rgba(0, 128, 0, 1)',  # var(--secondary-green)
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
        'naps_taken': round(naps_taken, 2)
    }

    return jsonify({
        'pie_chart_data': pie_chart_data,
        'line_chart_data': line_chart_data,
        'fun_stats': fun_stats,
        'time_range': time_range
    })


def generateDailyLineChart(sessions):
    end_time = int(time.time())
    start_time = end_time - 24 * 60 * 60  # 24 hours ago
    
    hourly_data = {hour: 0 for hour in range(24)}
    
    for session in sessions:
        session_start_hour = (session.start_time - start_time) // 3600
        if 0 <= session_start_hour < 24:
            hourly_data[session_start_hour] += session.duration / 60  # Convert to minutes
    
    labels = [(datetime.fromtimestamp(start_time + i * 3600).strftime('%H:%M')) for i in range(24)]
    data = [hourly_data[i] for i in range(24)]
    
    return {
        'labels': labels,
        'datasets': [{
            'label': 'Minutes',
            'data': data,
            'borderColor': 'rgba(30, 144, 255)',
            'fill': False,
            'lineTension': 0.4
        }]
    }



def generateWeeklyLineChart(sessions):
    daily_durations = {}
    for session in sessions:
        day_of_week = time.strftime("%A", time.localtime(session.start_time))
        if day_of_week not in daily_durations:
            daily_durations[day_of_week] = []
        daily_durations[day_of_week].append(session.duration / 3600)  # Convert duration to hours

    return {
        'labels': list(daily_durations.keys()),
        'datasets': [{
            'label': 'Study Duration per Day (hours)',
            'data': [sum(durations) for day, durations in daily_durations.items()],
            'fill': False,
            'borderColor': 'rgb(30, 144, 255)',
            'lineTension': 0.4
        }]
    }


def generateMonthlyLineChart(sessions):
    daily_durations = {}
    for session in sessions:
        day_of_month = time.strftime("%d", time.localtime(session.start_time))
        if day_of_month not in daily_durations:
            daily_durations[day_of_month] = []
        daily_durations[day_of_month].append(session.duration / 3600)  # Convert duration to hours

    return {
        'labels': list(daily_durations.keys()),
        'datasets': [{
            'label': 'Study Duration per Day (hours)',
            'data': [sum(durations) for day, durations in daily_durations.items()],
            'fill': False,
            'borderColor': 'rgb(30, 144, 255)',
            'lineTension': 0.4
        }]
    }


def generateYearlyLineChart(sessions):
    monthly_durations = {}
    for session in sessions:
        month = time.strftime("%b", time.localtime(session.start_time))
        if month not in monthly_durations:
            monthly_durations[month] = []
        monthly_durations[month].append(session.duration / 3600)  # Convert duration to hours

    return {
        'labels': list(monthly_durations.keys()),
        'datasets': [{
            'label': 'Study Duration per Month (hours)',
            'data': [sum(durations) for month, durations in monthly_durations.items()],
            'fill': False,
            'borderColor': 'rgb(30, 144, 255)',
            'lineTension': 0.4
        }]
    }


def generateAllTimeLineChart(sessions):
    yearly_durations = {}
    for session in sessions:
        year = time.strftime("%Y", time.localtime(session.start_time))
        if year not in yearly_durations:
            yearly_durations[year] = []
        yearly_durations[year].append(session.duration / 3600)  # Convert duration to hours

    return {
        'labels': list(yearly_durations.keys()),
        'datasets': [{
            'label': 'Total Study Duration per Year (hours)',
            'data': [sum(durations) for year, durations in yearly_durations.items()],
            'fill': False,
            'borderColor': 'rgb(30, 144, 255)',
            'lineTension': 0.4
        }]
    }