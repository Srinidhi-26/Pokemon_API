# Installed Imports
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Custom Imports
from app import ma
from app import app


db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db, compare_type=True)


@dataclass
class Pokemon(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    rank: int = db.Column(db.Integer)
    name: str = db.Column(db.Text, unique=True)
    type_1: str = db.Column(db.Text, nullable=True)
    type_2: str = db.Column(db.Text, nullable=True)
    total: int = db.Column(db.Integer, nullable=True)
    hp: int = db.Column(db.Integer, nullable=True)
    attack: int = db.Column(db.Integer, nullable=True)
    defense: int = db.Column(db.Integer, nullable=True)
    sp_atk: int = db.Column(db.Integer, nullable=True)
    sp_def: int = db.Column(db.Integer)
    speed: int = db.Column(db.Integer, nullable=True)
    generation: int = db.Column(db.Integer, nullable=True)
    legendary: bool = db.Column(db.Boolean)


class PokemonSchema(ma.Schema):
    class Meta:
        fields = (
            "rank",
            "name",
            "type_1",
            "type_2",
            "total",
            "hp",
            "attack",
            "defense",
            "sp_atk",
            "sp_def",
            "speed",
            "generation",
            "legendary",
        )


pokemon_schema = PokemonSchema()
pokemonss_schema = PokemonSchema(many=True)
