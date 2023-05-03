import hashlib
import uuid

from flask import g
from flask_login import current_user

from configs import db
from www.commons.utils import random_word
from www.ecomm.orders.iamport import payments_prepare, find_transaction
from www.ecomm.orders.models import Order, OrderTransaction, CustomerUid, OrderProduct, OrderProductOption, PAY_TYPE, ORDER_STATUS, VALIDATION_STATUS, OrderCoupon
from www.ecomm.products.models import Product, ProductOption
from www.ecomm.promotions.models import UsedCoupon, Point
from www.ecomm.promotions.utils import coupon_count_update, order_point_update, coupon_count_cancel_update, order_point_cancel_update

prod = ''
option = ''


def new_order_coupon_create(order, used_coupon):
    new_order_coupon = OrderCoupon(
        order_id=order.id,
        coupon_id=used_coupon.coupon_id,
        code=used_coupon.code,
        amount=used_coupon.amount,
        owner_id=used_coupon.owner_id,
        consumer_id=used_coupon.consumer_id
    )
    g.db.bulk_save_objects([new_order_coupon])


def order_transaction_create(order_id, amount, success=None, transaction_status=None):
    if not order_id:
        raise ValueError("주문 정보 오류")
    order = Order.query.filter_by(id=order_id).first()
    random_str = str(uuid.uuid4())[:18]+"-"+random_word(10)+"-"+str(current_user.id)
    merchant_order_id = str(random_str)

    payments_prepare(merchant_order_id, amount)

    transaction = OrderTransaction(
        buyer_id=current_user.id,
        order_id=order_id,
        merchant_order_id=merchant_order_id,
        amount=amount
    )
    if success is not None:
        transaction.is_success = success
        transaction.transaction_status = transaction_status

    try:
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        print("save error", e)
    return transaction.merchant_order_id


def order_items_complete_transaction(order, cart, order_coupons):
    order_productitems = OrderProduct.query.filter_by(order_id=order.id).all()
    order_optionitems = OrderProductOption.query.filter_by(order_id=order.id).all()
    if order_productitems and not order_optionitems:
        product_only_stock_minus_update(order_productitems)
    if order_productitems and order_optionitems:
        product_and_option_stock_minus_update(order_productitems, order_optionitems)

    used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id, is_used=False, is_cancel=False).all()
    if used_coupons:
        coupon_count_update(used_coupons)
        for order_coupon in order_coupons:
            order_coupon.is_paid = True
            db.session.add(order_coupon)
            db.session.commit()

    point_obj = Point.query.filter_by(user_id=current_user.id).first()  # 카트에 담을때 이미 포인트객체를 만들어 놓는다.
    if point_obj:
        order_point_update(cart, order, point_obj)


def order_items_cancel_transaction(order_id, cart, order_coupons):
    order = Order.query.filter_by(id=order_id).first()
    order_productitems = OrderProduct.query.filter_by(order_id=order_id).all()
    order_optionitems = OrderProductOption.query.filter_by(order_id=order_id).all()
    if order_productitems and not order_optionitems:
        product_only_stock_plus_update(order_productitems)
    if order_productitems and order_optionitems:
        product_and_option_stock_plus_update(order_productitems, order_optionitems)

    used_coupons = UsedCoupon.query.filter_by(cart_id=cart.id, consumer_id=current_user.id).all()
    if used_coupons:
        coupon_count_cancel_update(used_coupons)
        for order_coupon in order_coupons:
            order_coupon.is_cancel = True
            db.session.add(order_coupon)
            db.session.commit()

    point_obj = Point.query.filter_by(user_id=current_user.id).first()  # 카트에 담을때 이미 포인트객체를 만들어 놓는다.
    if point_obj:
        order_point_cancel_update(cart, order, point_obj)


def order_transaction_remnant(trans, imp_uid):
    trans.transaction_id = imp_uid  # 미리 저장해놓으면 관리자든 고객이든 결제취소를 할 수 있다. (아임포트 결제 완료 but, 상점서버에 결제정보 저장과정 에러시에...)
    trans.is_success = True
    trans.type = PAY_TYPE[0]  # 가상계좌, 계좌이체 사용시 받아서 저장
    current_db_sessions = db.session.object_session(trans)
    current_db_sessions.add(trans)


