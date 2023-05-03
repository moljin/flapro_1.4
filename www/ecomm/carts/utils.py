import uuid

from flask import session
from flask_login import current_user

from configs import db
from www.commons.required import login_required
from www.commons.utils import elapsed_day
from www.ecomm.carts.models import Cart
from www.ecomm.promotions.models import Coupon


def _cart_id():
    """session 에 cart_id를 담아두는 방법이다.
    브라우저를 닫으면 session 에 저장된 cart_id가 삭제된다.
    카트에 상품을 담은 후라면, 브라우저를 닫더라도... 카트에 담겼던 상품을 삭제하지 않으면,
    카트와 그에 저장된 상품들은 db 에 보관되어 있는 상태이다."""
    if 'cart_id' in session:
        session['cart_id'] = session.get('cart_id')
    else:
        session['cart_id'] = str(uuid.uuid4())
    return session['cart_id']


def new_cartproduct_create(new_cartproduct, product_obj, pd_single_applied_price, pd_count, pd_total_price):
    new_cartproduct.shop_id = product_obj.shop_id
    new_cartproduct.title = product_obj.title
    new_cartproduct.price = product_obj.price
    new_cartproduct.applied_price = pd_single_applied_price
    new_cartproduct.base_dc_amount = product_obj.base_dc_amount
    new_cartproduct.product_subtotal_quantity = int(pd_count)
    new_cartproduct.product_subtotal_price = int(pd_total_price)


def new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price):
    new_cartproductoption.option_id = op_id[idx]
    new_cartproductoption.title = option_obj.title
    new_cartproductoption.price = option_obj.price
    new_cartproductoption.op_quantity = int(op_count[idx])
    new_cartproductoption.op_line_price = int(op_total_price[idx])
    db.session.bulk_save_objects([new_cartproductoption])


def cartproduct_update(old_cartproduct, pd_count, pd_total_price):
    old_cartproduct.product_subtotal_quantity += int(pd_count)
    old_cartproduct.product_subtotal_price += int(pd_total_price)


def cartproduct_update_remnant(cartproduct, idx, op_total_price):
    cartproduct.op_subtotal_price += int(op_total_price[idx])
    cartproduct.line_price = cartproduct.product_subtotal_price + cartproduct.op_subtotal_price
    db.session.add(cartproduct)


def cartproductoption_update(cartproductoption, idx, op_count, op_total_price):
    cartproductoption.op_quantity += int(op_count[idx])
    cartproductoption.op_line_price += int(op_total_price[idx])
    db.session.bulk_save_objects([cartproductoption])


@login_required
def cart_total_price(cart, cart_products):
    exist_total_price = 0
    for cart_product in cart_products:
        exist_total_price += cart_product.line_price
    cart.cart_total_price = exist_total_price
    current_db_sessions = db.session.object_session(cart)
    current_db_sessions.add(cart)
    db.session.commit()


def cart_active_check(cart):
    beyond_days = elapsed_day(cart.updated_at)
    if beyond_days >= 31:
        cart.is_active = False
        cart.cart_id = "비구매 1개월 초과 카트"
        cart = Cart(user_id=current_user.id, cart_id=_cart_id())
        db.session.add(cart)
        db.session.commit()


def temp_op_list_for_cart_update(op_id, op_count, op_title, op_price, idx, option_id, option_count, cartproductoption):
    op_id.append(option_id[idx])
    op_count.append(option_count[idx])
    op_title.append(cartproductoption.title)
    op_price.append(cartproductoption.price)


def over_discount_cart_apply(used_coupons, used_point, used_coupons_amount, cart, base_pay_amount, point_log):
    if used_coupons:
        print("over_discount_cart_apply")
        if used_point:
            if (used_coupons_amount + used_point) > (cart.cart_total_price - base_pay_amount):
                print("used_coupon and used_point :: 할인금액 초과")
                for used_coupon in used_coupons:
                    coupon_id = used_coupon.coupon_id

                    current_db_sessions = db.session.object_session(used_coupon)
                    current_db_sessions.delete(used_coupon)
                    db.session.commit()

                    coupon_obj = Coupon.query.filter_by(id=coupon_id).first()
                    coupon_obj.available_count += 1
                    coupon_obj.used_count -= 1
                    current_db_sessions = db.session.object_session(coupon_obj)
                    current_db_sessions.add(coupon_obj)
                    db.session.commit()

                point_log.used_point = 0
                point_log.new_remained_point += int(used_point)
                db.session.add(point_log)
                db.session.commit()
        else:
            if used_coupons_amount > (cart.cart_total_price - base_pay_amount):
                print("only used_coupon :: 할인금액 초과")
                for used_coupon in used_coupons:
                    coupon_id = used_coupon.coupon_id

                    current_db_sessions = db.session.object_session(used_coupon)
                    current_db_sessions.delete(used_coupon)
                    db.session.commit()

                    coupon_obj = Coupon.query.filter_by(id=coupon_id).first()
                    coupon_obj.available_count += 1
                    coupon_obj.used_count -= 1
                    current_db_sessions = db.session.object_session(coupon_obj)
                    current_db_sessions.add(coupon_obj)
                    db.session.commit()
    else:
        if used_point:
            if used_point > (cart.cart_total_price - base_pay_amount):  # 할인포인트가 (주문가격-최소결제금액) 초과
                print("only used_point :: 할인금액 초과")
                point_log.used_point = 0
                point_log.new_remained_point += int(used_point)
                db.session.add(point_log)
                db.session.commit()

