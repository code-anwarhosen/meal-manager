from typing import List, Optional, Tuple
from app.db.core import DatabaseConnection, LookupTypes
from app.db.row import Row

class QuerySet:
    """
    Chainable query builder for database operations.
    Supports filtering, ordering, and limiting.
    """
    def __init__(self, model_class, db_connection: DatabaseConnection):
        self.model_class = model_class
        self.db = db_connection
        self._filters = {}
        self._order_by = None
        self._limit = None
        self._descending = False
    
    def filter(self, **filters) -> 'QuerySet':
        """Add filters to the query with Django-style lookups"""
        self._filters.update(filters)
        return self
    
    def exclude(self, **filters) -> 'QuerySet':
        """Exclude records matching the filters"""
        
        for field, value in filters.items():
            field, lookup_type = self.db._parse_field_lookup(field)
            
            # Convert exclude to negative filters
            if lookup_type == LookupTypes.EXACT:
                self._filters[f"{field}__ne"] = value
                
            elif lookup_type == LookupTypes.IN:
                self._filters[f"{field}__nin"] = value
                
            else:
                # For other lookups, we'll need to handle them differently
                self._filters[f"NOT_{field}__{lookup_type}"] = value
        
        return self
    
    def order_by(self, field: str, descending: bool = False) -> 'QuerySet':
        """Set ordering for the query"""
        
        self._order_by = field
        self._descending = descending
        return self
    
    def limit(self, count: int) -> 'QuerySet':
        """Set limit for the query"""
        
        self._limit = count
        return self
    
    def _build_query(self) -> Tuple[str, tuple]:
        """Build the SQL query based on current state"""
        
        # Base SELECT
        sql = f"SELECT * FROM {self.model_class.table_name}"
        
        # WHERE clause
        where_clause, values = self.db._build_where_clause(self._filters)
        sql += f" {where_clause}"
        
        # ORDER BY clause
        if self._order_by:
            direction = "DESC" if self._descending else "ASC"
            sql += f" ORDER BY {self._order_by} {direction}"
        
        # LIMIT clause
        if self._limit:
            sql += f" LIMIT {self._limit}"
        
        return sql, values
    
    def all(self) -> List[Row]:
        """Execute the query and return all results as Row objects"""
        
        sql, values = self._build_query()
        rows = self.db.fetch_all(sql, values)
        
        return [Row(dict(row), self.model_class.table_name, self.db) for row in rows]
    
    def first(self) -> Optional[Row]:
        """Execute the query and return the first result as a Row object"""
        sql, values = self._build_query()
        # Add LIMIT 1 to ensure we only get one row
        if "LIMIT" not in sql:
            sql += " LIMIT 1"
        
        row = self.db.fetch_one(sql, values)
        return Row(dict(row), self.model_class.table_name, self.db) if row else None
    
    def count(self) -> int:
        """Return the count of rows matching the current filters"""
        
        # Build count query
        sql = f"SELECT COUNT(*) as count FROM {self.model_class.table_name}"
        where_clause, values = self.db._build_where_clause(self._filters)
        sql += f" {where_clause}"
        
        result = self.db.fetch_one(sql, values)
        return result['count'] if result else 0
    
    def exists(self) -> bool:
        """Check if any rows match the current filters"""
        return self.count() > 0
    
    def delete(self) -> int:
        """Delete all rows matching the current filters"""
        where_clause, values = self.db._build_where_clause(self._filters)
        sql = f"DELETE FROM {self.model_class.table_name} {where_clause}"
        
        with self.db._get_cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.rowcount
