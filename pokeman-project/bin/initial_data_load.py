#!/usr/bin/env python3
import os
import sys
import json
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
            Name=pokemon["Name"],
            Type_1=pokemon["Type 1"],
            Type_2=pokemon["Type 2"],
            Total=pokemon["Total"],
            HP=pokemon["HP"],
            Attack=pokemon["Attack"],
            Defense=pokemon["Defense"],
            Sp_Atk=pokemon["Sp. Atk"],
            Sp_Def=pokemon["Sp. Def"],
            Speed=pokemon["Speed"],
            Generation=pokemon["Generation"],
            Legendary=pokemon["Legendary"],
        )
        db.session.add(pokemon_data)
    db.session.commit()

get_load_data()
