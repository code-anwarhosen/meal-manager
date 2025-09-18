from typing import Any, Dict, Optional
from app.db.core import DatabaseConnection

class Row:
    """
    Represents a single database row with attribute-style access.
    Provides methods to save and delete the row.
    """
    
    def __init__(self, data: Dict[str, Any], table_name: str, db_connection: DatabaseConnection):
        self._data: dict = data
        self.table_name: str = table_name
        self.db: DatabaseConnection = db_connection
        self._modified: bool = False
    
    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access to row data"""
        if name in self._data:
            return self._data[name]
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Track modifications to row data"""
        
        if name not in ('_data', 'table_name', 'db', '_modified'):
            if name in self._data:
                self._data[name] = value
                self._modified = True
                return
        super().__setattr__(name, value)
    
    def save(self) -> bool:
        """Save changes to the database"""
        
        if not self._modified:
            return True
        
        if 'id' not in self._data:
            return False
        
        # Build SET clause for update
        set_parts = []
        values = []
        
        for col, val in self._data.items():
            if col != 'id':
                set_parts.append(f"{col}=?")
                values.append(val)
        
        values.append(self._data['id'])  # For WHERE clause
        set_clause = ", ".join(set_parts)
        
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE id=?"
        
        success = self.db.execute(sql, tuple(values))
        if success:
            self._modified = False
            
        return success
    
    def delete(self) -> bool:
        """Delete the row from the database"""
        if 'id' not in self._data:
            return False
        
        sql = f"DELETE FROM {self.table_name} WHERE id=?"
        return self.db.execute(sql, (self._data['id'],))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the row to a dictionary"""
        return self._data.copy()
    
    def __repr__(self) -> str:
        return f"<Row {self.table_name}: {self._data}>"
