# Installed Imports
from flask import Blueprint, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
import ast

# Custom Imports
from app import app
from app.models import Pokemon, db, PokemonSchema
from app.auth import auth_required


pokeman_api = Blueprint("pokeman_api", __name__, url_prefix="/pokemons")


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
@pokeman_api.route("/<int:pokemon_id>", methods=["GET"])
@auth_required
def get_pokemon(pokemon_id=None):
    """
    Get Pokemon data. It works on both single/multiple entities.
    Params:
        limit(int): number of records per page
        sort(str): column to sort on.
        order(str): desc/asc
        page_num(int): page number to fetch.
        search(str): search str in pokemon name.
        pokemon_id(int): pokemon id to get its visible property
    """
    limit = request.args.get("limit", app.config.get("PAGE_LIMIT"), type=int)
    page_num = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "name")
    order = request.args.get("order", "asc")
    search = request.args.get("search")
    type_1 = request.args.get("type_1")
    type_2 = request.args.get("type_2")
    total = request.args.get("total")
    speed = request.args.get("speed")
    generation = request.args.get("generation")
    legendary = request.args.get("legendary")
    pokemon_query = Pokemon.query

    if pokemon_id:
        pokemon_query = pokemon_query.filter(Pokemon.id == pokemon_id)
        if not pokemon_query.first():
            raise PokemonException(
                f" Pokemon ID {pokemon_id} doesn't exist.",
                404,
            )

    pokemon_query = pokemon_query.order_by(getattr(getattr(Pokemon, sort), order)())

    if search:
        pokemon_query = pokemon_query.filter(Pokemon.name.ilike(f"%{search}%"))

    if type_1:
        pokemon_query = pokemon_query.filter(Pokemon.Type_1.ilike(f"%{type_1}%"))

    if type_2:
        pokemon_query = pokemon_query.filter(Pokemon.Type_2.ilike(f"%{type_2}%"))

    if total:
        pokemon_query = pokemon_query.filter(Pokemon.Total == total)

    if speed:
        pokemon_query = pokemon_query.filter(Pokemon.Speed == speed)

    if generation:
        pokemon_query = pokemon_query.filter(Pokemon.generation == generation)

    if legendary:
        legendary = ast.literal_eval(legendary)
        pokemon_query = pokemon_query.filter(Pokemon.legendary.is_(legendary))

    pokemon_data = pokemon_query.paginate(
        page=page_num, per_page=limit, error_out=False
    )

    pokemons_schema = PokemonSchema(many=True)
    data = pokemons_schema.dump(pokemon_data.items)

    if len(data) == 0:
        raise PokemonException(
            "No Pokemon data Present",
            404,
        )

    if pokemon_data.has_next:
        next_url = url_for("pokeman_api.get_pokemon", page=pokemon_data.next_num, _external= True)
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
        "message": "Pokemon Data Retrieved Successfully.",
    }, 200


@pokeman_api.route("/", methods=["POST"])
@auth_required
def create_pokemon():
    """
    This API creates Pokemons. when using this api then pass all values.
    Payload :
        rank (int): rank of the pokemon
        name (str): name of the pokemon
        type_1 (str): type_1 for pokemon
        type_2 (str): type_2 for pokemon
        total(int): total of the pokemon
        hp(int): hp for the pokemon
        attack (int): attack for the pokemon
        defense(int): defense for the pokemon
        sp_Atk(int): sp_atk for the pokemon
        sp_Def(int): sp_def for the pokemon
        speed(int): speed of the pokemon
        generation(int): generation of the pokemon
        legendary(int): legendary of the pokemon
    """
    data = request.json.get("pokemon_data")
    pokemons = list(
        map(
            lambda pokemon_data: {
                "rank": pokemon_data.get("rank"),
                "name": pokemon_data.get("name"),
                "type_1": pokemon_data.get("type_1"),
                "type_2": pokemon_data.get("type_2"),
                "total": pokemon_data.get("total"),
                "hp": pokemon_data.get("hp"),
                "attack": pokemon_data.get("attack"),
                "defense": pokemon_data.get("defense"),
                "sp_atk": pokemon_data.get("sp_atk"),
                "sp_def": pokemon_data.get("sp_def"),
                "speed": pokemon_data.get("speed"),
                "generation": pokemon_data.get("generation"),
                "legendary": pokemon_data.get("legendary"),
            },
            data,
        )
    )
    if not all(pokemon["name"].isalpha() for pokemon in pokemons):
        raise PokemonException(
            "Invalid Name Format",
            404,
        )

    db.session.bulk_insert_mappings(Pokemon, pokemons)
    db.session.commit()

    return {
        "success": True,
        "message": "Pokemon created successfully.",
    }, 201


@pokeman_api.route("/", methods=["PUT"])
@auth_required
def upsert():
    """
    This API updates if the Pokémon is already present.
    If the Pokémon is not present, it will be inserted.
    Params: {
        name: Name of the Pokémon
        rank (int): Rank of the Pokémon
        type_1 (str): Type 1 of the Pokémon
        type_2 (str): Type 2 of the Pokémon
        total(int): total of the pokemon
        hp(int): hp for the pokemon
        attack (int): attack for the pokemon
        defense(int): defense for the pokemon
        sp_Atk(int): sp_atk for the pokemon
        sp_Def(int): sp_def for the pokemon
        speed(int): speed of the pokemon
        generation(int): generation of the pokemon
        legendary(int): legendary of the pokemon
    }
    """
    pokemon_data = request.json.get("pokemon_data")
    values = []
    for pokemon_info in pokemon_data:
        existing_pokemon = Pokemon.query.filter_by(name=pokemon_info.get("name")).first()
        if existing_pokemon:
            for column in Pokemon.__table__.columns:
                column_name = column.name
                if column_name != "id" and column_name != "name" and column_name != "type_1":
                    column_value = pokemon_info.get(column_name, getattr(existing_pokemon, column_name))
                else:
                    column_value = pokemon_info.get(column_name, getattr(existing_pokemon, column_name))
                
                pokemon_info[column_name] = column_value

        values.append(pokemon_info)

    insert_stmt = insert(Pokemon).values(values)

    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["name"],
        set_=insert_stmt.excluded
    )

    db.session.execute(do_update_stmt)
    db.session.commit()

    return {
        "success": True, 
        "message": "Pokémon added/updated successfully"
        }, 200


@pokeman_api.route("/", methods=["DELETE"])
@pokeman_api.route("/<int:pokemon_id>", methods=["DELETE"])
@auth_required
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
            raise PokemonException(
                f"Pokemon ID {pokemon_id} doesn't exist.",
                404,
            )
        db.session.delete(pokemon)

    else:
        pokemon_ids = request.get_json().get("pokemon_ids")
        delete_all = request.get_json().get("delete_all")
        if delete_all:
            Pokemon.query.delete()

        if not pokemon_ids:
            raise PokemonException(
                f" No Pokemons ID's Provided.",
                404,
            )
        deleted_count = Pokemon.query.filter(Pokemon.id.in_(pokemon_ids)).delete(
            synchronize_session=False
        )

    db.session.commit()
    return {
        "success": True,
        "message": f" Pokemon data deleted successfully.",
    }, 200
