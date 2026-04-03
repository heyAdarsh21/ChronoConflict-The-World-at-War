from src.ww2ops.db.models import User


class AuthRepository:
    @staticmethod
    def get_by_username(username: str):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email: str):
        return User.query.filter_by(email=email).first()
