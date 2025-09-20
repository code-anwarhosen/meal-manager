from flask import session, redirect, url_for, flash
from functools import wraps
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
    def get_username(cls):
        """return username from session"""
        return session.get(cls.USER_SESSION_KEY, None)

    @classmethod
    def is_authenticated(cls) -> bool:
        """Checks if a user is currently logged in."""
        return cls.USER_SESSION_KEY in session


def login_required(func):

    @wraps(func)  # This preserves the function's metadata
    def wrapper(*args, **kwargs):
        if Auth.is_authenticated():
            return func(*args, **kwargs)

        else:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))

    return wrapper


def current_user():
    username = Auth.get_username()

    return User.get(username=username)



