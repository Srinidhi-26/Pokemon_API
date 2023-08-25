# Installed Imports
from flask import Blueprint, request, url_for
from sqlalchemy.exc import SQLAlchemyError
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
def protected_route():
    return {"message": "You have access to this route"}


@pokeman_api.route("/", methods=["GET", "POST"])
@auth_required
def get_or_create_pokemon():
    if request.method == "GET":
        pokemon_id = request.args.get("pokemon_id", type=int)
        if pokemon_id:
            pokemon = Pokemon.query.filter_by(id=pokemon_id).first()
            if not pokemon:
                raise PokemonException(f"Pokemon ID {pokemon_id} doesn't exist.", 404)

            pokemon_schema = PokemonSchema()
            data = pokemon_schema.dump(pokemon)

            return {
                "success": True,
                "pokemon_data": data,
                "message": f"Pokemon with ID {pokemon_id} Retrieved Successfully.",
            }, 200
        else:
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

            pokemon_query = pokemon_query.order_by(
                getattr(getattr(Pokemon, sort), order)()
            )

            if search:
                pokemon_query = pokemon_query.filter(Pokemon.name.ilike(f"%{search}%"))

            if type_1:
                pokemon_query = pokemon_query.filter(
                    Pokemon.Type_1.ilike(f"%{type_1}%")
                )

            if type_2:
                pokemon_query = pokemon_query.filter(
                    Pokemon.Type_2.ilike(f"%{type_2}%")
                )

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
                raise PokemonException("No Pokemon data Present", 404)

            if pokemon_data.has_next:
                next_url = url_for(
                    "pokeman_api.get_or_create_pokemon",
                    page=pokemon_data.next_num,
                    _external=True,
                )
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

    elif request.method == "POST":
        """
        This API creates Pokemons. when using this API then pass all values.
        Payload :
            pokemon_data (list of dicts): List of Pokémon data with keys like rank, name, type_1, etc.
        """
        data = request.json.get("pokemon_data")

        if not data or not isinstance(data, list):
            raise PokemonException(
                "Invalid payload format. 'pokemon_data' should be a list of Pokémon data.",
                400,
            )

        pokemons = []
        for pokemon_data in data:
            pokemon = {
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
            }

            if not all(pokemon["name"].isalpha() for pokemon in pokemons):
                raise PokemonException(
                    "Invalid Name Format",
                    400,
                )

            pokemons.append(pokemon)

        db.session.bulk_insert_mappings(Pokemon, pokemons)
        db.session.commit()

        return {
            "success": True,
            "message": "Pokemon created successfully.",
        }, 201


# @pokeman_api.route("/", methods=["GET"])
# @pokeman_api.route("/<int:pokemon_id>", methods=["GET"])
# @auth_required
# def get_pokemon(pokemon_id=None):
#     """
#     Get Pokemon data. It works on both single/multiple entities.
#     Params:
#         limit(int): number of records per page
#         sort(str): column to sort on.
#         order(str): desc/asc
#         page_num(int): page number to fetch.
#         search(str): search str in pokemon name.
#         pokemon_id(int): pokemon id to get its visible property
#     """
#     limit = request.args.get("limit", app.config.get("PAGE_LIMIT"), type=int)
#     page_num = request.args.get("page", 1, type=int)
#     sort = request.args.get("sort", "name")
#     order = request.args.get("order", "asc")
#     search = request.args.get("search")
#     type_1 = request.args.get("type_1")
#     type_2 = request.args.get("type_2")
#     total = request.args.get("total")
#     speed = request.args.get("speed")
#     generation = request.args.get("generation")
#     legendary = request.args.get("legendary")
#     pokemon_query = Pokemon.query

#     if pokemon_id:
#         pokemon_query = pokemon_query.filter(Pokemon.id == pokemon_id)
#         if not pokemon_query.first():
#             raise PokemonException(
#                 f" Pokemon ID {pokemon_id} doesn't exist.",
#                 404,
#             )

#     pokemon_query = pokemon_query.order_by(getattr(getattr(Pokemon, sort), order)())

#     if search:
#         pokemon_query = pokemon_query.filter(Pokemon.name.ilike(f"%{search}%"))

#     if type_1:
#         pokemon_query = pokemon_query.filter(Pokemon.Type_1.ilike(f"%{type_1}%"))

#     if type_2:
#         pokemon_query = pokemon_query.filter(Pokemon.Type_2.ilike(f"%{type_2}%"))

