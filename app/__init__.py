from flask import Flask
from app.database import dbConnector
from app.config import SERVER_NAME, DB_NAME

def create_app():
    app = Flask(__name__)
    app.db_connector = dbConnector(SERVER_NAME, DB_NAME)
    return app