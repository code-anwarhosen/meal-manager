from app.db import BaseModel

class User(BaseModel):
    table_name = 'users'
    schema = {
        'columns': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'username': 'TEXT UNIQUE NOT NULL CHECK(LENGTH(username) = 11)',
            'name': 'TEXT NOT NULL CHECK(LENGTH(name) < 50)',
            'password_hash': 'TEXT NOT NULL',
            'is_admin': 'INTEGER DEFAULT 0 CHECK(is_admin IN (0, 1))',
            'joined_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        },
        'constraints': [
            f'CREATE INDEX IF NOT EXISTS idx_username ON {table_name}(username);'
        ]
    }
User.init_db()
