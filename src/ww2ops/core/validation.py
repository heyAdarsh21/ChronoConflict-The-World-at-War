from typing import Type

from flask import request
from pydantic import BaseModel


def parse_json(model: Type[BaseModel]):
    payload = request.get_json(silent=True) or {}
    return model.model_validate(payload)
