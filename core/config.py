from pathlib import Path
from decouple import config, Csv

# ------- Helpers for class: Config ---------
BASE_DIR = Path(__file__).resolve().parent.parent

# Database for development
SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Database for production
MYSQL_DB = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default=None),
        'USER': config('DB_USER', default=None),
        'PASSWORD': config('DB_PASSWORD', default=None),
        'HOST': config('DB_HOST', default=None),
        'PORT': config('DB_PORT', default=None),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# ------ Main Config --------
# Constants
class Const:
    Dev = 'development'
    Prod = 'production'
    
    Sqlite = 'sqlite'
    MySql = 'mysql'
    
    
class Config:
    SECRET_KEY = config('SECRET_KEY')
    DEBUG = config('DEBUG', default=False, cast=bool)
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
    
    # ENV: production or development
    Env = config('ENV', default=Const.Dev)

    # Get the database based on ENV
    @classmethod
    def get_database(cls):
        if config('WHICH_DB', default=Const.Sqlite) == Const.Sqlite:
            return SQLITE_DB
        return MYSQL_DB
