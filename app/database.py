# app/database.py - Database connection management
from flask_pymongo import PyMongo

# MongoDB instance
mongo = None

def get_db():
    """
    Returns the MongoDB client instance.
    Should be used to access the database from other modules.
    """
    global mongo
    if mongo is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return mongo

def init_db(app):
    """
    Initialize the MongoDB connection with the given Flask app.
    Returns the MongoDB client instance.
    """
    global mongo
    mongo = PyMongo(app)
    return mongo