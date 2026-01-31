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

    from routes.auth import auth_bp
    from routes.sponsors import sponsors_bp
    from routes.events import events_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(sponsors_bp, url_prefix="/api/sponsors")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
