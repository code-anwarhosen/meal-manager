from flask import session
from app.models import User


# ---------- Auth: Session ----------
USER_SESSION_KEY = 'user__name'

def login_user(username, remember=False):
    """Logs in the user by saving their username in the session."""
    session[SESSION_USER_KEY] = username
    if remember:
        session.permanent = True
    else:
        session.permanent = False

def logout_user():
    """Logs out the user by removing them from the session."""
    session.pop(USER_SESSION_KEY, None)

def user_logged_in() -> bool:
    """Checks if a user is currently logged in."""
    return USER_SESSION_KEY in session

def current_user() -> 'User':
    """Returns the currently logged-in user, or None."""
    username = session.get(USER_SESSION_KEY)
    if not username:
        return None

    return User.get(username=username)
