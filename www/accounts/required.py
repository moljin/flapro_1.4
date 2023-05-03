from functools import wraps

from flask import redirect, url_for, abort, session

from www.accounts.models import User, Profile
from www.commons.required import created_obj_ownership


def account_ownership_required(function):
    @wraps(function)
    def decorator_function(_id, *args, **kwargs):
        user = User.query.get_or_404(_id)
        created_obj_ownership(user.id)
        return function(_id, *args, **kwargs)
    return decorator_function


def profile_ownership_required(function):
    @wraps(function)
    def decorator_function(_id, *args, **kwargs):
        profile = Profile.query.get_or_404(_id)
        created_obj_ownership(profile.user_id)
        return function(_id, *args, **kwargs)
    return decorator_function

