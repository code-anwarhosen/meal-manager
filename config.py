import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    DEBUG = True

    DATABASE = 'db.sqlite3'
    SECRET_KEY = 'your-secret-key'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB file limit
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
