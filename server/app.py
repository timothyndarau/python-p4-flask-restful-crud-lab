#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)


api.add_resource(PlantByID, '/plants/<int:id>')

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['plants_db']
collection = db['plants']

# Update Route (PATCH)
@app.route('/plants/<string:id>', methods=['PATCH'])
def update_plant(id):
    try:
        updated_data = request.get_json()
        plant = collection.find_one_and_update(
            {'_id': ObjectId(id)},
            {'$set': updated_data},
            return_document=True
        )

        if not plant:
            return jsonify({'error': 'Plant not found'}), 404

        return jsonify(plant)
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Internal server error'}), 500

# Destroy Route (DELETE)
@app.route('/plants/<string:id>', methods=['DELETE'])
def delete_plant(id):
    try:
        result = collection.delete_one({'_id': ObjectId(id)})

        if result.deleted_count == 0:
            return '', 204  # No Content
        else:
            return jsonify({'error': 'Plant not found'}), 404
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
