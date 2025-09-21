from app.db import BaseModel
import os, base64, hashlib


class PasswordManager:
    iterations: int = 1_00_000

    @classmethod
    def make_password(cls, password: str) -> str:
        """Hash a password with PBKDF2-HMAC (SHA256) and a random salt."""
        
        salt = os.urandom(16)  # 128-bit salt
        pwd = password.encode("utf-8")
        
        dk = hashlib.pbkdf2_hmac("sha256", pwd, salt, cls.iterations)
        
        # Store as base64: iterations$salt$hash
        return f"{cls.iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"

    @classmethod
    def check_password(cls, password: str, stored_hash: str) -> bool:
        """Verify a password against the stored hash string."""
        
        iterations_str, salt_b64, hash_b64 = stored_hash.split("$")
        iterations = int(iterations_str)
        
        salt = base64.b64decode(salt_b64)
        old_hash = base64.b64decode(hash_b64)

        pwd = password.encode("utf-8")
        new_hash = hashlib.pbkdf2_hmac("sha256", pwd, salt, iterations)

        return new_hash == old_hash
    

class User(BaseModel, PasswordManager):
    table_name = 'users'
    schema = {
        'columns': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'username': 'TEXT UNIQUE NOT NULL CHECK(LENGTH(username) = 11)',
            'name': 'TEXT NOT NULL CHECK(LENGTH(name) < 50)',
            'password_hash': 'TEXT NOT NULL',
            'is_admin': 'INTEGER DEFAULT 0 CHECK(is_admin IN (0, 1))',
            'joined_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
    }
