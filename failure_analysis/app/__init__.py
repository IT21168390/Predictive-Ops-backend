from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")

    app.config.from_object('app.config.DevelopmentConfig')

    return app
