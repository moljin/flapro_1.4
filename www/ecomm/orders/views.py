import datetime

from flask import Blueprint, request, g, make_response, jsonify, render_template, flash, url_for
from flask_login import current_user
from sqlalchemy import desc

from configs import db
from www.commons.required import login_required
from www.commons.utils import error_400_json_data
from www.ecomm.carts.models import Cart, CartProduct, CartProductOption
from www.ecomm.orders.forms import OrderCreateForm
from www.ecomm.orders.iamport import req_cancel_pay, onetime_pay_billing_key
from www.ecomm.orders.models import Order, OrderCoupon, OrderProduct, OrderProductOption, OrderTransaction, CancelPayOrder, CustomerUid
from www.ecomm.orders.utils import order_transaction_create, check_customer_uid, order_items_complete_transaction, order_complete_transaction, order_items_cancel_transaction, \
    new_order_coupon_create
from www.ecomm.promotions.models import PointLog, UsedCoupon, Coupon, Point

NAME = 'orders'
orders = Blueprint(NAME, __name__, url_prefix='/orders')


@orders.route('/request/init', methods=['POST'])
@login_required
def order_init():
    now = datetime.datetime.now()
    cart_id = request.form.get('cart_id')
    cart = Cart.query.filter_by(id=cart_id).first()
    print(cart)
    order = Order.query.filter_by(buyer_id=current_user.id, cart_id=cart.id).first()
    if not order:
        new_order = Order(
            buyer_id=current_user.id,
            cart_id=cart_id
        )
        g.db.add(new_order)
        g.db.commit()
        """order_num 에 order.id를 넣기위해 한번 커밋후 new_order 를 다시 불러옴"""
        new_order.order_num = str(new_order.id) + '-' + str(cart.id) + '-' + now.strftime(str(current_user.id)+'-%y%m%d%H%M'),  # '-%y%m%d%H%M%S%f'
        g.db.add(new_order)
    g.db.commit()
    data = {'_success': "success"}
    return make_response(jsonify(data), 200)


