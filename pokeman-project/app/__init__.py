# Installed Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('config.py')

try:
    from app import pokeman, models
    app.register_blueprint(pokeman.pokeman_api)
    models.db.configure_mappers()
    models.db.create_all()
    models.db.session.commit()
    
    
except Exception as e:
    print(f"Error: {e}")