#     if total:
#         pokemon_query = pokemon_query.filter(Pokemon.Total == total)

#     if speed:
#         pokemon_query = pokemon_query.filter(Pokemon.Speed == speed)

#     if generation:
#         pokemon_query = pokemon_query.filter(Pokemon.generation == generation)

#     if legendary:
#         legendary = ast.literal_eval(legendary)
#         pokemon_query = pokemon_query.filter(Pokemon.legendary.is_(legendary))

#     pokemon_data = pokemon_query.paginate(
#         page=page_num, per_page=limit, error_out=False
#     )

#     pokemons_schema = PokemonSchema(many=True)
#     data = pokemons_schema.dump(pokemon_data.items)

#     if len(data) == 0:
#         raise PokemonException(
#             "No Pokemon data Present",
#             404,
#         )

#     if pokemon_data.has_next:
#         next_url = url_for(
#             "pokeman_api.get_pokemon", page=pokemon_data.next_num, _external=True
#         )
#     else:
#         next_url = None

#     return {
#         "success": True,
#         "pokemon_data": data,
#         "sort": sort,
#         "order": order,
#         "page": pokemon_data.page,
#         "next_page": next_url,
#         "total_pages": pokemon_data.pages,
#         "total": pokemon_data.total,
#         "message": "Pokemon Data Retrieved Successfully.",
#     }, 200


# @pokeman_api.route("/", methods=["POST"])
# @auth_required
# def create_pokemon():
#     """
#     This API creates Pokemons. when using this api then pass all values.
#     Payload :
#         rank (int): rank of the pokemon
#         name (str): name of the pokemon
#         type_1 (str): type_1 for pokemon
#         type_2 (str): type_2 for pokemon
#         total(int): total of the pokemon
#         hp(int): hp for the pokemon
#         attack (int): attack for the pokemon
#         defense(int): defense for the pokemon
#         sp_Atk(int): sp_atk for the pokemon
#         sp_Def(int): sp_def for the pokemon
#         speed(int): speed of the pokemon
#         generation(int): generation of the pokemon
#         legendary(int): legendary of the pokemon
#     """
#     data = request.json.get("pokemon_data")
#     pokemons = list(
#         map(
#             lambda pokemon_data: {
#                 "rank": pokemon_data.get("rank"),
#                 "name": pokemon_data.get("name"),
#                 "type_1": pokemon_data.get("type_1"),
#                 "type_2": pokemon_data.get("type_2"),
#                 "total": pokemon_data.get("total"),
#                 "hp": pokemon_data.get("hp"),
#                 "attack": pokemon_data.get("attack"),
#                 "defense": pokemon_data.get("defense"),
#                 "sp_atk": pokemon_data.get("sp_atk"),
#                 "sp_def": pokemon_data.get("sp_def"),
#                 "speed": pokemon_data.get("speed"),
#                 "generation": pokemon_data.get("generation"),
#                 "legendary": pokemon_data.get("legendary"),
#             },
#             data,
#         )
#     )
#     if not all(pokemon["name"].isalpha() for pokemon in pokemons):
#         raise PokemonException(
#             "Invalid Name Format",
#             404,
#         )

#     db.session.bulk_insert_mappings(Pokemon, pokemons)
#     db.session.commit()

#     return {
#         "success": True,
#         "message": "Pokemon created successfully.",
#     }, 201


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

    insert_values = []
    update_values = []

    for pokemon_info in pokemon_data:
        pokemon_id = pokemon_info.get("id")
        existing_pokemon = Pokemon.query.get(pokemon_id) if pokemon_id else None

        if existing_pokemon:
            for column in Pokemon.__table__.columns:
                column_name = column.name
                if column_name != "name":
                    column_value = pokemon_info.get(
                        column_name, getattr(existing_pokemon, column_name)
                    )
                    setattr(existing_pokemon, column_name, column_value)
            update_values.append(existing_pokemon)

        else:
            pokemon_info.pop("id", None)
            new_pokemon = Pokemon()
            for column_name, column_value in pokemon_info.items():
                setattr(new_pokemon, column_name, column_value)
            insert_values.append(new_pokemon)

    if insert_values:
        db.session.add_all(insert_values)
    if update_values:
        db.session.bulk_save_objects(update_values)

    db.session.commit()

    return {"success": True, "message": "Pokemon added/updated successfully"}, 200


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