def order_complete_save(order, merchant_uid):
    """order 에  merchant_id를 저장해놓아야
    order_detail 에서  merchant_id를 사용해서 결제 취소를 할 수 있다."""
    order.merchant_order_id = merchant_uid
    order.is_paid = True
    order.order_status = ORDER_STATUS[1]
    current_db_sessions = db.session.object_session(order)
    current_db_sessions.add(order)


def cart_complete_save(cart):
    cart.is_active = False
    cart.cart_id = '주문완료된 카트'
    current_db_sessions = db.session.object_session(cart)
    current_db_sessions.add(cart)


def order_complete_transaction(trans, imp_uid, order, cart):
    merchant_uid = trans.merchant_order_id

    order_transaction_remnant(trans, imp_uid)
    order_complete_save(order, merchant_uid)
    cart_complete_save(cart)
    db.session.commit()
    """장고에서도 post_save.connect(order_payment_validation, sender=OrderTransaction) 으로 모두 저장후에 connect"""
    iamport_client_validation(trans)  # trans 에 trans.transaction_id = imp_uid 가 저장되어 있어야 validation 가능


def product_only_stock_minus_update(order_products):
    global prod
    for order_product in order_products:
        prod = Product.query.filter_by(id=order_product.product_id).one()
        prod.stock -= order_product.pd_subtotal_quantity

    db.session.bulk_save_objects([prod])
    db.session.commit()


def product_and_option_stock_minus_update(order_products, order_options):
    global option
    product_only_stock_minus_update(order_products)

    for order_option in order_options:
        option = ProductOption.query.get(order_option.option_id)
        option.stock -= order_option.op_quantity
    db.session.bulk_save_objects([option])
    db.session.commit()


def product_only_stock_plus_update(order_products):
    global prod
    for order_product in order_products:
        prod = Product.query.filter_by(id=order_product.product_id).one()
        prod.stock += order_product.pd_subtotal_quantity

    db.session.bulk_save_objects([prod])
    db.session.commit()


def product_and_option_stock_plus_update(order_products, order_options):
    global option
    product_only_stock_plus_update(order_products)

    for order_option in order_options:
        option = ProductOption.query.get(order_option.option_id)
        option.stock += order_option.op_quantity
    db.session.bulk_save_objects([option])
    db.session.commit()


# get_transaction--find_transaction--order_payment_validation 통합 (
# def iamport_client_validation(merchant_id, order_id):
def iamport_client_validation(trans):
    """get_transaction--find_transaction 을 거치면서 아임포트와 통신해서
    imp_id를 받아내 local_transaction 을 찾아 확인하는 validation 한다."""
    # trans = OrderTransaction.query.filter_by(merchant_order_id=merchant_id, order_id=order_id).first()
    if trans.transaction_id:
        iamport_transaction = get_transaction(trans.merchant_order_id)
        print("iamport_transaction==============", iamport_transaction)

        merchant_order_id = iamport_transaction['merchant_order_id']
        imp_id = iamport_transaction['imp_id']
        amount = iamport_transaction['amount']
        local_transaction = db.session.query(db.exists().where(OrderTransaction.merchant_order_id == merchant_order_id,
                                                               OrderTransaction.transaction_id == imp_id,
                                                               OrderTransaction.amount == amount)).scalar()
        print('local_transaction : True====================', local_transaction)
        trans.validation_status = VALIDATION_STATUS[1]
        db.session.add(trans)
        db.session.commit()
        if not iamport_transaction or not local_transaction:
            trans.validation_status = VALIDATION_STATUS[2]
            db.session.add(trans)
            db.session.commit()
            raise ValueError("비정상 거래입니다.")


def get_transaction(merchant_order_id):
    result = find_transaction(merchant_order_id)
    if result['status'] == 'paid':
        return result
    else:
        return None


