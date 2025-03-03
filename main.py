from flask import Flask
from dotenv import load_dotenv
from app.routes.routes import register_routes
from app.routes.UserRoutes import init_user_routes
from app.routes.ExpenseRoutes import init_expense_routes
from app.routes.CategoryRoutes import init_category_routes
from app.routes.DashboardRoutes import init_dashboard_routes
from app.routes.AuthRoutes import init_auth_routes
from app.routes.ExpenseFormRoutes import init_expense_form_routes
from app.database import init_db
from config import config
import os

# Load environment variables
load_dotenv()

def create_app(config_name='default'):
    # Initialize app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    mongo = init_db(app)
    
    # Register all routes
    register_routes(app, mongo)

    # Register user routes
    init_user_routes(app, mongo)
    
    # Register expense routes
    init_expense_routes(app, mongo)
    
    # Register category routes
    init_category_routes(app, mongo)
    
    # Register dashboard routes
    init_dashboard_routes(app)
    
    # Register authentication routes
    init_auth_routes(app)
    
    # Register expense form routes
    init_expense_form_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=app.config['DEBUG'])