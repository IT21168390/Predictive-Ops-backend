from .instructions import bp as instructions_bp
from .diagnostics import bp as diagnostics_bp
from .analytics import bp as analytics_bp

# Aggregate the blueprints for easy imports
def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(instructions_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(analytics_bp)