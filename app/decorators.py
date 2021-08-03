from functools import wraps
from flask_login import current_user
from flask import abort,flash,redirect,url_for
from .utils import redirect_back

def admin_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.is_anonymous or not current_user.is_admin:
            abort(403)
        return func(*args,**kwargs)
    return wrapper


def check_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            flash('You Are Already Logged in','danger')
            return redirect_back()
        return func(*args, **kwargs)

    return wrapper
