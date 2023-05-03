from functools import wraps

from flask import session, redirect, url_for, abort

from www.accounts.models import User, Profile
from www.commons.required import created_obj_ownership
from www.ecomm.products.models import Shop, Product


def vendor_required(function):
    @wraps(function)
    def decorator_function(*args, **kwargs):
        try:
            logged_user_username = session['username']
            user_obj = User.query.filter_by(username=logged_user_username).first()
            profile_obj = Profile.query.filter_by(user_id=user_obj.id).first()
            # 프로필이 있지만 판매사업자가 아니면 vendor not 으로 보낸다.
            if profile_obj.level != '판매사업자':
                return redirect(url_for('accounts.vendor_not'))
            return function(*args, **kwargs)
        except Exception as e:
            print("vendor_required Error", e)
            # 로그인되어있지만 프로필 없거나, 로그인되지 않은 경우 401 로 보낸다.
            abort(401)
    return decorator_function


def shop_ownership_required(function):
    @wraps(function)
    def decorated_function(_id, *args, **kwargs):
        shop = Shop.query.get_or_404(_id)
        created_obj_ownership(shop.user_id)
        return function(_id, *args, **kwargs)
    return decorated_function


def product_ownership_required(function):
    @wraps(function)
    def decorated_function(_id, *args, **kwargs):
        product = Product.query.get_or_404(_id)
        created_obj_ownership(product.user_id)
        return function(_id, *args, **kwargs)
    return decorated_function




