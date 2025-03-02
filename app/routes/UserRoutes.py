from flask import Blueprint, request, jsonify, current_app
from models.UserHandler import UserRepository
from models.User import User
from bson.json_util import dumps
import json

# Create Blueprint
user_bp = Blueprint('users', __name__, url_prefix='/api/users')

# Create repository instance
user_repo = None

def init_user_routes(app, mongo):
    """Initialize user routes with application context"""
    global user_repo
    # Initialize repository with the database connection
    with app.app_context():
        user_repo = UserRepository()
    
    # Register the blueprint with the app
    app.register_blueprint(user_bp)

# Route to register a new user
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Create the user
    success, result = user_repo.create(data)
    
    if success:
        # Convert user to dict without private info
        user_dict = result.to_dict()
        # Convert ObjectId to string for JSON serialization
        user_dict['_id'] = str(user_dict['_id'])
        return jsonify({'user': user_dict, 'message': 'User registered successfully'}), 201
    else:
        # Return validation errors
        return jsonify({'errors': result}), 400

# Route to authenticate a user
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Check for username/email and password
    if 'password' not in data:
        return jsonify({'error': 'Password is required'}), 400
    
    if 'username' in data:
        user = user_repo.find_by_username(data['username'])
    elif 'email' in data:
        user = user_repo.find_by_email(data['email'])
    else:
        return jsonify({'error': 'Username or email is required'}), 400
    
    # Check if user exists and password is correct
    if user and user.check_password(data['password']):
        # Return user data without sensitive info
        user_dict = user.to_dict()
        user_dict['_id'] = str(user_dict['_id'])
        
        # In a real app, you would generate a JWT token here
        return jsonify({
            'message': 'Login successful',
            'user': user_dict
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Route to get user profile
@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    user = user_repo.find_by_id(user_id)
    
    if user:
        user_dict = user.to_dict()
        user_dict['_id'] = str(user_dict['_id'])
        return jsonify({'user': user_dict})
    
    return jsonify({'error': 'User not found'}), 404

# Route to update user
@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    
    # Update the user
    success, result = user_repo.update(user_id, data)
    
    if success:
        user_dict = result.to_dict()
        user_dict['_id'] = str(user_dict['_id'])
        return jsonify({'user': user_dict, 'message': 'User updated successfully'})
    else:
        return jsonify({'errors': result}), 400

# Route to delete user
@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    success = user_repo.delete(user_id)
    
    if success:
        return jsonify({'message': 'User deleted successfully'})
    
    return jsonify({'error': 'User not found or could not be deleted'}), 404

# Route to list users (with pagination)
@user_bp.route('', methods=['GET'])
def list_users():
    # Parse query parameters
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    sort_by = request.args.get('sort_by', 'username')
    sort_dir = int(request.args.get('sort_dir', 1))  # 1 for ascending, -1 for descending
    
    # Get users with pagination
    result = user_repo.list_all(skip, limit, sort_by, sort_dir)
    
    # Convert users to dict for JSON serialization
    users_dict = []
    for user in result['users']:
        user_dict = user.to_dict()
        user_dict['_id'] = str(user_dict['_id'])
        users_dict.append(user_dict)
    
    return jsonify({
        'users': users_dict,
        'total': result['total'],
        'skip': result['skip'],
        'limit': result['limit']
    })