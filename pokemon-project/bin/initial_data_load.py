#!/usr/bin/env python3
import os
import sys
import requests

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(parentdir)
sys.path.insert(0, parentdir)

from app import app
from app.models import db, Pokemon

url = "https://coralvanda.github.io/pokemon_data.json"
response = requests.get(url)
data = response.json()

def get_load_data():
    for pokemon in data:
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
