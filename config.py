import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/myFlaskApp')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv('TEST_MONGO_URI', 'mongodb://localhost:27017/testFlaskApp')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}