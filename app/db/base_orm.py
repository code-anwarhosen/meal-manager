import sqlite3, logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union, Tuple


logging.basicConfig(
    level=logging.DEBUG,  # Can be INFO in production
    # format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class AbstractSQLite:
    """
    Abstract base class that defines the required interface
    for any database table representation.
    """
    def __init__(self, db_path: str):
        
        if not db_path or not isinstance(db_path, str):
            raise ValueError('Database Error: db_path can\'t be empty!')
        
        self.__db_path: str = db_path
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        
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
        
        conn = sqlite3.connect(self.__db_path)
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
            
    def _execute(self, sql: str, params: Union[Tuple, None] = None) -> bool:
        """
        Args:
            sql: SQL command to execute
            params: Parameters for the SQL command
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(sql, params or ())
            return True
        
        except sqlite3.Error as e:
            self.logger.error(f"Execute failed: {e} - SQL: {sql}")
            return False
    
    def table_exists(self, table: str) -> bool:
        """
        Check if a table exists in the database.
        """
        sql = "SELECT name FROM sqlite_master WHERE type=? AND name=?"
        
        with self._get_cursor() as cursor:
            cursor.execute(sql, ('table', table))
            result = cursor.fetchone()
            return True if result else False
        
    def get_table_columns(self, table: str) -> List[str]:
        """
        Get column names for a table.
        """
        sql = f"PRAGMA table_info({table})"
        
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [row['name'] for row in rows] if rows else []
    
    def _drop_table(self, table: str) -> bool:
        """
        Drop a table if it exists.
        """
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")
            
        sql = f"DROP TABLE IF EXISTS {table}"
        return self._execute(sql)
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Tuple[str, tuple]:
        """
        Build WHERE clause from dict 'filters' for filtering
        
        Args example
          filters{
              'username': 'john_doe'
          }
        """
        if not filters:
            return "", ()
        
        clause = " AND ".join([f"{col}=?" for col in filters.keys()])
        
        return f"WHERE {clause}", tuple(filters.values())
    
    def _get_dict(self, row: sqlite3.Row) -> Union[Dict, None]:
        """
        Return dict from sqlite3.Row object
        """
        if not row:
            return None
        
        return dict(row)
    
    def _get_list_of_dict(self, rows: List[sqlite3.Row]) -> List[Dict]:
        """
        Return list of dict from list of sqlite3.Row object
        """
        if not rows:
            return []
        
        return [dict(row) for row in rows]


class DatabaseTable(AbstractSQLite):
    """
    A versatile SQLite database wrapper that provides core CRUD operations
    
    Args:
        table: table name represent a table in the database e.g: users
        schema: sql schema for the table in dict form 
          e.g:
          {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'username': 'TEXT NOT NULL'
          }
        db_path: sqlite db name or path e.g: db.sqlite3
    """
    def __init__(self, table: str, schema: Dict[str, str], db_path: str = 'db.sqlite3'):
        
        if not table or not isinstance(table, str) or not table.isidentifier():
            raise ValueError('Database Error: Invalid table name!')
        
        if not schema or not isinstance(schema, dict):
            raise ValueError('Database Error: Invalid schema!')
        
        self.__db_path = db_path # db.sqlite3
        self.__table = table     # users
        self.__schema = schema   # dict: {col_name: col_definition}
        
        super().__init__(self.__db_path)
        self._init_table()
        
    @property
    def table(self):
        return self.__table
    
    @property
    def schema(self):
        return self.__schema
        
    def _init_table(self):
        """Create database table with the given table name and schema"""
        
        columns = ", ".join([f"{col} {definition}" for col, definition in self.schema.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {self.table} ({columns});"
        
        # self.logger.info(f"Creating table: '{self.table}' (if not exists)!")
        self._execute(sql=sql)
        
    
    def create(self, **kwargs) -> Union[int, None]:
        """
        Insert into database table
        
        kwargs:
            column=value keyword arguments
            e.g: for table users
                username='john_doe', name='John Doe'
        Return:
            return the last row id if success
            return None if gets somethig wrong
        """
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = tuple(kwargs.values())

        sql = f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})"
        
        with self._get_cursor() as cursor:
            cursor.execute(sql, values)
            
            return cursor.lastrowid
        
    def get(self, **filters) -> Union[Dict[str, Any], None]:
        """
        Return one row from the database if match filters else return None
        
        Args example:
            {
                username='john_doe'
            }
        """
        where, values = self._build_where_clause(filters)
        
        sql = f"SELECT * FROM {self.table} {where} LIMIT 1"
        
        with self._get_cursor() as cursor:
            cursor.execute(sql, values)
            row = cursor.fetchone()
            
            return self._get_dict(row)
    
    def exists(self, **filters) -> bool:
        """
        Return True if a row exists with the given filters else return False
        Args example:
            {
                username='john_doe'
            }
        """
        return True if self.get(**filters) else False
    
    def all(self) -> List[Dict[str, Any]]:
        """Return all row from the database"""
        sql = f"SELECT * FROM {self.table}"
    
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            
            rows = cursor.fetchall()
            return self._get_list_of_dict(rows)
    
    def update(self, filters: Dict[str, Any], values: Dict[str, Any]) -> int:
        """
        Update database rows with given values if filters matched
        
        Args example:
          filters{
              'username': 'john_doe'
          }
          values{
              'email': 'new_email@example.com'
          }
        """
        where_clause, where_values = self._build_where_clause(filters)
        
        set_clause = ", ".join([f"{col}=?" for col in values.keys()])
        set_values = tuple(values.values())

        sql = f"UPDATE {self.table} SET {set_clause} {where_clause}"
        
        with self._get_cursor() as cursor:
            
            cursor.execute(sql, set_values + where_values)
            return cursor.rowcount
    
    def delete(self, **filters) -> int:
        """
        Delete database rows from the table if filters matched
        """
        where, values = self._build_where_clause(filters)
        
        sql = f"DELETE FROM {self.table} {where}"
        
        with self._get_cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.rowcount
        
    def count(self, **filters) -> int:
        """
        Count records in a table with optional conditions.
        """
        
        where, values = self._build_where_clause(filters)
        
        sql = f"SELECT COUNT(*) as count FROM {self.table} {where}"
        
        with self._get_cursor() as cursor:
            cursor.execute(sql, values)

            result = cursor.fetchone()
            return result['count'] if result else 0
    

# test_schema = {'id': 'INTEGER PRIMARY KEY AUTOINCREMENT','name': 'TEXT NOT NULL'}
# Table = DatabaseTable('table_name', test_schema)

# Table.create(name='John Doe')

# Table.update({'id': 1}, {'name': 'Mr. John Doe'})

# Table.delete(id=2)

# print(Table.all())
# print(Table.count())
