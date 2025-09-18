from app import create_app

app = create_app()

from app.db import BaseModel
with app.app_context():
    from config import Config
    BaseModel.init_db(db_path=Config.DATABASE)
        
@app.context_processor
def utility_for_templates():
    """All functions here are callable in templates"""
    
    from app.utils import Auth
    return dict(
        is_authenticated=Auth.is_authenticated
    )

if __name__ == '__main__':
    app.run()