@orders.route('/create/ajax', methods=['POST'])
@login_required
def order_create_ajax():
    cart = Cart.query.filter_by(id=request.form.get("ordercart_id")).first()
    try:
        user_id = current_user.id
    except:
        user_id = None
    cart_productitems = CartProduct.query.filter_by(cart_id=cart.id).all()
    cart_optionitems = CartProductOption.query.filter_by(cart_id=cart.id).all()
    form = OrderCreateForm()
    if form.validate_on_submit():
        try:
            point_log = PointLog.query.filter_by(cart_id=cart.id).first()
        except Exception as e:
            print(e, 'no used_point')
            point_log = None
        order = Order.query.filter_by(buyer_id=user_id, cart_id=cart.id).first()
        order.name = request.form.get('name')
        order.email = request.form.get('email')
        order.phonenumber = request.form.get('phonenumber')
        order.postal_code = request.form.get('postal_code')
        order.address = request.form.get('address')
        order.detail_address = request.form.get('detail_address')
        order.extra_address = request.form.get('extra_address')
        order.order_memo = request.form.get('order_memo')

        order.used_point = point_log.used_point,
        order.get_point = cart.prep_point(),
        order.total_discount_amount = cart.discount_total_amount(),
        order.total_order_amount = cart.subtotal_price(),
        order.get_total_amount = cart.get_total_price(),
        order.total_delivery_pay_amount = cart.get_total_delivery_pay(),
        order.real_paid_amount = cart.get_real_pay_price()

        g.db.add(order)
        g.db.commit()

        used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
        old_order_coupons = OrderCoupon.query.filter_by(order_id=order.id, consumer_id=current_user.id).all()
        if used_coupons and old_order_coupons:
            for old_order_coupon in old_order_coupons:
                db.session.delete(old_order_coupon)
            db.session.commit()
            for used_coupon in used_coupons:
                new_order_coupon_create(order, used_coupon)
            g.db.commit()
        elif used_coupons and (not old_order_coupons):
            for used_coupon in used_coupons:
                new_order_coupon_create(order, used_coupon)
            g.db.commit()
        elif (not used_coupons) and old_order_coupons:
            for order_coupon in old_order_coupons:
                db.session.delete(order_coupon)
            db.session.commit()

        for cart_productitem in cart_productitems:
            existing_order_product = OrderProduct.query.filter_by(order_id=order.id, product_id=cart_productitem.product_id).first()
            if existing_order_product:
                existing_order_product.pd_title = cart_productitem.title,
                existing_order_product.pd_price = cart_productitem.price,
                existing_order_product.applied_price = cart_productitem.applied_price,
                existing_order_product.base_dc_amount = cart_productitem.base_dc_amount,
                existing_order_product.pd_subtotal_price = cart_productitem.product_subtotal_price,
                existing_order_product.pd_subtotal_quantity = cart_productitem.product_subtotal_quantity,
                existing_order_product.op_subtotal_price = cart_productitem.op_subtotal_price,
                existing_order_product.line_price = cart_productitem.line_price
                g.db.bulk_save_objects([existing_order_product])
            else:
                new_order_productitem = OrderProduct(
                    buyer_id=user_id,
                    cart_id=cart.id,
                    order_id=order.id,
                    product_id=cart_productitem.product_id,
                    shop_id=cart_productitem.shop_id,
                    pd_title=cart_productitem.title,
                    pd_price=cart_productitem.price,
                    applied_price=cart_productitem.applied_price,
                    base_dc_amount=cart_productitem.base_dc_amount,
                    pd_subtotal_price=cart_productitem.product_subtotal_price,
                    pd_subtotal_quantity=cart_productitem.product_subtotal_quantity,
                    op_subtotal_price=cart_productitem.op_subtotal_price,
                    line_price=cart_productitem.line_price
                )
                g.db.bulk_save_objects([new_order_productitem])
        g.db.commit()
        if cart_optionitems:
            for cart_optionitem in cart_optionitems:
                existing_order_option = OrderProductOption.query.filter_by(order_id=order.id, option_id=cart_optionitem.option_id).first()
                if existing_order_option:
                    existing_order_option.op_price = cart_optionitem.price,
                    existing_order_option.op_quantity = cart_optionitem.op_quantity,
                    existing_order_option.op_line_price = cart_optionitem.op_line_price
                    g.db.bulk_save_objects([existing_order_option])
                else:
                    new_order_optionitem = OrderProductOption(
                        buyer_id=user_id,
                        order_id=order.id,
                        product_id=cart_optionitem.product_id,
                        option_id=cart_optionitem.option_id,
                        op_title=cart_optionitem.title,
                        op_price=cart_optionitem.price,
                        op_quantity=cart_optionitem.op_quantity,
                        op_line_price=cart_optionitem.op_line_price
                    )
                    g.db.bulk_save_objects([new_order_optionitem])
            g.db.commit()

        """여기서부터는 기존 오더에서 변경된 오더를 반영한다.
        카트에서 삭제된 오더상품과 오더옵션을 제거하는 과정이다."""
        order_productitems = OrderProduct.query.filter_by(order_id=order.id).all()
        order_optionitems = OrderProductOption.query.filter_by(order_id=order.id).all()

        real_order_products = []
        real_order_options = []
        for cart_product in cart_productitems:
            for order_product in order_productitems:
                if order_product.product_id == cart_product.product_id:
                    real_order_products.append(order_product)
        for cart_option in cart_optionitems:
            for order_option in order_optionitems:
                if order_option.option_id == cart_option.option_id:
                    real_order_options.append(order_option)

        deleted_order_products = set(order_productitems) - set(real_order_products)
        if deleted_order_products:
            for deleted in deleted_order_products:
                db.session.delete(deleted)
            db.session.commit()
        deleted_order_options = set(order_optionitems) - set(real_order_options)
        if deleted_order_options:
            for deleted in deleted_order_options:
                db.session.delete(deleted)
            db.session.commit()

        data = {'order_id': order.id}
        # data = {'order_id': new_order.id}
        return make_response(jsonify(data), 200)
    else:
        message = '어딘가 올바르지 않게 입력되었어요!!'
        return make_response(jsonify({'message': message}), 401)


merchant_order_id = ""


