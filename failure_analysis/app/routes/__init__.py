from flask import Blueprint 

from .instructions import bp as instructions_bp

# Aggregate the blueprints for easy imports
def register_blueprints(app):
    app.register_blueprint(instructions_bp)