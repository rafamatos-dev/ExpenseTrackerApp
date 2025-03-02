from flask import Flask
from dotenv import load_dotenv
from app.routes.routes import register_routes
from app.routes.UserRoutes import init_user_routes
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
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=app.config['DEBUG'])