@orders.route('/checkout/ajax', methods=['POST'])
@login_required
def order_checkout_ajax():
    global merchant_order_id
    cart_id = request.form['cart_id']
    cart = Cart.query.filter_by(id=cart_id).first()
    order_id = request.form['order_id']
    req_amount = request.form['amount']

    try:
        """서버에 저장된 카트의 실 결제금액과 결제요청이 들어온 결제금액의 일치여부를 확인한다.
        (템플릿단에서 금액을 조작해서 결제요청하는 것을 차단하기 위해서)"""
        if cart.get_real_pay_price() == int(req_amount):
            merchant_order_id = order_transaction_create(order_id=order_id, amount=req_amount)
            order_products = OrderProduct.query.filter_by(order_id=order_id).all()
            order_options = OrderProductOption.query.filter_by(order_id=order_id).all()
        else:
            merchant_order_id = None
    except Exception as e:
        print(e)
        merchant_order_id = None
    print("def order_checkout_ajax(): :: merchant_order_id", merchant_order_id)
    if merchant_order_id is not None:
        data = {  # checkout.js: OrderCheckoutAjax 로 넘기는 data
            "works": True,
            "_message": "order_checkout_ajax: success",
            "merchant_id": merchant_order_id
        }
        return make_response(jsonify(data), 200)
    else:  # 템플린단에서 조작한 amount 를 보내면 여기로 들어온다.
        message = '[Error 401] 인증되지 않은 요청이에요!\n입력내용을 확인해주세요!'
        return make_response(jsonify({'_message': message}), 401)


@orders.route('/imp/ajax', methods=['POST'])
@login_required
def order_imp_transaction():
    """모바일 결제 완료시에는 여기를 거치지 않는다. PC 만 여기를 거친다."""
    cart = Cart.query.filter_by(id=request.form.get("cart_id")).first()
    point_log = PointLog.query.filter_by(cart_id=cart.id).first()
    order_id = request.form['order_id']
    order = Order.query.filter_by(id=order_id).first()
    order_coupons = OrderCoupon.query.filter_by(order_id=order_id).all()

    merchant_id = request.form['merchant_id']
    imp_uid = request.form['imp_id']
    amount = request.form['amount']
    # # 구매 메일링 여기에 넣으면 될 듯...

    try:
        trans = OrderTransaction.query.filter_by(
            order_id=order_id,
            merchant_order_id=merchant_id,
            amount=amount
        ).first()
    except:
        trans = None

    if trans is not None:
        """일단 결제가 승인되어 완료되면 transaction_id는 저장을 해둬야 이용자가 취소 가능하다."""
        order_complete_transaction(trans, imp_uid, order, cart)
        order_items_complete_transaction(order, cart, order_coupons)

        data = {
            "works": True,
            "order_id": order_id,
            "merchant_order_id": merchant_id
        }

        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify({}), 401)


@orders.route('/pay/complete/mobile', methods=['GET'])
@login_required
def order_complete_mobile():
    """모바일에서 결제가 완료되면 리다이렉트 되면서, 아임포트에서 날라오는 get_data 4개"""
    imp_uid = request.args.get("imp_uid")
    merchant_uid = request.args.get("merchant_uid")
    imp_success = request.args.get("imp_success")
    error_msg = request.args.get("error_msg")

    m_trans = OrderTransaction.query.filter_by(merchant_order_id=merchant_uid).first()
    """일단 결제가 승인되어 완료되면 transaction_id는 저장을 해둬야 이용자가 취소 가능하다."""

    order_id = m_trans.order_id
    m_order = Order.query.filter_by(id=order_id).first()
    cart = Cart.query.filter_by(id=m_order.cart_id).first()

    m_order_productitems = OrderProduct.query.filter_by(order_id=order_id).all()
    m_order_optionitems = OrderProductOption.query.filter_by(order_id=order_id).all()
    m_order_coupons = OrderCoupon.query.filter_by(order_id=order_id).all()
    m_point_log = PointLog.query.filter_by(cart_id=cart.id).first()
    m_cancel_pay = CancelPayOrder.query.filter_by(order_id=order_id, is_success=True).first()

    if imp_success == "true":
        """아임포트에서 imp_success 키에 string 으로 true 를 담아서 보내준다.
         모바일 결제완료시에는 order_imp_transaction 을 거치지 않으므로 여기에서 시행해줘야 한다."""
        if not m_trans.device:
            m_trans.device = "mobile"
            db.session.add(m_trans)
            db.session.commit()
            """첫 결제시에는 if 문을 통과 하면서 iamport_client_validation(m_trans)을 거친다.
            그리고, 같은 페이지를 리로드시 if 문을 통과하지 않아야 에러 없다."""
            order_complete_transaction(m_trans, imp_uid, m_order, cart)
            order_items_complete_transaction(m_order, cart, m_order_coupons)

    return render_template('ecomm/orders/order_complete_detail.html',
                           cart=cart,
                           order=m_order,
                           order_productitems=m_order_productitems,
                           order_optionitems=m_order_optionitems,
                           order_transaction=m_trans,
                           point_log=m_point_log,
                           order_coupons=m_order_coupons,
                           cancel_pay=m_cancel_pay,
                           device="mobile",

                           imp_uid=imp_uid,
                           merchant_uid=merchant_uid,
                           imp_success=imp_success,
                           error_msg=error_msg
                           )


