# routes/ExpenseFormRoutes.py
from flask import Blueprint, render_template
import datetime

# Create Blueprint
expense_form_bp = Blueprint('expense_form', __name__)

def init_expense_form_routes(app):
    """Initialize expense form routes with application context"""
    # Register the blueprint with the app
    app.register_blueprint(expense_form_bp)

# New expense form route
@expense_form_bp.route('/expenses/new')
def new_expense():
    # Current year for footer copyright
    current_year = datetime.datetime.now().year
    
    return render_template('expense_form.html', year=current_year)

# Edit expense form route
@expense_form_bp.route('/expenses/edit/<expense_id>')
def edit_expense(expense_id):
    # Current year for footer copyright
    current_year = datetime.datetime.now().year
    
    return render_template('expense_form.html', year=current_year, expense_id=expense_id)