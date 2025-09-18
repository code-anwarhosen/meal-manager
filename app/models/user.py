import bcrypt
from app.db import BaseModel


class Password:
    @staticmethod
    def make_password(password: str) -> str:
        # Convert to bytes
        bytes = password.encode('utf-8')

        # Generate salt and hash
        salt = bcrypt.gensalt()

        hash_bytes = bcrypt.hashpw(bytes, salt)
        return hash_bytes.decode('utf-8')

    @staticmethod
    def check_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

class User(BaseModel, Password):
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
