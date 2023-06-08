# Installed Imports
from flask import Flask
from flask_marshmallow import Marshmallow

# Custom Imports
from app.config import Config, ProductionConfig

app = Flask(__name__)
ma = Marshmallow(app)


def create_app():
    app.config.from_object(Config)
    app.config.from_object(ProductionConfig)

    register_blueprints()
    return app


def register_blueprints():
    from app.views import pokeman_api

    app.register_blueprint(pokeman_api)
