from pathlib import Path
from decouple import config

# ------- Helpers for class: Config ---------
BASE_DIR = Path(__file__).resolve().parent.parent

# Database for development
DEV_SQLITE_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Database for production
PROD_MYSQL_DB = {
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
class Config:
    # Constants
    DEV = 'development'
    PROD = 'production'
    
    # ENV: production or development
    ENV = config('ENV', default=DEV)

    # Get the database based on ENV
    @classmethod
    def get_database(cls):
        if config('WHICH_DB', default='mysql') == 'mysql':
            return PROD_MYSQL_DB
        return DEV_SQLITE_DB
