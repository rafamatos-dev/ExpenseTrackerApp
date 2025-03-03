# routes/CategoryRoutes.py
from flask import Blueprint, request, jsonify
from app.models.CategoryHandler import CategoryHandler
from app.models.ExpenseHandler import ExpenseHandler
from app.models.Category import Category
from bson.objectid import ObjectId

# Create Blueprint
category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

# Create repository instances
category_repo = None
expense_repo = None

def init_category_routes(app, mongo):
    """Initialize category routes with application context"""
    global category_repo, expense_repo
    # Initialize repositories with the database connection
    with app.app_context():
        category_repo = CategoryHandler()
        expense_repo = ExpenseHandler()
    
    # Register the blueprint with the app
    app.register_blueprint(category_bp)


# Route to get all categories for a user
@category_bp.route('/user/<user_id>', methods=['GET'])
def get_user_categories(user_id):
    # Parse query parameters
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    sort_by = request.args.get('sort_by', 'name')
    sort_dir = int(request.args.get('sort_dir', 1))  # 1 for ascending
    
    # Get categories with pagination
    result = category_repo.find_by_user(user_id, skip, limit, sort_by, sort_dir)
    
    # Convert categories to dict for JSON serialization
    categories_dict = []
    for category in result['categories']:
        category_dict = category.to_dict()
        category_dict['_id'] = str(category_dict['_id'])
        if 'user_id' in category_dict and category_dict['user_id']:
            category_dict['user_id'] = str(category_dict['user_id'])
        category_dict['created_at'] = category_dict['created_at'].isoformat()
        categories_dict.append(category_dict)
    
    return jsonify({
        'categories': categories_dict,
        'total': result['total'],
        'skip': result['skip'],
        'limit': result['limit']
    })

# Route to create a new category
@category_bp.route('', methods=['POST'])
def create_category():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'user_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Create the category
    success, result = category_repo.create(data)
    
    if success:
        # Convert category to dict
        category_dict = result.to_dict()
        # Convert ObjectId to string for JSON serialization
        category_dict['_id'] = str(category_dict['_id'])
        if 'user_id' in category_dict and category_dict['user_id']:
            category_dict['user_id'] = str(category_dict['user_id'])
        category_dict['created_at'] = category_dict['created_at'].isoformat()
        
        return jsonify({'category': category_dict, 'message': 'Category created successfully'}), 201
    else:
        # Return validation errors
        return jsonify({'errors': result}), 400

# Route to get all categories without user filter
@category_bp.route('', methods=['GET'])
def get_all_categories():
    # Parse query parameters
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    sort_by = request.args.get('sort_by', 'name')
    sort_dir = int(request.args.get('sort_dir', 1))  # 1 for ascending
    
    # Query for all categories without user filter
    cursor = category_repo.collection.find()
    
    # Apply sorting
    cursor = cursor.sort(sort_by, sort_dir)
    
    # Apply pagination
    total_count = category_repo.collection.count_documents({})
    cursor = cursor.skip(skip).limit(limit)
    
    # Convert to Category objects
    categories = [Category.from_dict(category_data) for category_data in cursor]
    
    # Convert categories to dict for JSON serialization
    categories_dict = []
    for category in categories:
        category_dict = category.to_dict()
        category_dict['_id'] = str(category_dict['_id'])
        if 'user_id' in category_dict and category_dict['user_id']:
            category_dict['user_id'] = str(category_dict['user_id'])
        category_dict['created_at'] = category_dict['created_at'].isoformat()
        categories_dict.append(category_dict)
    
    return jsonify({
        'categories': categories_dict,
        'total': total_count,
        'skip': skip,
        'limit': limit
    })

# Route to get a specific category
@category_bp.route('/<category_id>', methods=['GET'])
def get_category(category_id):
    category = category_repo.find_by_id(category_id)
    
    if category:
        category_dict = category.to_dict()
        category_dict['_id'] = str(category_dict['_id'])
        if 'user_id' in category_dict and category_dict['user_id']:
            category_dict['user_id'] = str(category_dict['user_id'])
        category_dict['created_at'] = category_dict['created_at'].isoformat()
        
        return jsonify({'category': category_dict})
    
    return jsonify({'error': 'Category not found'}), 404

# Route to update a category
@category_bp.route('/<category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.json
    
    # Update the category
    success, result = category_repo.update(category_id, data)
    
    if success:
        category_dict = result.to_dict()
        category_dict['_id'] = str(category_dict['_id'])
        if 'user_id' in category_dict and category_dict['user_id']:
            category_dict['user_id'] = str(category_dict['user_id'])
        category_dict['created_at'] = category_dict['created_at'].isoformat()
        
        return jsonify({'category': category_dict, 'message': 'Category updated successfully'})
    else:
        return jsonify({'errors': result}), 400

# Route to delete a category
@category_bp.route('/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    # First check if there are any expenses with this category
    # You may want to implement a find_by_category method in ExpenseRepository
    # For now we'll query directly
    
    # Check for any expenses with this category
    expenses_with_category = expense_repo.find_by_user(
        user_id=None,  # Not filtering by user
        category_id=category_id,
        limit=1  # Just need to know if any exist
    )
    
    if expenses_with_category['total'] > 0:
        return jsonify({
            'error': 'Cannot delete category because it has associated expenses. ' +
                    'Please reassign or delete these expenses first.'
        }), 400
    
    # If no expenses use this category, proceed with deletion
    success = category_repo.delete(category_id)
    
    if success:
        return jsonify({'message': 'Category deleted successfully'})
    
    return jsonify({'error': 'Category not found or could not be deleted'}), 404

# Route to create default categories for a user
@category_bp.route('/defaults/<user_id>', methods=['POST'])
def create_default_categories(user_id):
    count = category_repo.create_default_categories(user_id)
    
    return jsonify({
        'message': f'Created {count} default categories for user',
        'count': count
    })