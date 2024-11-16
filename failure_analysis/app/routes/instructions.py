from flask import Blueprint, jsonify, request
from app.models import mongo

bp = Blueprint('instructions', __name__, url_prefix='/instructions')

@bp.route('/add', methods=['POST'])
def add_instruction():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        
        # Check for uniqueness of the failure name
        collection = mongo.db['instructions']

        # Construct the instruction object
        new_instruction = {
            'failure': data['failure'],
            'details': data['details']
        }
        
        # Insert into MongoDB
        result = collection.insert_one(new_instruction)
        
        return jsonify({'message': 'Instruction added successfully', 'id': str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500