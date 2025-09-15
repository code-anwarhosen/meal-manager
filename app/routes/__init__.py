from .main_routes import bp as main_bp
from .user_routes import bp as user_bp

from flask import Flask

def register_blueprints(app: Flask):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
