import os, sys
from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
    
    # MongoDB URI
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ExpenseAppDB')
    
    # Make sure the database name is specified in the URI
    if 'mongodb+srv://' in MONGO_URI and MONGO_URI.endswith('/'):
        MONGO_URI += 'ExpenseAppDB'
    elif 'mongodb+srv://' in MONGO_URI and '/' not in MONGO_URI.split('@')[1]:
        MONGO_URI += '/ExpenseAppDB'
    
    # MongoDB connection settings
    MONGO_CONNECT = True
    MONGO_MAXPOOLSIZE = 50
    MONGO_MINPOOLSIZE = 10
    MONGO_MAX_IDLE_TIME_MS = 10000
    MONGO_RETRYREADS = True
    MONGO_RETRYWRITES = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv('TEST_MONGO_URI', 'mongodb://localhost:27017/ExpenseAppDB_test')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}