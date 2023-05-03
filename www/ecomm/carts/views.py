import datetime

from flask import Blueprint, request, make_response, jsonify, redirect, render_template, url_for, abort
from flask_login import current_user

from configs import db
from www.commons.models import BaseAmount
from www.commons.required import login_required
from www.ecomm.carts.models import Cart, CartProduct, CartProductOption
from www.ecomm.carts.utils import _cart_id, cart_active_check, new_cartproduct_create, new_cartproductoption_create, cartproduct_update_remnant, cartproduct_update, cartproductoption_update, \
    cart_total_price, over_discount_cart_apply, temp_op_list_for_cart_update
from www.ecomm.orders.models import CustomerUid
from www.ecomm.orders.utils import customer_uid_set
from www.ecomm.products.models import Product, ProductOption
from www.ecomm.promotions.forms import AddCouponForm
from www.ecomm.promotions.models import Coupon, UsedCoupon, Point, PointLog
from www.ecomm.promotions.utils import cart_point_log_create, cart_point_log_update

NAME = 'carts'
carts = Blueprint(NAME, __name__, url_prefix='/ecomm/carts')


@carts.route('/add/to/cart/<int:_id>', methods=['POST'])
@login_required
def add_to_cart(_id):
    product_obj = Product.query.get_or_404(_id)
    option_objs = ProductOption.query.filter_by(product_id=_id).all()

    pd_count = request.form.get("pd-count")
    pd_single_applied_price = request.form.get("pd-applied-price")
    pd_total_price = request.form.get("pd-total-price")

    op_id = request.form.getlist("op-id")
    op_count = request.form.getlist("op-count")
    op_total_price = request.form.getlist("op-total-price")
    print(op_id)
    print(op_count)
    print(op_total_price)

    total_price = request.form.get("total-price")
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart:
        cart = Cart(user_id=current_user.id, cart_id=_cart_id())
        db.session.add(cart)
        db.session.commit()
    else:  # 여기로 지나갈 수는 없지만...d/t 상품페이지로 진입시 이 과정을 거친다.
        cart_active_check(cart)

    old_cartproduct = CartProduct.query.filter_by(cart_id=cart.id, product_id=_id).first()
    old_cartproductoptions = CartProductOption.query.filter_by(cart_id=cart.id, product_id=_id).all()

    if option_objs and not old_cartproduct and not old_cartproductoptions:
        new_cartproduct = CartProduct(cart_id=cart.id, product_id=_id)
        new_cartproduct_create(new_cartproduct, product_obj, pd_single_applied_price, pd_count, pd_total_price)
        db.session.add(new_cartproduct)

        if op_id:
            for idx in range(len(op_id)):
                option_obj = ProductOption.query.get_or_404(int(op_id[idx]))
                new_cartproductoption = CartProductOption(cart_id=cart.id, product_id=_id)
                new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price)

                if new_cartproduct.op_subtotal_price is None:
                    new_cartproduct.op_subtotal_price = 0
                    """cartproduct가 맨처음 만들어질때는 아직 op_subtotal_price 에 default=0이 적용되있지 않기 때문에 
                        명시적으로 0을 넣어주고 진행한다. 
                        그렇지 않으면 cartproduct.op_subtotal_price 이 None 으로 +=를 적용시키지 못한다."""
                cartproduct_update_remnant(new_cartproduct, idx, op_total_price)
        else:
            new_cartproduct.line_price = new_cartproduct.product_subtotal_price
            db.session.add(new_cartproduct)
        db.session.commit()

    elif option_objs and old_cartproduct and not old_cartproductoptions:
        cartproduct_update(old_cartproduct, pd_count, pd_total_price)
        db.session.add(old_cartproduct)

        for idx in range(len(op_id)):
            option_obj = ProductOption.query.get_or_404(int(op_id[idx]))
            new_cartproductoption = CartProductOption(cart_id=cart.id, product_id=_id)
            new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price)

            cartproduct_update_remnant(old_cartproduct, idx, op_total_price)
        db.session.commit()

    elif option_objs and old_cartproduct and old_cartproductoptions:
        cartproduct_update(old_cartproduct, pd_count, pd_total_price)
        db.session.add(old_cartproduct)
        if op_id:
            for idx in range(len(op_id)):
                old_cartproductoption = CartProductOption.query.filter_by(cart_id=cart.id, product_id=_id, option_id=int(op_id[idx])).first()
                if old_cartproductoption:
                    cartproductoption_update(old_cartproductoption, idx, op_count, op_total_price)
                else:
                    option_obj = ProductOption.query.get_or_404(int(op_id[idx]))
                    new_cartproductoption = CartProductOption(cart_id=cart.id, product_id=_id)
                    new_cartproductoption_create(new_cartproductoption, option_obj, idx, op_id, op_count, op_total_price)

                cartproduct_update_remnant(old_cartproduct, idx, op_total_price)
        else:
            old_cartproduct.line_price = old_cartproduct.product_subtotal_price + old_cartproduct.op_subtotal_price
            db.session.add(old_cartproduct)
        db.session.commit()

    elif not option_objs and not old_cartproduct:
        new_cartproduct = CartProduct(cart_id=cart.id, product_id=_id)
        new_cartproduct_create(new_cartproduct, product_obj, pd_single_applied_price, pd_count, pd_total_price)

        new_cartproduct.line_price = new_cartproduct.product_subtotal_price
        db.session.add(new_cartproduct)
        db.session.commit()

    elif not option_objs and old_cartproduct:
        cartproduct_update(old_cartproduct, pd_count, pd_total_price)

        old_cartproduct.line_price = old_cartproduct.product_subtotal_price
        db.session.add(old_cartproduct)
        db.session.commit()

    return redirect(url_for('carts.cart_view'))


