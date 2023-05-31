# Installed Imports
from flask import Blueprint, request, url_for
import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from sqlalchemy import insert
import json
from sqlalchemy.dialects.postgresql import insert

# Custom imports
from app import app
from app.models import Pokemon, db


pokeman_api = Blueprint("pokeman_api", __name__)


class PokemonException(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


@pokeman_api.errorhandler(PokemonException)
def handle_scheduler_exception(e):
    app.logger.exception(e)
    return {"success": False, "error": e.message}, e.code


@pokeman_api.errorhandler(SQLAlchemyError)
def handle_scheduler_exception(e):
    app.logger.exception(e)
    return {"success": False, "error": f"{e.orig}"}, 400


@pokeman_api.route("/", methods=["GET"])
@pokeman_api.route("/pokemon/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id=None):
    """
    Get Pokemon data.It works on both single/multiple entities.
    Params:
        limit(int): number of records per page
        sort(str): column to sort on.
        order(str): desc/asc
        page_num(int): page number to fetch.
        search(str): search str in pokemon name.
        pokemon_id(int): pokemon id to get is visible property

    """
    limit = request.args.get("limit", app.config.get("PAGE_LIMIT"), type=int)
    page_num = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "Name")
    order = request.args.get("order", "asc")
    search = request.args.get("search")
    Type_1 = request.args.get("Type_1")
    Type_2 = request.args.get("Type_2")
    Total = request.args.get("Total")
    Speed = request.args.get("Speed")
    Generation = request.args.get("Generation")
    pokemon_data = Pokemon.query
    pokemon_data = pokemon_data.order_by(getattr(getattr(Pokemon, sort), order)())
    if pokemon_id:
        pokemon_data = pokemon_data.filter(Pokemon.id == pokemon_id)
        if not pokemon_data:
            raise PokemonException(
                f"Data Source ID {pokemon_id} doesn't exist.",
                404,
            )
    if search:
        pokemon_data = pokemon_data.filter(Pokemon.Name.ilike(f"%{search}%"))

    if Type_1:
        pokemon_data = pokemon_data.filter(Pokemon.Type_1 == Type_1)
   
    if Type_2:
        pokemon_data = pokemon_data.filter(Pokemon.Type_2 == Type_2)

    if Total:
        pokemon_data = pokemon_data.filter(Pokemon.Total == Total)

    if Speed:
        pokemon_data = pokemon_data.filter(Pokemon.Speed == Speed)

    if Generation:
        pokemon_data = pokemon_data.filter(Pokemon.Generation == Generation)

    pokemon_data = pokemon_data.paginate(page=page_num, per_page=limit, error_out=False)
    data = pokemon_data.items

    if len(data) == 0:
        raise PokemonException(
            "No Pokemon data Present",
            404,
        )

    if pokemon_data.has_next:
        next_url = url_for("pokeman_api.get_pokemon", page=pokemon_data.next_num)
    else:
        next_url = None

    return {
        "success": True,
        "pokemon_data": data,
        "sort": sort,
        "order": order,
        "page": pokemon_data.page,
        "next_page": next_url,
        "total_pages": pokemon_data.pages,
        "total": pokemon_data.total,
        "message": "Pokemon Data Retrieved Sucessfully.",
    }, 200


@pokeman_api.route("/", methods=["POST"])
def create_pokemon():
    """
    This API creates Pokemons. when using this api then pass all values.
    Payload :
        rank (int): rank of the pokemon
        Name (str): Name of the pokemon
        Type_1 (str): Type_1 for pokemon
        Type_2 (str): Type_2 for pokemon
        Total(int): Total of the pokemon
        HP(int): HP for the pokemon
        Attack (int): Attack for the pokemon
        Defense(int): Defense for the pokemon
        Sp_Atk(int): sp_atk for the pokemon
        Sp_Def(int): sp_def for the pokemon
        Speed(int): speed of the pokemon
        Generation(int): generation of the pokemon
        Legendary(int): legendary of the pokemon
    """
    data = request.json.get("pokemon_data")
    pokemons = list(
        map(
            lambda pokemon_data: {
                "rank": pokemon_data.get("rank"),
                "Name": pokemon_data.get("Name"),
                "Type_1": pokemon_data.get("Type_1"),
                "Type_2": pokemon_data.get("Type_2"),
                "Total": pokemon_data.get("Total"),
                "HP": pokemon_data.get("HP"),
                "Attack": pokemon_data.get("Attack"),
                "Defense": pokemon_data.get("Defense"),
                "Sp_Atk": pokemon_data.get("Sp_Atk"),
                "Sp_Def": pokemon_data.get("Sp_Def"),
                "Speed": pokemon_data.get("Speed"),
                "Generation": pokemon_data.get("Generation"),
                "Legendary": pokemon_data.get("Legendary"),
            },
            data,
        )
    )

    db.session.bulk_insert_mappings(Pokemon, pokemons)
    db.session.commit()

    return {
        "success": True,
        "message": "Pokemon created successfully.",
    }, 201


@pokeman_api.route("/", methods=["PUT"])
def upsert():
    """ 
    This API updates If the pokemon is already present. 
    if pokemon is not present it will insert.
    params : {
        Name: Name of the database
        rank (int): Rank of the pokemon
        Type_1 (str): Type_1 of the pokemon
        Type_2(str): Type_2 of the pokemon
        }
    """
    pokemon_data = request.json.get("pokemon_data")
    values = []
    for pokemon_data in pokemon_data:
        pokemon_values = {
            'Name': pokemon_data.get('Name'),
            'rank': pokemon_data.get('rank'),
            'Type_1': pokemon_data.get('Type_1'),
            'Type_2': pokemon_data.get('Type_2'),
            'Total': pokemon_data.get('Total'),
            'HP': pokemon_data.get('HP'),
            'Attack': pokemon_data.get('Attack'),
            'Defense': pokemon_data.get('Defense'),
            'Sp_Atk': pokemon_data.get('Sp_Atk'),
            'Sp_Def': pokemon_data.get('Sp_Def'),
            'Speed': pokemon_data.get('Speed'),
            'Generation': pokemon_data.get('Generation'),
            'Legendary': pokemon_data.get('Legendary')
        }

        values.append(pokemon_values)

    insert_stmt = insert(Pokemon).values(values)

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['Name'],
        set_={
            'rank': insert_stmt.excluded.rank,
            'Name': insert_stmt.excluded.Name,
            'Type_1': insert_stmt.excluded.Type_1,
            'Type_2': insert_stmt.excluded.Type_2,
            'Total': insert_stmt.excluded.Total,
            'HP': insert_stmt.excluded.HP,
            'Attack': insert_stmt.excluded.Attack,
            'Defense': insert_stmt.excluded.Defense,
            'Sp_Atk': insert_stmt.excluded.Sp_Atk,
            'Sp_Def': insert_stmt.excluded.Sp_Def,
            'Speed': insert_stmt.excluded.Speed,
            'Generation': insert_stmt.excluded.Generation,
            'Legendary': insert_stmt.excluded.Legendary
        }
    )

    db.session.execute(do_update_stmt)
    db.session.commit()
    return {
            "success": True,
            "message": "Pokemon added/updated successfully"
        }, 200


@pokeman_api.route("/", methods=["DELETE"])
@pokeman_api.route("/pokemon/<int:pokemon_id>", methods=["DELETE"])
def delete_pokemon(pokemon_id=None):
    """
    To delete Pokemon data.
    Path:
        pokemon_id (int, Required): id of pokemon.
        pokemon_ids (list of int, optional): list of pokemon ids, needed for bulk operation
    """
    if pokemon_id:
        pokemon = Pokemon.query.get(pokemon_id)
        if not pokemon:
            return {"message": f"Pokemon ID {pokemon_id} doesn't exist."}, 404
        db.session.delete(pokemon)

    else:
        pokemon_ids = request.get_json().get("pokemon_ids")
        delete_all = request.get_json().get("delete_all")
        if delete_all:
            Pokemon.query.delete()
            return {
                "success": True,
                "message": "All Pokemon data deleted successfully.",
            }
        if not pokemon_ids:
            return {"message": "No Pokemon's ID's Provided"}, 400
        deleted_count = Pokemon.query.filter(Pokemon.id.in_(pokemon_ids)).delete(
            synchronize_session=False
        )

    db.session.commit()
    return {
        "success": True,
        "message": f" Pokemon data deleted successfully.",
    }, 200
