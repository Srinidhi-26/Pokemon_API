#!/usr/bin/env python3
import os
import sys
import requests

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(parentdir)
sys.path.insert(0, parentdir)

from app import app
from app.models import db, Pokemon
from app.views import pokeman_api


class PokemonException(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


@pokeman_api.errorhandler(PokemonException)
def handle_scheduler_exception(e):
    app.logger.exception(e)
    return {"success": False, "error": e.message}, e.code

url = "https://coralvanda.github.io/pokemon_data.json"
response = requests.get(url)
data = response.json()

def get_load_data():
    for pokemon in data:
         existing_pokemon = Pokemon.query.filter_by(name=pokemon["Name"]).first()
         if existing_pokemon:
            raise PokemonException(f"Pokemon data already present")
         pokemon_data = Pokemon(
            rank=pokemon["#"],
            name=pokemon["Name"],
            type_1=pokemon["Type 1"],
            type_2=pokemon["Type 2"],
            total=pokemon["Total"],
            hp=pokemon["HP"],
            attack=pokemon["Attack"],
            defense=pokemon["Defense"],
            sp_atk=pokemon["Sp. Atk"],
            sp_def=pokemon["Sp. Def"],
            speed=pokemon["Speed"],
            generation=pokemon["Generation"],
            legendary=pokemon["Legendary"],
        )
         db.session.add(pokemon_data)
    db.session.commit()

get_load_data()