coupons = ""
_used_coupons = ""


@carts.route('/view', methods=['GET'])
@login_required
def cart_view():
    global coupons, _used_coupons
    now = datetime.datetime.now()
    try:
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        if cart:
            cart_active_check(cart)
            coupons = Coupon.query.filter_by(is_active=True).filter(Coupon.use_from <= now, Coupon.use_to >= now).all()
            _used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()

    except Exception as e:
        print(e, 'cart_view Exception: 카트가 없고, 사용가능한 쿠폰, 사용한 쿠폰도 없다.')
        cart = None
        coupons = None
        _used_coupons = None
    if current_user.is_authenticated:
        if cart and cart.is_active is True:
            add_coupon_form = AddCouponForm()
            cart_products = CartProduct.query.filter_by(cart_id=cart.id).all()
            cart_productoptions = CartProductOption.query.filter_by(cart_id=cart.id).all()

            cart_total_price(cart, cart_products)

            point_obj = Point.query.filter_by(user_id=current_user.id).first()
            point_log_obj = PointLog.query.filter_by(cart_id=cart.id).first()
            if not point_log_obj:
                point_log_obj = cart_point_log_create(cart, point_obj)
            else:
                point_log_obj = cart_point_log_update(cart, point_obj)
            if _used_coupons:
                print("000000000000000000000000 사용쿠폰 있슴")
            else:
                print('========================================= 사용쿠폰 없슴')
            used_coupons_amount = cart.coupon_discount_total()
            base_pay_amount = BaseAmount.query.get(1).amount
            """혹시 cart_update 시 저장을 하지않고 넘어가면, cart_view 를 이용자가 새로고침하면 적용하기 위해"""
            over_discount_cart_apply(_used_coupons, point_log_obj.used_point, used_coupons_amount, cart, base_pay_amount, point_log_obj)

            customer_uid_obj = CustomerUid.query.filter_by(buyer_id=current_user.id).first()
            if customer_uid_obj:
                customer_uid = customer_uid_obj.customer_uid
            else:
                customer_uid = customer_uid_set(cart.id)

            context = {
                "cart_id": cart.id,
                'cart': cart,
                'cart_products': cart_products,
                'cart_productoptions': cart_productoptions,
                'items_total_count': len(cart_products),
                'cart_total_price': cart.cart_total_price,
                "get_total_delivery_pay": cart.get_total_delivery_pay(),

                'coupons': coupons,
                'used_coupons': _used_coupons,
                'add_coupon_form': add_coupon_form,

                'point_obj': point_obj,
                'point_log_obj': point_log_obj,  # 이거를 넘기면 첫 포인트 로그 생성시 값들이 넘어간다. 갱신되는 값에는 적용 못한다.
                'prep_point': cart.prep_point(),
                'used_point': cart.used_point(),
                'remained_point': cart.remained_point(),
                'new_remained_point': cart.new_remained_point(),  # used_point 가 없을 때 사용하기 위해 템플릿으로 넘긴다.
                'customer_uid': customer_uid,
            }
            return render_template('ecomm/carts/cart_view.html', context=context)
        else:
            abort(400)
    else:
        abort(401)


