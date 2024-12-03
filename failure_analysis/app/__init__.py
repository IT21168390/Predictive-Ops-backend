from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

from app.models import mongo

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")

    app.config.from_object('app.config.DevelopmentConfig')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')

    mongo.init_app(app)

    from app.routes import instructions, diagnostics, analytics, correlations
    app.register_blueprint(instructions.bp)
    app.register_blueprint(diagnostics.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(correlations.bp)

    return app
