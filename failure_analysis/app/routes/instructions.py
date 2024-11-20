from flask import Blueprint, jsonify, request
from app.models import mongo
from bson.objectid import ObjectId

bp = Blueprint('instructions', __name__, url_prefix='/instructions')

@bp.route('/add', methods=['POST'])
def add_instruction():
    """Endpoint to add a new instruction to the database."""
    try:
        # Parse JSON data from the request
        data = request.get_json()
        
        if not data:  # Check if data is None
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Validate that required keys are present
        if not all(key in data for key in ('failure', 'details')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not isinstance(data['details'], list) or not data['details']:
            return jsonify({'error': "'details' must be a non-empty list"}), 400
        
        # Validate each detail entry
        for detail in data['details']:
            if not all(detail.get(key) for key in ('reason', 'solution')):
                return jsonify({'error': "Each detail must have 'reason', 'solution'"}), 400
            
            # Validate 'tags' only if present
            if 'tags' in detail and not isinstance(detail['tags'], list):
                return jsonify({'error': "'tags', if present, must be a list"}), 400
        
        # Check for uniqueness of the failure name
        collection = mongo.db['instructions']
        existing_instruction = collection.find_one({'failure': data['failure']})
        if existing_instruction:
            return jsonify({'error': f"An instruction with the failure '{data['failure']}' already exists"}), 409
        
        # Construct the instruction object
        new_instruction = {
            'failure': data['failure'],
            'details': data['details']  # Includes reason, solution, and tags
        }
        
        # Insert into MongoDB
        result = collection.insert_one(new_instruction)
        
        return jsonify({'message': 'Instruction added successfully', 'id': str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['GET'])
def get_all_instructions():
    """Fetch all instructions from the database."""
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
    """Fetch a single instruction by ID."""
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

@bp.route('/failure/<string:failure_name>', methods=['GET'])
def get_instructions_by_failure(failure_name):
    """ Fetch instructions based on the failure name. """
    try:
        collection = mongo.db['instructions']
        # Query MongoDB for documents with the matching failure
        instructions = list(collection.find({'failure': failure_name}, {'_id': 1, 'failure': 1, 'details': 1}))
        
        # If no documents are found, return a 404 error
        if not instructions:
            return jsonify({'error': 'No instructions found for the given failure'}), 404
        
        # Convert ObjectId to string for JSON serialization
        for instruction in instructions:
            instruction['_id'] = str(instruction['_id'])
        
        return jsonify({'instructions': instructions}), 200

    except Exception as e:
        # Catch any unexpected errors
        return jsonify({'error': str(e)}), 500

    

@bp.route('/<string:instruction_id>', methods=['PUT'])
def update_instruction(instruction_id):
    """Update an instruction by ID."""
    try:
        # Parse JSON data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Build the update object
        update_fields = {}

        # Optional: Update the 'failure' field if present
        if 'failure' in data and isinstance(data['failure'], str) and data['failure'].strip():
            update_fields['failure'] = data['failure']

        # Optional: Update the 'details' field if present
        if 'details' in data:
            if not isinstance(data['details'], list):
                return jsonify({'error': "'details' must be a list"}), 400
            
            # Validate each detail in the list
            for detail in data['details']:
                if not all(key in detail for key in ('reason', 'solution')):
                    return jsonify({'error': "Each detail must have 'reason' and 'solution'"}), 400
                if 'tags' in detail and not isinstance(detail['tags'], list):
                    return jsonify({'error': "'tags', if present, must be a list"}), 400
            
            update_fields['details'] = data['details']

        # Ensure there is something to update
        if not update_fields:
            return jsonify({'error': 'No valid fields provided for update'}), 400

        # Update the document in MongoDB
        collection = mongo.db['instructions']
        result = collection.update_one(
            {'_id': ObjectId(instruction_id)},  # Match by ID
            {'$set': update_fields}            # Apply updates
        )
        
        # Check if the document was found and updated
        if result.matched_count == 0:
            return jsonify({'error': 'Instruction not found'}), 404
        
        return jsonify({'message': 'Instruction updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Invalid ID format' if 'ObjectId' in str(e) else str(e)}), 400


@bp.route('/<string:instruction_id>', methods=['DELETE'])
def delete_instruction_by_id(instruction_id):
    """Delete an instruction by ID."""
    try:
        collection = mongo.db['instructions']
        result = collection.delete_one({'_id': ObjectId(instruction_id)})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Instruction not found'}), 404
        
        return jsonify({'message': 'Instruction deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Invalid ID format' if 'ObjectId' in str(e) else str(e)}), 400