@orders.route('/complete/detail', methods=['GET'])
@login_required
def order_complete_detail():
    """PC 에서 결제가 완료되면 여기로 리다이렉트 된다."""
    merchant_uid = request.args.get("merchant_order_id")
    order_id = request.args.get("order_id")
    pc_order = Order.query.filter_by(id=order_id).first()
    cart = Cart.query.filter_by(id=pc_order.cart_id).first()

    pc_order_products = OrderProduct.query.filter_by(order_id=order_id).all()
    pc_order_options = OrderProductOption.query.filter_by(order_id=order_id).all()
    pc_order_coupons = OrderCoupon.query.filter_by(order_id=order_id, is_paid=True).all()
    point_log = PointLog.query.filter_by(order_id=order_id, cart_id=cart.id).first()
    pc_cancel_pay = CancelPayOrder.query.filter_by(order_id=order_id, is_success=True).first()

    pc_trans = OrderTransaction.query.filter_by(order_id=order_id, merchant_order_id=merchant_uid).first()
    if not pc_trans.device:
        """모바일에서 결제진행한것에는 mobile 로 입력되어 있기 때문에,
         pc 에서 모바일 결제된 경우 pc 에서 열어볼 경우, 이것을 pc로 변경되지 않게 하기 위해"""
        pc_trans.device = "pc"
        db.session.add(pc_trans)
        db.session.commit()
    return render_template('ecomm/orders/order_complete_detail.html',
                           cart=cart,
                           order=pc_order,
                           order_productitems=pc_order_products,
                           order_optionitems=pc_order_options,
                           order_transaction=pc_trans,
                           point_log=point_log,
                           order_coupons=pc_order_coupons,
                           cancel_pay=pc_cancel_pay,
                           # imp_success="false",
                           device="pc")


@orders.route('/complete/list', methods=['GET'])
@login_required
def order_complete_list():
    order_objs = Order.query.filter_by(buyer_id=current_user.id, is_paid=True, is_display=True).order_by(desc(Order.created_at)).all()
    point_obj = Point.query.filter_by(user_id=current_user.id).first()
    carts = Cart.query.filter_by(user_id=current_user.id).all()
    order_optionitems = OrderProductOption.query.filter_by(buyer_id=current_user.id).all()
    point_logs = PointLog.query.filter_by(user_id=current_user.id).all()
    order_coupons = OrderCoupon.query.filter_by(consumer_id=current_user.id, is_paid=True).all()
    trans_all = OrderTransaction.query.filter_by(buyer_id=current_user.id).all()
    all_orders_with_transaction_fail = Order.query.filter_by(buyer_id=current_user.id).order_by(desc(Order.created_at)).all()

    return render_template('ecomm/orders/order_complete_list.html',
                           orders=order_objs,
                           point_obj=point_obj,
                           # carts=carts, # order.cart.get_total_delivery_pay() 를 사용
                           # order_optionitems=order_optionitems,
                           # point_logs=point_logs,
                           # order_coupons=order_coupons,
                           # trans_all=trans_all, # order.order_ordertransaction_set 을 사용하면 된다.
                           # all_orders=all_orders_with_transaction_fail  # 임시로 볼려고 해놨다.
                           )


