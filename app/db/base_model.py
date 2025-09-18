from typing import Any, Dict, List, Optional
from app.db.core import DatabaseConnection
from app.db.queryset import QuerySet
from app.db.row import Row

def check(db):
    if not db:
        raise ValueError("Database not initialized. Call .set_database() first.")
    
class QuerySetDescriptor:
    """Descriptor that returns a QuerySet instance."""
    
    def __get__(self, instance, owner) -> QuerySet:
        return QuerySet(owner, owner._db)


class BaseModel:
    """
    Abstract base class for ORM models.
    Provides class-based table definitions and ORM operations.
    """
    # These should be defined in subclasses
    table_name: str = None # type: ignore
    schema = {
        "columns": {},
        "constraints": []
    }
    
    # Class-level database connection
    _db: DatabaseConnection = None # type: ignore
    
    _table_initialized = False
    
    objects = QuerySetDescriptor()
    
    @classmethod
    def init_db(cls, db_path: str = 'db.sqlite3'):
        """Set the database connection for all models"""
        cls._db = DatabaseConnection(db_path)
        cls.init_table()
        
    @classmethod
    def init_table(cls):
        """Create the table and apply constraints if they don't exist"""
        cls._table_initialized = cls._db.table_exists(cls.table_name)
        
        if cls._table_initialized:
            return
        
        # Create table
        columns = ", ".join([f"{col} {definition}" for col, definition in cls.schema["columns"].items()])
        sql = f"CREATE TABLE {cls.table_name} ({columns})"
        cls._db.execute(sql)
        
        # Apply constraints
        for constraint in cls.schema.get("constraints", []):
            cls._db.execute(constraint)
    
    @classmethod
    def create(cls, **kwargs) -> Optional[int]:
        """Create a new record and return its ID"""
        
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = tuple(kwargs.values())
        
        sql = f"INSERT INTO {cls.table_name} ({cols}) VALUES ({placeholders})"
        
        with cls._db._get_cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.lastrowid
    
    @classmethod
    def get(cls, **filters) -> Optional[Row]:
        """Get a single record matching the filters"""
        
        where, values = cls._db._build_where_clause(filters)
        sql = f"SELECT * FROM {cls.table_name} {where} LIMIT 1"
        
        row = cls._db.fetch_one(sql, values)
        return Row(dict(row), cls.table_name, cls._db) if row else None
    
    @classmethod
    def exists(cls, **filters) -> bool:
        """Check if a record exists matching the filters"""
        
        return cls.get(**filters) is not None
    
    @classmethod
    def all(cls) -> List[Row]:
        """Get all records from the table"""
        
        sql = f"SELECT * FROM {cls.table_name}"
        rows = cls._db.fetch_all(sql)
        return [Row(dict(row), cls.table_name, cls._db) for row in rows]
    
    @classmethod
    def update(cls, filters: Dict[str, Any], values: Dict[str, Any]) -> int:
        """Update records matching the filters with the given values"""
        
        where_clause, where_values = cls._db._build_where_clause(filters)
        set_clause = ", ".join([f"{col}=?" for col in values.keys()])
        set_values = tuple(values.values())
        
        sql = f"UPDATE {cls.table_name} SET {set_clause} {where_clause}"
        
        with cls._db._get_cursor() as cursor:
            cursor.execute(sql, set_values + where_values)
            return cursor.rowcount
    
    @classmethod
    def delete(cls, **filters) -> int:
        """Delete records matching the filters"""
        
        where, values = cls._db._build_where_clause(filters)
        sql = f"DELETE FROM {cls.table_name} {where}"
        
        with cls._db._get_cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.rowcount
    
    @classmethod
    def count(cls, **filters) -> int:
        """Count records matching the filters"""
        
        where, values = cls._db._build_where_clause(filters)
        sql = f"SELECT COUNT(*) as count FROM {cls.table_name} {where}"
        
        result = cls._db.fetch_one(sql, values)
        return result['count'] if result else 0
    
    # @classmethod
    # def objects(cls) -> QuerySet:
    #     """Return a QuerySet for chainable queries"""
        
    #     return QuerySet(cls, cls._db)
