from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import mongo

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize MongoDB
    mongo.init_app(app)

    # Import and register blueprints from both backends
    from .routes.analytics import analytics_bp
    from .routes.diagnostics import diagnostics_bp
    from .routes.correlations import correlations_bp
    from .routes.feature_importance import feature_importance_bp
    from .routes.model_matrix import model_matrix_bp
    from .routes.failure_analysis import failure_analysis_bp
    from .routes.preprocessor import preprocessor_bp
    from .routes.instructions import bp as instructions_bp

    # Register blueprints
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(diagnostics_bp, url_prefix='/diagnostics')
    app.register_blueprint(correlations_bp, url_prefix='/correlations')
    app.register_blueprint(feature_importance_bp, url_prefix='/feature-importance')
    app.register_blueprint(model_matrix_bp)
    app.register_blueprint(failure_analysis_bp, url_prefix='/failure_analysis')
    app.register_blueprint(preprocessor_bp, url_prefix='/preprocessor')
    app.register_blueprint(instructions_bp)

    return app