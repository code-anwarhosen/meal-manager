import sqlite3, logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Union, Tuple

# from .utils import Password

class SQLite:
    def __init__(self, db_path: str):
        if not db_path or not isinstance(db_path, str):
            raise ValueError('Database Error: db_path can\'t be empty!')
        
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and set pragmas"""
        try:
            with self._get_connection() as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with automatic cleanup"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        try:
            yield conn
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        
        finally:
            conn.close()

    @contextmanager
    def _get_cursor(self):
        """Context manager for database cursor operations"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            yield cursor

    def execute(self, sql: str, params: Union[Tuple, List, None] = None) -> bool:
        """
        Execute a SQL command without returning results.
        
        Args:
            sql: SQL command to execute
            params: Parameters for the SQL command
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params or ())
            return True
        
        except sqlite3.Error as e:
            self.logger.error(f"Execute failed: {e} - SQL: {sql}")
            return False

    def fetch_all(self, sql: str, params: Union[Tuple, List, None] = None) -> List[Dict]:
        """
        Fetch all rows from a query.
        
        Args:
            sql: SQL query
            params: Parameters for the query
            
        Returns:
            List of dictionaries representing rows
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params or ())
                rows = cursor.fetchall()
                return [dict(row) for row in rows] if rows else []
            
        except sqlite3.Error as e:
            self.logger.error(f"Fetch all failed: {e} - SQL: {sql}")
            return []

    def fetch_one(self, sql: str, params: Union[Tuple, List, None] = None) -> Optional[Dict]:
        """
        Fetch a single row from a query.
        
        Args:
            sql: SQL query
            params: Parameters for the query
            
        Returns:
            Dictionary representing the row, or None if not found
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params or ())
                row = cursor.fetchone()
                return dict(row) if row else None
            
        except sqlite3.Error as e:
            self.logger.error(f"Fetch one failed: {e} - SQL: {sql}")
            return None

    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a new record into a table.
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs
            
        Returns:
            int: ID of the inserted row, or None if failed
        """
        if not data:
            return None

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, values)
                return cursor.lastrowid
            
        except sqlite3.Error as e:
            self.logger.error(f"Insert failed: {e} - Table: {table}")
            return None

    def update(self, table: str, data: Dict[str, Any], where: str, where_params: Union[Tuple, List] = ()) -> int:
        """
        Update records in a table.
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs to update
            where: WHERE clause (without WHERE keyword) e.g: id=?
            where_params: Parameters for the WHERE clause e.g: (1,)
            
        Returns:
            int: Number of rows affected
        """
        if not data:
            return 0

        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        values = tuple(data.values()) + tuple(where_params)
        
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, values)
                return cursor.rowcount
            
        except sqlite3.Error as e:
            self.logger.error(f"Update failed: {e} - Table: {table}")
            return 0

    def delete(self, table: str, where: str, params: Union[Tuple, List] = ()) -> int:
        """
        Delete records from a table.
        
        Args:
            table: Table name
            where: WHERE clause (without WHERE keyword) e.g: id=?
            params: Parameters for the WHERE clause e.g: (1,)
            
        Returns:
            int: Number of rows deleted
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount
            
        except sqlite3.Error as e:
            self.logger.error(f"Delete failed: {e} - Table: {table}")
            return 0

    def drop_table(self, table: str) -> bool:
        """
        Drop a table if it exists.
        """
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")
            
        sql = f"DROP TABLE IF EXISTS {table}"
        return self.execute(sql)

    def table_exists(self, table: str) -> bool:
        """
        Check if a table exists in the database.
        """
        sql = "SELECT name FROM sqlite_master WHERE type=? AND name=?"
        result = self.fetch_one(sql, ('table', table))
        return result is not None

    def get_table_columns(self, table: str) -> List[str]:
        """
        Get column names for a table.
        
        Args:
            table: Table name
            
        Returns:
            List of column names
        """
        sql = f"PRAGMA table_info({table})"
        rows = self.fetch_all(sql)
        return [row['name'] for row in rows] if rows else []

    def count(self, table: str, where: str = "1=1", params: Union[Tuple, List] = ()) -> int:
        """
        Count records in a table with optional conditions.
        
        Args:
            table: Table name
            where: WHERE clause (without WHERE keyword)
            params: Parameters for the WHERE clause
            
        Returns:
            int: Number of records
        """
        sql = f"SELECT COUNT(*) as count FROM {table} WHERE {where}"
        result = self.fetch_one(sql, params)
        return result['count'] if result else 0


class UserTmp(SQLite):
    def __init__(self, table: str, db_path: str = 'db.sqlite3'):
        super().__init__(db_path)
        
        self.table = table
        
    def create_users_table(self):
        schema = f"""
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL CHECK(LENGTH(username) >= 4),
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL CHECK(LENGTH(phone) = 11),
            is_admin INTEGER DEFAULT 0 CHECK(is_admin IN (0, 1)),
            password_hash TEXT NOT NULL CHECK(LENGTH(password_hash) >= 20),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """
    
    def create_indexes_for_users_table(self):
        # Add index creation for frequently queried columns
        self.execute(f"CREATE INDEX IF NOT EXISTS idx_username ON {self.table}(username)")
        self.execute(f"CREATE INDEX IF NOT EXISTS idx_phone ON {self.table}(phone)")
    
    def add_user(self, username, name, phone, password, is_admin=False):
        
        # pw_hash = Password.make_hash(password)
        
        data = {
            'username': username,
            'name': name,
            'phone': phone,
            'is_admin': is_admin,
            'password_hash': 'pw_hash',
        }
        return self.insert(self.table, data)

    def get_user_by_id(self, id: int):
        
        sql = f"""
            SELECT * 
            FROM {self.table} 
            WHERE id = ?
        """
        return self.fetch_one(sql, (id,))
        
    def get_user_by_username(self, username: str):
        
        sql = f"""
            SELECT * FROM {self.table} 
            WHERE username=?;
        """
        return self.fetch_one(sql, (username,))

    def get_all_users(self):
        sql = f"""
            SELECT * FROM {self.table};
        """
        return self.fetch_all(sql)
    
    def delete_user_by_id(self, id: int):
        return self.delete(table=self.table, where="id=?", params=(id, ))
    
    def delete_user_by_username(self, username: str):
        return self.delete(table=self.table, where="username=?", params=(username, ))
    
    def update_user_by_id(self, id: int, data: dict):
        
        return self.update(
            table=self.table, 
            data=data, 
            where="id=?",
            where_params=(id,)
        )
    
    def is_valid_user(self, username: str, password: str):
        
        user = self.get_user_by_username(username)
        pw_hash = user['password_hash'] if user else None
        
        if not pw_hash:
            return False
        
        #return Password.check(password, pw_hash)


class DatabaseTable(SQLite):
    """
    A versatile SQLite database wrapper that provides core CRUD operations
    
    Args:
        table: table name in the database e.g: users
        schema: sql schema for the table in string form 
          e.g:
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        db_path: sqlite db name or path e.g: db.sqlite3
    """
    
    def __init__(self, table: str, schema: str, db_path: str = 'db.sqlite3'):
        if not table or not isinstance(table, str):
            raise ValueError('Database Error: table name can\'t be empty!')
        
        if not schema or not isinstance(schema, str):
            raise ValueError('Database Error: schema can\'t be empty!')
        
        self.__table = table
        self.__schema = schema
        
        super().__init__(db_path)
        
        self.__init_table()
        
    def __init_table(self):
        with self._get_cursor() as cursor:
            sql = f"CREATE TABLE IF NOT EXISTS {self.table} ({self.schema})"
            cursor.execute(sql)
        
    @property
    def table(self):
        return self.__table
    
    @property
    def schema(self):
        return self.__schema
    

User = DatabaseTable(table='users', schema='')
