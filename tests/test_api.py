import pytest

from src.ww2ops import create_app
from src.ww2ops.config import Config
from src.ww2ops.extensions import db


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    AUTO_CREATE_SCHEMA = True


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_stats_endpoint_returns_expected_shape(client):
    response = client.get('/api/stats')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'total_battles' in payload
    assert 'date_range' in payload
