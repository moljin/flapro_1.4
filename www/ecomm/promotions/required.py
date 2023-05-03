from functools import wraps

from www.commons.required import created_obj_ownership
from www.ecomm.promotions.models import Coupon


def coupon_ownership_required(function):
    @wraps(function)
    def decorated_function(_id, *args, **kwargs):
        coupon = Coupon.query.get_or_404(_id)
        created_obj_ownership(coupon.user_id)
        return function(_id, *args, **kwargs)
    return decorated_function
