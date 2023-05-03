from functools import wraps

from flask import session, request, redirect, url_for, abort
from flask_login import current_user

from www.accounts.models import User


def created_obj_ownership(user_id):
    user = User.query.get_or_404(user_id)
    admin = User.query.filter_by(is_admin=True).first()
    if not current_user.is_authenticated:
        abort(404)
    else:
        if (user != current_user) and (admin != current_user):
            abort(401)


def login_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        if not current_user.is_authenticated:
            try:
                session['previous_url'] = request.path  # request.referrer 을 이용하면 그 전 path 로 보낸다.
            except Exception as e:
                print("login_required(function) Exception::: ", e)
                session['previous_url'] = None
            return redirect(url_for('accounts.login'))
            # return redirect(url_for('accounts.login', next=request.path))  # 작동되게 못하겠다.
        return function(*args, **kwargs)
    return decorator_function


def admin_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        if current_user.is_authenticated:
            if not current_user.is_admin:
                abort(401)
        else:
            abort(401)
        return function(*args, **kwargs)
    return decorator_function


