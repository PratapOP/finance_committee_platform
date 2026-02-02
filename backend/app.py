from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    # Initialize models with db and login_manager instances
    from models import init_models
    init_models(db, login_manager)

    from routes.auth import auth_bp
    from routes.sponsors import sponsors_bp
    from routes.events import events_bp
    from routes.sponsorships import sponsorships_bp
    from routes.analytics import analytics_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(sponsors_bp, url_prefix="/api/sponsors")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(sponsorships_bp, url_prefix="/api/sponsorships")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
