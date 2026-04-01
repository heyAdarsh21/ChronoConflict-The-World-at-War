"""
WW2 Intelligence Operations Simulator
Main Flask application entry point
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

from database import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ww2-intel-ops-secret-key-1945'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ww2_intel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from models import (
    User,
    Battle,
    Operation,
    Resource,
    Territory,
    IntelligenceReport,
    Simulation,
    Leader,
    CommandAssignment,
    Campaign,
    WarCrime,
    EconomicStat,
    Tactic,
    MilitaryInnovation,
)

# Import routes after models
from routes import auth, dashboard, timeline, simulation, api, command, aftermath

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(timeline.bp)
app.register_blueprint(simulation.bp)
app.register_blueprint(api.bp)
app.register_blueprint(command.bp)
app.register_blueprint(aftermath.bp)

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

def init_db():
    """Initialize database tables and seed data"""
    with app.app_context():
        db.create_all()
        # Seed initial data if database is empty
        if Territory.query.count() == 0:
            from seed_data import seed_database
            seed_database()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

