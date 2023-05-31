from app import app
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db, compare_type=True)


@dataclass
class Pokemon(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    rank: int = db.Column(db.Integer)
    Name: str = db.Column(db.Text, unique=True)
    Type_1: str = db.Column(db.Text)
    Type_2: str = db.Column(db.Text)
    Total: int = db.Column(db.Integer)
    HP: int = db.Column(db.Integer)
    Attack: int = db.Column(db.Integer)
    Defense: int = db.Column(db.Integer)
    Sp_Atk: int = db.Column(db.Integer)
    Sp_Def: int = db.Column(db.Integer)
    Speed: int = db.Column(db.Integer)
    Generation: int = db.Column(db.Integer)
    Legendary: bool = db.Column(db.Boolean)


