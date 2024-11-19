from flask import Blueprint, jsonify, request
from app.models import mongo
from bson.objectid import ObjectId

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
    

@bp.route('/', methods=['GET'])
def get_all_instructions():
    try:
        collection = mongo.db['instructions']
        instructions = list(collection.find({}, {'_id': 1, 'failure': 1, 'details': 1}))
        
        # Convert ObjectId to string for JSON serialization
        for instruction in instructions:
            instruction['_id'] = str(instruction['_id'])
        
        return jsonify({'instructions': instructions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<string:instruction_id>', methods=['GET'])
def get_instruction_by_id(instruction_id):
    try:
        collection = mongo.db['instructions']
        instruction = collection.find_one({'_id': ObjectId(instruction_id)})
        
        if not instruction:
            return jsonify({'error': 'Instruction not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        instruction['_id'] = str(instruction['_id'])
        
        return jsonify({'instruction': instruction}), 200

    except Exception as e:
        return jsonify({'error': 'Invalid ID format' if 'ObjectId' in str(e) else str(e)}), 400
    

@bp.route('/<string:instruction_id>', methods=['PUT'])
def update_instruction(instruction_id):
    try:
        # Parse JSON data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Build the update object
        update_fields = {}

        # Optional: Update the 'details' field if present
        if 'details' in data:
            if not isinstance(data['details'], list):
                return jsonify({'error': "'details' must be a list"}), 400
            
            update_fields['details'] = data['details']

        # Ensure there is something to update
        if not update_fields:
            return jsonify({'error': 'No valid fields provided for update'}), 400

        # Update the document in MongoDB
        collection = mongo.db['instructions']
        result = collection.update_one(
            {'_id': ObjectId(instruction_id)}, 
            {'$set': update_fields}       
        )
        
        # Check if the document was found and updated
        if result.matched_count == 0:
            return jsonify({'error': 'Instruction not found'}), 404
        
        return jsonify({'message': 'Instruction updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Invalid ID format' if 'ObjectId' in str(e) else str(e)}), 400