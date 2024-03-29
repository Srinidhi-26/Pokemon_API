# Installed Imports
from flask import Flask
from flask_marshmallow import Marshmallow

# Custom Imports
from app.config import Config

app = Flask(__name__)
ma = Marshmallow(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://pok:pok@localhost/pokk"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

from app import models

def create_app():
    config = Config(app)
    app.config.update(config.parse_config())
    register_blueprints()
    return app


def register_blueprints():
    from app.views import pokeman_api

    app.register_blueprint(pokeman_api)
