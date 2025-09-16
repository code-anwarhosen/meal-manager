from app.db import DatabaseTable

__USER_SCHEMA = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'name': 'TEXT NOT NULL CHECK(LENGTH(name) < 50)',
    'phone': 'TEXT UNIQUE NOT NULL CHECK(LENGTH(phone) = 11)',
    'password_hash': 'TEXT NOT NULL',
    'is_admin': 'INTEGER DEFAULT 0 CHECK(is_admin IN (0, 1))',
    'joined_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
}

User = DatabaseTable('users', __USER_SCHEMA)
