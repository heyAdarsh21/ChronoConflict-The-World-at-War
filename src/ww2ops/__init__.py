import json
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, render_template

from src.ww2ops.analytics.routes import analytics_bp, bp as dashboard_bp
from src.ww2ops.auth.routes import bp as auth_bp
from src.ww2ops.command.routes import bp as command_bp
from src.ww2ops.config import Config
from src.ww2ops.core.http import success_response
from src.ww2ops.db.models import User
from src.ww2ops.extensions import cache, csrf, db, limiter, migrate
from src.ww2ops.ingest.service import HistoricalIngestionService
from src.ww2ops.intelligence.routes import bp as aftermath_bp
from src.ww2ops.services.dashboard_service import DashboardService
from src.ww2ops.services.seed_service import SeedService
from src.ww2ops.simulation.routes import bp as simulation_bp
from src.ww2ops.timeline.routes import bp as timeline_bp


def create_app(config_object=Config):
    load_dotenv()
    project_root = Path(__file__).resolve().parents[2]
    app = Flask(__name__, template_folder=str(project_root / 'templates'), static_folder=str(project_root / 'static'))
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(project_root / 'migrations'))
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    csrf.exempt(auth_bp)
    csrf.exempt(simulation_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(command_bp)
    app.register_blueprint(aftermath_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/stats')
    def stats():
        return success_response(DashboardService().get_stats())

    @app.cli.command('seed-reference-data')
    def seed_reference_data():
        SeedService().seed_reference_data()
        click.echo('Reference data seeded.')

    @app.cli.command('ingest-historical-data')
    @click.option('--force-refresh', is_flag=True, default=False, help='Refresh cached remote payloads.')
    @click.option('--kaggle-csv-path', default=None, type=click.Path(exists=True, dir_okay=False))
    def ingest_historical_data(force_refresh: bool, kaggle_csv_path: str | None):
        summary = HistoricalIngestionService().ingest_all(force_refresh=force_refresh, kaggle_csv_path=kaggle_csv_path)
        click.echo(json.dumps(summary, indent=2, default=str))

    @app.cli.command('ingest-kaggle-csv')
    @click.option('--path', 'csv_path', required=True, type=click.Path(exists=True, dir_okay=False))
    def ingest_kaggle_csv(csv_path: str):
        summary = HistoricalIngestionService().ingest_kaggle_resource_csv(csv_path)
        click.echo(json.dumps({'kaggle_csv': summary}, indent=2))

    @app.cli.command('validate-backend')
    def validate_backend():
        report = {}
        with app.test_client() as client:
            report['stats'] = client.get('/api/stats').status_code
            report['auth_session'] = client.get('/auth/session').status_code
            report['dashboard_resources'] = client.get('/dashboard/api/resources').status_code
            report['dashboard_battles'] = client.get('/dashboard/api/battles').status_code
            report['dashboard_intelligence'] = client.get('/dashboard/api/intelligence').status_code
            report['timeline'] = client.get('/timeline/api/events?start_year=1939&end_year=1945').status_code
            report['command'] = client.get('/command/api/leaders').status_code
            report['aftermath'] = client.get('/aftermath/api/events').status_code
            report['analytics_root'] = client.get('/analytics/').status_code
            report['analytics_overview'] = client.get('/analytics/overview').status_code
            with app.app_context():
                user = User.query.filter_by(username='validator').first()
                if user is None:
                    user = User(username='validator', email='validator@example.com', password_hash='validation', role='analyst')
                    db.session.add(user)
                    db.session.commit()
                user_id = user.id
                username = user.username
                role = user.role
            with client.session_transaction() as session_tx:
                session_tx['user_id'] = user_id
                session_tx['username'] = username
                session_tx['role'] = role
            start_response = client.post('/simulation/start', json={'scenario_name': 'Validation Scenario', 'start_year': 1942, 'side': 'allies', 'seed': 42})
            report['simulation_start'] = start_response.status_code
            if start_response.status_code == 201:
                simulation_id = start_response.get_json()['simulation_id']
                decision_response = client.post(
                    '/simulation/decision',
                    json={
                        'simulation_id': simulation_id,
                        'decision_type': 'military_action',
                        'decision_data': {'operation_type': 'offensive', 'location': 'Normandy', 'forces': 12000},
                    },
                )
                report['simulation_decision'] = decision_response.status_code
                report['simulation_timeline'] = client.get(f'/timeline/api/events?start_year=1939&end_year=1945&simulation_id={simulation_id}').status_code
        click.echo(json.dumps(report, indent=2))

    if app.config.get('AUTO_CREATE_SCHEMA', True):
        with app.app_context():
            db.create_all()
            SeedService().seed_if_empty()

    return app