@carts.route('/cart/update/ajax', methods=['POST'])
@login_required
def cart_update_ajax():
    cart_id = request.form.get("cart_id")
    cart = Cart.query.get_or_404(cart_id)
    product_id = request.form.get("product_id")
    product_count = request.form.get("product_count")
    product_total_price = request.form.get("product_total_price")

    option_id = request.form.getlist("option_id[]")
    option_count = request.form.getlist("option_count[]")
    option_line_price = request.form.getlist("option_total_price[]")

    cartproduct = CartProduct.query.filter_by(cart_id=cart_id, product_id=product_id).first()
    cartproduct.product_subtotal_quantity = 0
    cartproduct.product_subtotal_price = 0
    cartproduct.op_subtotal_price = 0
    cartproduct_update(cartproduct, product_count, product_total_price)
    db.session.add(cartproduct)

    op_id = list()
    op_count = list()
    op_title = list()
    op_price = list()
    if option_id:
        for idx in range(len(option_id)):
            cartproductoption = CartProductOption.query.filter_by(cart_id=cart_id, option_id=int(option_id[idx])).first()

            if cartproductoption:
                cartproductoption.op_quantity = 0
                cartproductoption.op_line_price = 0
                cartproductoption_update(cartproductoption, idx, option_count, option_line_price)
                db.session.commit()

                temp_op_list_for_cart_update(op_id, op_count, op_title, op_price, idx, option_id, option_count, cartproductoption)
            else:
                option_obj = ProductOption.query.get_or_404(option_id[idx])
                new_cartproductoption = CartProductOption(cart_id=cart_id, product_id=product_id)
                new_cartproductoption_create(new_cartproductoption, option_obj, idx, option_id, option_count, option_line_price)
                db.session.commit()

                temp_op_list_for_cart_update(op_id, op_count, op_title, op_price, idx, option_id, option_count, new_cartproductoption)

            cartproduct_update_remnant(cartproduct, idx, option_line_price)
            db.session.commit()

    base_pay_amount = BaseAmount.query.get(1).amount
    used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
    used_coupons_amount = cart.coupon_discount_total()

    point_log = PointLog.query.filter_by(cart_id=cart.id).first()
    used_point = point_log.used_point

    over_discount_cart_apply(used_coupons, used_point, used_coupons_amount, cart, base_pay_amount, point_log)

    cart_products = CartProduct.query.filter_by(cart_id=cart.id).all()
    cart_total_price(cart, cart_products)
    point_obj = Point.query.filter_by(user_id=current_user.id).first()
    point_log_obj = cart_point_log_update(cart, point_obj)

    update_data_response = {
        "product_id": product_id,
        "pd_subtotal_qty": cartproduct.product_subtotal_quantity,
        "product_subtotal_price": cartproduct.product_subtotal_price,

        "op_id": op_id,
        "op_count": op_count,
        "op_title": op_title,
        "op_price": op_price,
        "cartproduct_op_subtotal_price": cartproduct.op_subtotal_price,
        "cartproduct_line_price": cartproduct.line_price,

        "cart_total_price": cart.cart_total_price,
        "get_total_price": cart.get_total_price(),
        "get_total_delivery_pay": cart.get_total_delivery_pay(),

        'coupon_total': cart.coupon_discount_total(),
        'point_log_id': point_log_obj.id,
        'used_point': point_log_obj.used_point,
        'prep_point': point_log_obj.prep_point,
        'new_remained_point': point_log_obj.new_remained_point,
    }
    return make_response(jsonify(update_data_response))


