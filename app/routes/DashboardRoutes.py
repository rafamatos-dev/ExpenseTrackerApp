# routes/DashboardRoutes.py
from flask import Blueprint, render_template
import datetime

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

def init_dashboard_routes(app):
    """Initialize dashboard routes with application context"""
    # Register the blueprint with the app
    app.register_blueprint(dashboard_bp)

# Dashboard home route
@dashboard_bp.route('/dashboard')
def dashboard():
    # Current year for footer copyright
    current_year = datetime.datetime.now().year
    
    return render_template('dashboard.html', year=current_year)