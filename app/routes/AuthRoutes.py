# routes/AuthRoutes.py
from flask import Blueprint, render_template
import datetime

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

def init_auth_routes(app):
    """Initialize authentication routes with application context"""
    # Register the blueprint with the app
    app.register_blueprint(auth_bp)

# Login page route
@auth_bp.route('/login')
def login():
    # Current year for footer copyright
    current_year = datetime.datetime.now().year
    
    return render_template('login.html', year=current_year)

# Registration page route
@auth_bp.route('/register')
def register():
    # Current year for footer copyright
    current_year = datetime.datetime.now().year
    
    return render_template('register.html', year=current_year)