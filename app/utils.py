from flask import session
from app.models import User


# ---------- Auth: Session ----------
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
    def is_authenticated(cls) -> bool:
        """Checks if a user is currently logged in."""
        return cls.USER_SESSION_KEY in session

