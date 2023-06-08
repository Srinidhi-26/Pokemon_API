# Installed Imports
from flask import Flask, request
from functools import wraps

# Custom Imports
from app import app

TOKENS = "pokemon-api"


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Api-Token")

        if not token:
            return {"message": "Authentication Required"}, 401

        if token not in TOKENS:
            return {"message": "Invalid token"}, 401

        return f(*args, **kwargs)

    return decorated
