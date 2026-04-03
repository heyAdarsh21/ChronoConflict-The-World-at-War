from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from src.ww2ops.db.models import User
from src.ww2ops.extensions import db
from src.ww2ops.repositories.auth_repository import AuthRepository


class AuthService:
    def register_user(self, username: str, email: str, password: str, role: str) -> User:
        if AuthRepository.get_by_username(username):
            raise ValueError("Username already exists")
        if AuthRepository.get_by_email(email):
            raise ValueError("Email already registered")

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        user = AuthRepository.get_by_username(username)
        if not user or not check_password_hash(user.password_hash, password):
            return None

        user.last_login_at = datetime.utcnow()
        db.session.commit()
        return user