@carts.route('/cart/option/delete/ajax', methods=['POST'])
@login_required
def cart_option_delete_ajax():
    cart_id = request.form.get("cart_id")
    product_id = request.form.get("product_id")
    option_id = request.form.get("option_id")
    cart = Cart.query.get_or_404(cart_id)

    cartproduct = CartProduct.query.filter_by(cart_id=cart_id, product_id=product_id).first()
    cart_productoption = CartProductOption.query.filter_by(cart_id=cart_id, option_id=option_id).first()
    if cart_productoption:
        cartproduct.op_subtotal_price = cartproduct.op_subtotal_price - cart_productoption.op_line_price
        cartproduct.line_price = cartproduct.line_price - cart_productoption.op_line_price
        db.session.add(cartproduct)

        cart.cart_total_price = cart.cart_total_price - cart_productoption.op_line_price
        db.session.add(cart)

        db.session.delete(cart_productoption)
        db.session.commit()
        print("===================================== option", CartProductOption.query.filter_by(cart_id=cart_id, option_id=option_id).first())
        """SAWarning: Multiple rows returned with uselist=False for lazily-loaded attribute 'CartProductOption.cart_product'"""
        """, lazy='joined' 을 넣었다. 그러니까 오류가 없어진듯..."""

        delete_data_response = {
            "_success": "delete_success",
            "cart_pd_line_price": cartproduct.line_price,
        }
        return make_response(jsonify(delete_data_response))
    else:
        delete_data_response = {
            'unnecessary_ajax': "",
        }
        return make_response(jsonify(delete_data_response))


@carts.route('/cart/product/delete/ajax', methods=['POST'])
@login_required
def cart_product_delete_ajax():
    cart_id = request.form.get("cart_id")
    product_id = request.form.get("product_id")
    cart = Cart.query.get_or_404(cart_id)
    cartproduct = CartProduct.query.filter_by(cart_id=cart_id, product_id=product_id).first()
    if cartproduct:
        cart.cart_total_price = cart.cart_total_price - cartproduct.line_price
        db.session.add(cart)
        cartproductoptions = CartProductOption.query.filter_by(cart_id=cart_id, product_id=product_id).all()

        # models 에서 cascade='all, delete-orphan' 을 적용해서 cartproduct 를 삭제하면 그에 따른 cartproductoptions 은 같이 지워진다.
        # SAWarning: Multiple rows returned with uselist=False for lazily-loaded attribute 'CartProductOption.cart_product'
        # 아래처럼 적용하면 위 경고 문구가 출몰한다. cascade='all, delete-orphan' 을 적용을 없애면 아래처럼 직접 삭제해줘야 한다.
        if cartproductoptions:
            for cartpdop in cartproductoptions:
                db.session.delete(cartpdop)

        db.session.delete(cartproduct)
        db.session.commit()

    point_obj = Point.query.filter_by(user_id=current_user.id).first()
    point_log = PointLog.query.filter_by(cart_id=cart.id).first()
    used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
    used_coupons_amount = cart.coupon_discount_total()

    used_point = point_log.used_point
    base_pay_amount = BaseAmount.query.get(1).amount
    point_log_obj = cart_point_log_update(cart, point_obj)

    over_discount_cart_apply(used_coupons, used_point, used_coupons_amount, cart, base_pay_amount, point_log)
    print("cart.coupon_discount_total()", cart.coupon_discount_total())
    delete_data_response = {
        "_success": "delete_success",
        'coupon_total': cart.coupon_discount_total(),

        'used_point': point_log_obj.used_point,
        'prep_point': point_log_obj.prep_point,
        'new_remained_point': point_log_obj.new_remained_point,

        "cart_total_price": cart.cart_total_price,
        "get_total_price": cart.get_total_price(),
        "get_total_delivery_pay": cart.get_total_delivery_pay()
    }
    return make_response(jsonify(delete_data_response))
