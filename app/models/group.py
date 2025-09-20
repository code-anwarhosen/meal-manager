from app.db import BaseModel
from app.models import User


class Group(BaseModel):
    table_name = 'groups'
    schema = {
        'columns': {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'title': 'TEXT NOT NULL CHECK(LENGTH(title) > 1 AND LENGTH(title) < 25)',
            'description': 'TEXT',
            'member_count':  'INTEGER DEFAULT 1',
            'admin_user_id': 'INTEGER',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        },
        'constraints': [
            f'FOREIGN KEY (admin_user_id) REFERENCES {User.table_name}(id) ON DELETE SET NULL'
        ]
    }
