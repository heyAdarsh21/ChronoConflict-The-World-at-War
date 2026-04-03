from http import HTTPStatus

from flask import jsonify
from pydantic import ValidationError


def success_response(data, status: int = HTTPStatus.OK):
    return jsonify(data), status


def error_response(message: str, status: int = HTTPStatus.BAD_REQUEST, *, details=None):
    payload = {"error": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status


def validation_error_response(exc: ValidationError):
    return error_response("Validation failed", HTTPStatus.UNPROCESSABLE_ENTITY, details=exc.errors())
