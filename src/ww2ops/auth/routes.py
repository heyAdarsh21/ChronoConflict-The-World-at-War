from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from pydantic import ValidationError

from src.ww2ops.core.http import success_response
from src.ww2ops.schemas.requests import LoginRequest, RegisterRequest
from src.ww2ops.services.auth_service import AuthService

bp = Blueprint("auth", __name__, url_prefix="/auth")
service = AuthService()


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            payload = RegisterRequest.model_validate(dict(request.form))
            user = service.register_user(payload.username, payload.email, payload.password, payload.role)
        except ValidationError:
            flash("Invalid registration data")
            return render_template("auth/register.html"), 422
        except ValueError as exc:
            flash(str(exc))
            return redirect(url_for("auth.register"))

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            payload = LoginRequest.model_validate(dict(request.form))
        except ValidationError:
            flash("Invalid credentials")
            return render_template("auth/login.html"), 422

        user = service.authenticate(payload.username, payload.password)
        if not user:
            flash("Invalid username or password")
            return render_template("auth/login.html"), 401

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@bp.route("/session")
def session_status():
    return success_response({
        "authenticated": bool(session.get("user_id")),
        "user_id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role"),
    })


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
