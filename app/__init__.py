from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from config import Config
    app.config.from_object(Config)
    
    from app.routes import register_blueprints
    register_blueprints(app)
    
    return app
