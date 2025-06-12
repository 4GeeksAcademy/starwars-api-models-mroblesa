"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, FavPeople, FavPlanet
from sqlalchemy import select
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# get all users

@app.route('/users', methods=['GET'])
def handle_get_users():

    all_users = db.session.execute(select(User)).scalars().all()

    response_body = {
        "users": [user.serialize() for user in all_users],
        "message": 'Everything went well'
    }
    return jsonify(response_body), 200


# get planets

@app.route('/planets', methods=['GET'])
def handle_get_planets():

    all_planets = Planets.query.all()

    response_body = {
        "planets": [planet.serialize() for planet in all_planets],
        "message": 'Everything went well'
    }
    return jsonify(response_body), 200

# get planets id


@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_get_single_planet(planet_id):

    planet = Planets.query.get(planet_id)
    if not planet:
        return 'The planets does not exist, please add one', 404

    response_body = {
        "planet_id": planet.serialize(),
        "message": 'Everything went well'
    }

    return jsonify(response_body), 200

# get people


@app.route('/people', methods=['GET'])
def handle_get_people():

    all_people = People.query.all()

    response_body = {
        "people": [character.serialize() for character in all_people],
        "message": 'Everything went well'
    }

    return jsonify(response_body), 200

# get people id


@app.route('/people/<int:people_id>', methods=['GET'])
def handle_get_single_character(people_id):

    character = People.query.get(people_id)
    if not character:
        return 'The character does not exist, please add one', 404

    response_body = {
        "people_id": character.serialize(),
        "message": 'Everything went well'
    }

    return jsonify(response_body), 200

# get/users/favorites/user.id

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def handle_get_user_favorites(user_id):

    user = User.query.get(user_id)
    if not user:
        return 'User not found', 404

    favorite_people = FavPeople.query.all()
    favorite_planet = FavPlanet.query.all()

    response_body = {
        "user_id": user.serialize(),
        "favorite_people": [fav.serialize() for fav in favorite_people],
        "favorite_planet": [fav.serialize() for fav in favorite_planet],
        "message": 'Everything went well'
    }

    return jsonify(response_body), 200

# post/users/<int:user_id>/favorite_planets

@app.route('/users/<int:user_id>/favorite-planets', methods=['POST'])
def add_favorite_planet(user_id):
    data = request.get_json()
    planet_id = data.get('planet_id')

    if not data or 'planet_id' not in data:
        return jsonify({"error": "Missing planet_id in request body"}), 400
    
    planet_id = data['planet_id']

    if not planet_id:
        return jsonify({"error": "Planet ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    existing_fav = FavPlanet.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"error": "Planet already in favorites"}), 400

    new_favorite = FavPlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)

    try:
        db.session.commit()
        return jsonify({
            "message": "Planet added to favorites",
            "favorite": new_favorite.serialize()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# post/favorite/people/people.id

@app.route('/users/<int:user_id>/favorite-people', methods=['POST'])
def add_favorite_people(user_id):
    data = request.get_json()
    people_id = data.get('people_id')
    
    if not people_id:
        return jsonify({"error": "People ID is required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    
    existing_fav = FavPeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if existing_fav:
        return jsonify({"error": "Person already in favorites"}), 400
    
    new_favorite = FavPeople(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Person added to favorites",
            "favorite": new_favorite.serialize()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# delete/favorite/planet/user.id/planet.id

@app.route('/users/<int:user_id>/favorite-planets/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite = FavPlanet.query.filter_by(
        user_id=user_id, 
        planet_id=planet_id
    ).first()
    
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({
            "message": "Planet removed from favorites",
            "deleted_id": planet_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# delete/favorite/people/people.id/people.id

@app.route('/users/<int:user_id>/favorite-people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(user_id, people_id):
    favorite = FavPeople.query.filter_by(
        user_id=user_id, 
        people_id=people_id
    ).first()
    
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({
            "message": "Person removed from favorites",
            "deleted_id": people_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