def customer_uid_set(cart_id):
    user_id = str(g.user.id)
    username = g.user.email.split('@')[0]
    random_string = random_word(7)

    # customer_uid = username + "&_100" + user_id + "_%$" + random_string + "?" + str(NOW.microsecond)
    customer_uid = username + "_100" + user_id + "_100" + str(cart_id)
    new_customer_uid_obj = CustomerUid(buyer_id=user_id, customer_uid=customer_uid)
    db.session.add(new_customer_uid_obj)
    db.session.commit()
    return customer_uid


def check_customer_uid(req_card_number, expiry, req_customer_uid):
    customer_uid_obj = CustomerUid.query.filter_by(user_id=current_user.id,
                                                   card_number=req_card_number,
                                                   customer_uid=req_customer_uid).first()
    if customer_uid_obj:
        customer_uid = customer_uid_obj.customer_uid
        return customer_uid
    else:
        new_customer_uid_obj = CustomerUid(user_id=current_user.id,
                                           card_number=req_card_number,
                                           card_expiry=expiry,
                                           customer_uid=req_customer_uid)
        db.session.add(new_customer_uid_obj)
        db.session.commit()
        customer_uid = new_customer_uid_obj.customer_uid
        return customer_uid

"""
def find_transaction:::res = req.json()::: 
{'code': 0, 
'message': None, 
'response': {'amount': 500, 'apply_num': '31887298', 'bank_code': None, 'bank_name': None, 'buyer_addr': None, 
            'buyer_email': 'pingclic@naver.com', 'buyer_name': 'Khandure', 'buyer_postcode': None, 'buyer_tel': None, 
            'cancel_amount': 0, 'cancel_history': [], 'cancel_reason': None, 'cancel_receipt_urls': [], 'cancelled_at': 0, 
            'card_code': '361', 'card_name': 'BC카드', 'card_number': '910020*********7', 'card_quota': 0, 'card_type': 0, 'cash_receipt_issued': False, 
            'channel': 'pc', 'currency': 'KRW', 'custom_data': None, 'customer_uid': None, 'customer_uid_usage': None, 'emb_pg_provider': None, 
            'escrow': False, 'fail_reason': None, 'failed_at': 0, 'imp_uid': 'imp_856028681571', 'merchant_uid': 'e6aa6e4de141b88ec1e3qvzaiifsrg', 'name': '테이블의 id 컬럼을 의미등', 
            'paid_at': 1666536080, 'pay_method': 'card', 'pg_id': 'INIpayTest', 'pg_provider': 'html5_inicis', 'pg_tid': 'StdpayISP_INIpayTest20221023234120614238', 
            'receipt_url': 'https://iniweb.inicis.com/DefaultWebApp/mall/cr/cm/mCmReceipt_head.jsp?noTid=StdpayISP_INIpayTest20221023234120614238&noMethod=1', 
            'started_at': 1666536028, 'status': 'paid', 'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 
            'vbank_code': None, 'vbank_date': 0, 'vbank_holder': None, 'vbank_issued_at': 0, 'vbank_name': None, 'vbank_num': None}}

def find_transaction(order_id, *args, **kwargs): return context
**********************context 
{'imp_id': 'imp_856028681571', 'merchant_order_id': 'e6aa6e4de141b88ec1e3qvzaiifsrg', 'amount': 500, 'status': 'paid', 'type': 'card', 
'receipt_url': 'https://iniweb.inicis.com/DefaultWebApp/mall/cr/cm/mCmReceipt_head.jsp?noTid=StdpayISP_INIpayTest20221023234120614238&noMethod=1'}

iamport_transaction = get_transaction(trans.merchant_order_id)
iamport_transaction============== 
{'imp_id': 'imp_856028681571', 'merchant_order_id': 'e6aa6e4de141b88ec1e3qvzaiifsrg', 'amount': 500, 'status': 'paid', 'type': 'card',
'receipt_url': 'https://iniweb.inicis.com/DefaultWebApp/mall/cr/cm/mCmReceipt_head.jsp?noTid=StdpayISP_INIpayTest20221023234120614238&noMethod=1'}
 
local_transaction : True==================== True
========================_validation:::  True

"""