@orders.route('/cancel/pay/ajax', methods=['POST'])
@login_required
def cancel_pay_ajax():
    merchant_uid = request.form.get("merchant_uid")
    req_cancel_amount = request.form.get("cancel_amount")
    cancel_reason = request.form.get("cancel_reason")
    pay_type = request.form.get("pay_type")
    """가상계좌의 경우 단방향 결제수단이여서 환불 대상을 알 수 없으므로, 
    환불 금액 외에 다음의 환불 수령계좌 정보를 입력해야 합니다."""
    refund_holder = request.form.get("refund_holder")
    refund_bank = request.form.get("refund_bank")
    refund_account = request.form.get("refund_account")
    order_trans = OrderTransaction.query.filter_by(merchant_order_id=merchant_uid).first()
    if order_trans:
        cancelable_amount = order_trans.amount - order_trans.cancel_amount
        if cancelable_amount <= 0:
            # data = {
            #     "_success": "이미 전액 환불된 주문입니다."
            # }
            flash("이미 전액 환불된 주문입니다.")
            data = {"_success": "success", }
            return make_response(jsonify(data), 200)
        print("아임포트 REST API 로 결제환불 요청")
        imp_uid = order_trans.transaction_id
        cancel_response = req_cancel_pay(cancel_reason, imp_uid, req_cancel_amount, cancelable_amount)
        print("req_cancel_response", cancel_response)

        buyer_id = current_user.id
        order_id = order_trans.order_id
        ordertransaction_id = order_trans.id
        merchant_uid = cancel_response['response']['merchant_uid']
        try:
            cancel_pay = CancelPayOrder.query.filter_by(
                buyer_id=buyer_id,
                order_id=order_id,
                ordertransaction_id=ordertransaction_id,
                merchant_uid=merchant_uid,
            ).first()
        except:
            cancel_pay = None

        # code = cancel_response['code']
        order_title = cancel_response['response']['name']
        buyer_name = cancel_response['response']['buyer_name']
        cancel_amount = cancel_response['response']['cancel_amount']
        cancel_reason = cancel_response['response']['cancel_reason']
        # imp_uid = cancel_response['response']['imp_uid']
        # pay_method = cancel_response['response']['pay_method']

        card_name = cancel_response['response']['card_name']
        card_number = cancel_response['response']['card_number']
        if cancel_pay is None:
            new_cancel_pay = CancelPayOrder(buyer_id=buyer_id,
                                            order_id=order_id,
                                            ordertransaction_id=ordertransaction_id,
                                            merchant_uid=merchant_uid,
                                            order_title=order_title,
                                            buyer_name=buyer_name,
                                            cancel_amount=cancel_amount,
                                            cancel_reason=cancel_reason,
                                            type=pay_type,
                                            card_name=card_name,
                                            card_number=card_number,
                                            is_success=True)
            db.session.add(new_cancel_pay)

            order_trans.is_cancel = True
            order_trans.cancel_amount = cancel_amount
            db.session.add(order_trans)
            db.session.commit()

            order = Order.query.filter_by(id=order_trans.order_id).first()
            order.is_cancel = True
            db.session.add(order)
            db.session.commit()
            cart = Cart.query.filter_by(id=order.cart_id).first()
            order_coupons = OrderCoupon.query.filter_by(order_id=order_id).all()
            order_items_cancel_transaction(order_id, cart, order_coupons)
        else:
            print("나중에 부분결제가 있는 경우 적용할 계획")
        # data = {
        #     "_success": "success",
        #     "flash_message": "결제취소가 정상적으로 완료되었습니다."
        # }
        flash("정상적으로 결제가 취소되었습니다.")
        data = {"_success": "success",}
        return make_response(jsonify(data), 200)

    else:
        # flash("결제한 내용이 없습니다.")
        # return redirect(request.referrer)
        # data = {
        #     "_success": "fail error"
        # }
        flash("Fail Error")
        data = {"_success": "success", }
        return make_response(jsonify(data), 200)


@orders.route('order/delete/ajax', methods=['POST'])
@login_required
def order_delete_ajax():
    """삭제하지는 않고, is_display == False"""
    order_id = request.form.get("order_id")
    if order_id:
        target_order = Order.query.filter_by(id=order_id).first()
        target_order.is_display = False
        db.session.add(target_order)
        db.session.commit()
        # flash("주문정보가 삭제되었습니다.")
        data = {"_success": "success",
                "_delete": "delete",
                "redirect_url": url_for("orders.order_complete_list")}
        return make_response(jsonify(data), 200)
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@orders.route('order/complete/delete/ajax', methods=['POST'])
@login_required
def order_complete_delete_ajax():
    """Admin 단에서 UsedCoupon, PointLog 를 포함하여, 주문과 관련된 모든 정보를 삭제한다.
    PointLog 는 cascade delete 가 적용되어 있지만, UsedCoupon 은 직접 삭제해줘야 한다."""
    pass


