#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)  # Initialize the API

class HeroResource(Resource):
    def get(self, id=None):
        if id is None:
            heroes = Hero.query.all()
            return jsonify([hero.to_dict() for hero in heroes])
        else:
            hero = Hero.query.get(id)
            if hero:
                return jsonify(hero.to_dict())
            return {'error': 'Hero not found'}, 404

class PowerResource(Resource):
    def get(self, id=None):
        if id is None:
            powers = Power.query.all()
            return jsonify([power.to_dict() for power in powers])
        else:
            power = Power.query.get(id)
            if power:
                return jsonify(power.to_dict())
            return {'error': 'Power not found'}, 404

    def patch(self, id):
        power = Power.query.get(id)
        if power is None:
            return {'error': 'Power not found'}, 404

        data = request.get_json()
        description = data.get('description')

        if description:
            power.description = description
            db.session.commit()
            return jsonify(power.to_dict())

        return {'errors': ['Validation errors']}, 400

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')
        strength = data.get('strength')

        if not hero_id or not power_id or not strength:
            return {'errors': ['Missing required fields']}, 400

        new_hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
        db.session.add(new_hero_power)
        db.session.commit()

        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        return {
            "id": new_hero_power.id,
            "hero_id": hero_id,
            "power_id": power_id,
            "strength": strength,
            "hero": hero.to_dict(),
            "power": power.to_dict()
        }, 201

# Register resources with their respective endpoints
api.add_resource(HeroResource, '/heroes', '/heroes/<int:id>')
api.add_resource(PowerResource, '/powers', '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)

