# routes/ExpenseRoutes.py
from flask import Blueprint, request, jsonify
from app.models.ExpenseHandler import ExpenseHandler
from bson.objectid import ObjectId
from datetime import datetime
import json

# Create Blueprint
expense_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

# Create repository instance
expense_repo = None

def init_expense_routes(app, mongo):
    """Initialize expense routes with application context"""
    global expense_repo
    # Initialize repository with the database connection
    with app.app_context():
        expense_repo = ExpenseHandler()
    
    # Register the blueprint with the app
    app.register_blueprint(expense_bp)

# Helper function to parse date strings
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return None

# Route to create a new expense
@expense_bp.route('', methods=['POST'])
def create_expense():
    data = request.json
    
    # Validate required fields
    required_fields = ['amount', 'description', 'category_id', 'user_id']
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Parse date if provided
    if 'date' in data and data['date']:
        data['date'] = parse_date(data['date'])
    
    # Create the expense
    success, result = expense_repo.create(data)
    
    if success:
        # Convert expense to dict
        expense_dict = result.to_dict()
        # Convert ObjectId and datetime to string for JSON serialization
        expense_dict['_id'] = str(expense_dict['_id'])
        expense_dict['category_id'] = str(expense_dict['category_id'])
        expense_dict['user_id'] = str(expense_dict['user_id'])
        expense_dict['date'] = expense_dict['date'].isoformat()
        expense_dict['created_at'] = expense_dict['created_at'].isoformat()
        expense_dict['updated_at'] = expense_dict['updated_at'].isoformat()
        
        return jsonify({'expense': expense_dict, 'message': 'Expense created successfully'}), 201
    else:
        # Return validation errors
        return jsonify({'errors': result}), 400

# Route to get all expenses for a user with filtering
@expense_bp.route('/user/<user_id>', methods=['GET'])
def get_user_expenses(user_id):
    # Parse query parameters
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 50))
    sort_by = request.args.get('sort_by', 'date')
    sort_dir = int(request.args.get('sort_dir', -1))  # -1 for descending (newest first)
    
    # Parse date filters
    start_date = parse_date(request.args.get('start_date', None))
    end_date = parse_date(request.args.get('end_date', None))
    
    # Parse category filter
    category_id = request.args.get('category_id', None)
    
    # Get expenses with pagination and filtering
    result = expense_repo.find_by_user(
        user_id, skip, limit, sort_by, sort_dir, 
        start_date, end_date, category_id
    )
    
    # Convert expenses to dict for JSON serialization
    expenses_dict = []
    for expense in result['expenses']:
        expense_dict = expense.to_dict()
        expense_dict['_id'] = str(expense_dict['_id'])
        expense_dict['category_id'] = str(expense_dict['category_id'])
        expense_dict['user_id'] = str(expense_dict['user_id'])
        expense_dict['date'] = expense_dict['date'].isoformat()
        expense_dict['created_at'] = expense_dict['created_at'].isoformat()
        expense_dict['updated_at'] = expense_dict['updated_at'].isoformat()
        expenses_dict.append(expense_dict)
    
    return jsonify({
        'expenses': expenses_dict,
        'total': result['total'],
        'skip': result['skip'],
        'limit': result['limit']
    })

# Route to get a specific expense
@expense_bp.route('/<expense_id>', methods=['GET'])
def get_expense(expense_id):
    expense = expense_repo.find_by_id(expense_id)
    
    if expense:
        expense_dict = expense.to_dict()
        expense_dict['_id'] = str(expense_dict['_id'])
        expense_dict['category_id'] = str(expense_dict['category_id'])
        expense_dict['user_id'] = str(expense_dict['user_id'])
        expense_dict['date'] = expense_dict['date'].isoformat()
        expense_dict['created_at'] = expense_dict['created_at'].isoformat()
        expense_dict['updated_at'] = expense_dict['updated_at'].isoformat()
        
        return jsonify({'expense': expense_dict})
    
    return jsonify({'error': 'Expense not found'}), 404

# Route to update an expense
@expense_bp.route('/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.json
    
    # Parse date if provided
    if 'date' in data and data['date']:
        data['date'] = parse_date(data['date'])
    
    # Update the expense
    success, result = expense_repo.update(expense_id, data)
    
    if success:
        expense_dict = result.to_dict()
        expense_dict['_id'] = str(expense_dict['_id'])
        expense_dict['category_id'] = str(expense_dict['category_id'])
        expense_dict['user_id'] = str(expense_dict['user_id'])
        expense_dict['date'] = expense_dict['date'].isoformat()
        expense_dict['created_at'] = expense_dict['created_at'].isoformat()
        expense_dict['updated_at'] = expense_dict['updated_at'].isoformat()
        
        return jsonify({'expense': expense_dict, 'message': 'Expense updated successfully'})
    else:
        return jsonify({'errors': result}), 400

# Route to delete an expense
@expense_bp.route('/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    success = expense_repo.delete(expense_id)
    
    if success:
        return jsonify({'message': 'Expense deleted successfully'})
    
    return jsonify({'error': 'Expense not found or could not be deleted'}), 404

# Route to get expense summary by category
@expense_bp.route('/summary/category/<user_id>', methods=['GET'])
def get_category_summary(user_id):
    # Parse date filters
    start_date = parse_date(request.args.get('start_date', None))
    end_date = parse_date(request.args.get('end_date', None))
    
    # Get summary
    result = expense_repo.get_summary_by_category(user_id, start_date, end_date)
    
    # Convert ObjectIds to strings
    for item in result:
        item['_id'] = str(item['_id'])
    
    return jsonify({'summary': result})

# Route to get expense summary by month
@expense_bp.route('/summary/month/<user_id>', methods=['GET'])
def get_month_summary(user_id):
    # Parse year filter
    year = request.args.get('year', None)
    if year:
        year = int(year)
    
    # Get summary
    result = expense_repo.get_summary_by_month(user_id, year)
    
    return jsonify({'summary': result})

# Route to get expense summary by payment method
@expense_bp.route('/summary/payment-method/<user_id>', methods=['GET'])
def get_payment_method_summary(user_id):
    # Parse date filters
    start_date = parse_date(request.args.get('start_date', None))
    end_date = parse_date(request.args.get('end_date', None))
    
    # Get summary
    result = expense_repo.get_summary_by_payment_method(user_id, start_date, end_date)
    
    return jsonify({'summary': result})