@orders.route('billing/key/checkout/ajax', methods=['POST'])
@login_required
def billing_key_checkout_ajax():
    card_num1 = request.form.get('card_num1')
    card_num2 = request.form.get('card_num2')
    card_num3 = request.form.get('card_num3')
    card_num4 = request.form.get('card_num4')
    req_card_number = card_num1 + "-" + card_num2 + "-" + card_num3 + "-" + card_num4
    # card_number = card_num1 + card_num2 + card_num3 + card_num4
    expiry_num1 = request.form.get('expiry_num1')
    expiry_num2 = request.form.get('expiry_num2')
    expiry = "20" + expiry_num1 + "-" + expiry_num2
    # expiry = "20" + expiry_num1 + expiry_num2
    # print('"20" + expiry_num1 + "-" + expiry_num2', expiry)
    birth = request.form.get('birth')
    pwd_2digit = request.form.get('pwd_2digit')
    merchant_uid = request.form.get('merchant_uid')
    amount = request.form.get('amount')

    req_customer_uid = request.form.get('customer_uid')
    customer_uid_obj = CustomerUid.query.filter_by(user_id=current_user.id, customer_uid=req_customer_uid).first()
    print("customer_uid_obj", customer_uid_obj)
    customer_uid = check_customer_uid(req_card_number, expiry, req_customer_uid)
    print("customer_uid", customer_uid)

    # billing_key_response = req_billing_key(req_card_number, expiry, birth, pwd_2digit, customer_uid)
    billing_key_response = onetime_pay_billing_key(req_card_number, expiry, birth, pwd_2digit, customer_uid, merchant_uid, amount)
    # billing_key_response = onetime_pay_without_key(req_card_number, expiry, birth, merchant_uid, amount)
    print("billing_key_response::: ", billing_key_response)

    data = {
        "_success": "billing_key_checkout_ajax:: success",
        "billing_key_response": billing_key_response
    }
    return make_response(jsonify(data), 200)


"""
a = {'code': 0, 
    'message': None,
   'response': {'amount': 500, 'apply_num': '68767364', 'bank_code': None, 'bank_name': None, 'buyer_addr': None, 'buyer_email': 'moljin@naver.com', 'buyer_name': '양성훈', 'buyer_postcode': None,
                'buyer_tel': None, 'cancel_amount': 500, 
                'cancel_history': [{'pg_tid': 'StdpayISP_INIpayTest20221018174537673783', 'amount': 500, 'cancelled_at': 1666082753, 'reason': '테스트',
                                                                             'receipt_url': 'https://iniweb.inicis.com/DefaultWebApp/mall/cr/cm/mCmReceipt_head.jsp?noTid=StdpayISP_INIpayTest20221018174537673783&noMethod=1'}],
                'cancel_reason': '테스트', 'cancel_receipt_urls': ['https://iniweb.inicis.com/DefaultWebApp/mall/cr/cm/mCmReceipt_head.jsp?noTid=StdpayISP_INIpayTest20221018174537673783&noMethod=1'],
                'cancelled_at': 1666082753, 'card_code': '361', 'card_name': 'BC카드', 'card_number': '910020*********7', 'card_quota': 0, 'card_type': 0, 'cash_receipt_issued': False, 'channel': 'pc',
                'currency': 'KRW', 'custom_data': None, 'customer_uid': None, 'customer_uid_usage': None, 'emb_pg_provider': None, 'escrow': False, 'fail_reason': None, 'failed_at': 0,
                'imp_uid': 'imp_238673674012', 'merchant_uid': 'b28c2a7412357341fdc8', 'name': '홈오피스PC등', 'paid_at': 1666082737, 'pay_method': 'card', 'pg_id': 'INIpayTest',
                'pg_provider': 'html5_inicis', 'pg_tid': 'StdpayISP_INIpayTest20221018174537673783',
                'receipt_url': 'https://iniweb.inicis.com/DefaultWebApp/mall/cr/cm/mCmReceipt_head.jsp?noTid=StdpayISP_INIpayTest20221018174537673783&noMethod=1', 'started_at': 1666082673,
                'status': 'cancelled', 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 'vbank_code': None,
                'vbank_date': 0, 'vbank_holder': None, 'vbank_issued_at': 0, 'vbank_name': None, 'vbank_num': None}}
"""
