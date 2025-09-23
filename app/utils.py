from flask import session, redirect, url_for, flash
from functools import wraps
from app.models import User
from typing import Union
import base64


# ---------- Auth: Session ----------
def current_user():
    username = Auth.get_username()

    return User.get(username=username)


class Auth:
    USER_SESSION_KEY = 'user__name'

    @classmethod
    def login_user(cls, username, remember=False):
        """Logs in the user by saving their username in the session."""
        session[cls.USER_SESSION_KEY] = username

        if remember:
            session.permanent = True

        else:
            session.permanent = False

    @classmethod
    def logout_user(cls):
        """Logs out the user by removing them from the session."""

        # session.pop(cls.USER_SESSION_KEY, None)
        session.clear()

    @classmethod
    def get_username(cls) -> str:
        """return username from session"""
        return session.get(cls.USER_SESSION_KEY, None)

    @classmethod
    def is_authenticated(cls) -> bool:
        """Checks if a user is currently logged in."""
        user = current_user()
        if not user:
            return False
        
        session_username = cls.get_username()
        
        if session_username and user.username == session_username:
            return True
        
        return False


def login_required(func):

    @wraps(func)  # This preserves the function's metadata
    def wrapper(*args, **kwargs):
        if Auth.is_authenticated():
            return func(*args, **kwargs)

        else:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))

    return wrapper


class Encoding:
    @classmethod
    def get_base64_id(cls, id: Union[int, str]) -> str:
        id_bytes = str(id).encode()
        
        base64_id = base64.urlsafe_b64encode(id_bytes)
        return base64_id.decode()

    @classmethod
    def get_orginal_id(cls, base64_id: str) -> Union[str, int]:
        base64_bytes = str(base64_id).encode()
        
        orginal_id = base64.urlsafe_b64decode(base64_bytes).decode()
        
        if orginal_id.isnumeric():
            return int(orginal_id)
        
        return orginal_id
