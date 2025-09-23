from sqlite_orm.fields import (
    CharField, IntegerField, BooleanField,
    DateTimeField, ForeignKey, TextField
)
from sqlite_orm.db import BaseModel
from app.models.utils import PasswordManager


class User(BaseModel, PasswordManager):
    id = IntegerField(primary_key=True)
    username = CharField(max_length=50, unique=True, nullable=False)
    name = CharField(max_length=30, nullable=False)
    password_hash = TextField(nullable=False)
    is_admin = BooleanField(default=False)
    
    joined_at = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(nullable=True)
    
    table_name = 'users'
    
    
    def set_password(self, password: str) -> None:
        """Set password hash for the user"""
        self.password_hash = self.make_password(password)
        self.save()
    
    def check_password(self, password: str) -> bool:
        """Verify user password"""
        return PasswordManager._check_password(password, self.password_hash) # type: ignore


class Group(BaseModel):
    id = IntegerField(primary_key=True)
    title = CharField(max_length=50, nullable=False)
    description = CharField(max_length=256, nullable=True)
    admin_id = ForeignKey(User, nullable=False)
    created_at = DateTimeField(auto_now_add=True)
    
    @property
    def role(self):
        if not isinstance(self.id, int):
            return 'N/A'
        
        ugm = UserGroup.get(group_id=self.id)
        return ugm.role if ugm else 'N/A'
    
    @property
    def member_count(self):
        if not isinstance(self.id, int):
            return 0
        
        ugm = UserGroup.filter(group_id=self.id).all()
        return len(ugm)

class GroupRole:
    MEMBER = 'member'
    ADMIN = 'admin'

class UserGroup(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = ForeignKey(User, nullable=False)
    group_id = ForeignKey(Group, nullable=False)
    role = CharField(max_length=10, default=GroupRole.MEMBER)
    joined_at = DateTimeField(auto_now_add=True)

