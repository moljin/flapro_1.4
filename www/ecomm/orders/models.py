from configs import db
from www.commons.models import BaseModel

ORDER_STATUS = ('미결제',
                '결제확인중',
                '결제확인완료',
                '배송준비중',
                '배송중',
                '배송완료',
                '거래완료',
                '반송중',
                '반송확인중',
                '반송완료',
                '결제취소',
                '주문취소완료')


PAY_TYPE = ('카드결제',
            '가상계좌',
            '계좌이체')

VALIDATION_STATUS = ('not request',
                     'normal',
                     'abnormal')


class Order(BaseModel):
    __tablename__ = 'orders'
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    buyer = db.relationship('User', backref=db.backref('order_buyer_set'))

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='CASCADE'))
    cart = db.relationship('Cart', backref=db.backref('order_cart_set'))

    order_num = db.Column(db.String(50))
    name = db.Column(db.String(250), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phonenumber = db.Column(db.String(20), nullable=True)

    postal_code = db.Column(db.String(20), nullable=True)
    address = db.Column('주소', db.String(250), nullable=True)
    detail_address = db.Column('상세주소', db.String(250), nullable=True)
    extra_address = db.Column('주소 참고항목', db.String(250), nullable=True)

    order_memo = db.Column(db.String(250), nullable=True)

    is_paid = db.Column(db.Boolean(), nullable=False, default=False)
    is_display = db.Column(db.Boolean(), nullable=False, default=True)
    is_cancel = db.Column(db.Boolean(), nullable=False, default=False)
    """order 는 영원히 삭제 안되게..이용자가 삭제하더라도.false 로만 변경. 통계 보관..."""
    order_status = db.Column(db.String(250), default=ORDER_STATUS[0])  # , choices=ORDER_STATUS) # Form에서  적용
    merchant_order_id = db.Column(db.String(250), nullable=True)

    used_point = db.Column(db.Integer, default=0)
    get_point = db.Column(db.Integer, default=0)

    total_order_amount = db.Column(db.Integer, default=0)
    total_discount_amount = db.Column(db.Integer, default=0)
    get_total_amount = db.Column(db.Integer, default=0)
    total_delivery_pay_amount = db.Column(db.Integer, default=0)
    real_paid_amount = db.Column(db.Integer, default=0)

    def order_coupon_total(self):
        order_coupons = OrderCoupon.query.filter_by(order_id=self.id,
                                                    consumer_id=self.buyer_id,
                                                    is_paid=True,
                                                    is_cancel=False).all()
        total = 0
        if order_coupons:
            for order_coupon in order_coupons:
                print(order_coupon)
                total += order_coupon.amount
        return total


class OrderCoupon(BaseModel):
    __tablename__ = 'order_coupons'
    consumer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    consumer = db.relationship('User', backref=db.backref('ordercoupon_consumer_set'),
                               primaryjoin='foreign(OrderCoupon.consumer_id) == remote(User.id)')

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    owner = db.relationship('User', backref=db.backref('ordercoupon_owner_set'),
                            primaryjoin='foreign(OrderCoupon.owner_id) == remote(User.id)')

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Order', backref=db.backref('ordercoupon_order_set', cascade='all, delete-orphan'))

    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id', ondelete='CASCADE'))
    coupon = db.relationship('Coupon', backref=db.backref('ordercoupon_coupon_set'))

    code = db.Column(db.String(250))
    amount = db.Column(db.Integer, default="")
    is_paid = db.Column(db.Boolean(), nullable=False, default=True)
    is_cancel = db.Column(db.Boolean(), nullable=False, default=False)
    """결제하기 버튼을 누르면 order_coupon 객체 를 만든다.
    그래서, 결제하기 클릭후 완료하지 않고 도중에 벗어났다가, 결제하기를 누른경우와 구분하기 위해"""


class OrderProduct(BaseModel):
    __tablename__ = 'order_products'
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    buyer = db.relationship('User', backref=db.backref('orderproduct_buyer_set'))

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='CASCADE'))
    cart = db.relationship('Cart', backref=db.backref('orderproduct_cart_set'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Order', backref=db.backref('orderproduct_order_set', cascade='all, delete-orphan'))

    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    product = db.relationship('Product', backref=db.backref('orderproduct_product_set'))

    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id', ondelete='CASCADE'))
    shop = db.relationship('Shop', backref=db.backref('orderproduct_shop_set'))

    pd_title = db.Column(db.String(100))  #
    pd_price = db.Column(db.Integer, default="")
    applied_price = db.Column(db.Integer, default=0) #
    base_dc_amount = db.Column(db.Integer, default=0) #

    pd_subtotal_price = db.Column(db.Integer, default="")
    pd_subtotal_quantity = db.Column(db.Integer, default="")
    op_subtotal_price = db.Column(db.Integer, default="")
    line_price = db.Column(db.Integer, default="")


class OrderProductOption(BaseModel):
    __tablename__ = 'order_productoptions'
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    buyer = db.relationship('User', backref=db.backref('orderproductoption_buyer_set'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Order', backref=db.backref('orderproductoption_order_set', cascade='all, delete-orphan'))

    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    product = db.relationship('Product', backref=db.backref('orderproductoption_product_set'))

    option_id = db.Column(db.Integer, db.ForeignKey('product_options.id', ondelete='CASCADE'))
    option = db.relationship('ProductOption', backref=db.backref('orderoption_option_set'))

    op_title = db.Column(db.String(100), nullable=False)
    op_price = db.Column(db.Integer, default=0)
    op_quantity = db.Column(db.Integer, default=0)
    op_line_price = db.Column(db.Integer, default=0)


class OrderTransaction(BaseModel):
    __tablename__ = 'order_transactions'
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    buyer = db.relationship('User', backref=db.backref('ordertransaction_buyer_set'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Order', backref=db.backref('ordertransaction_order_set', cascade='all, delete-orphan'))

    amount = db.Column(db.Integer)
    merchant_order_id = db.Column(db.String(250), nullable=False)

    transaction_id = db.Column(db.String(120), nullable=True)
    type = db.Column(db.String(120), default="none")
    device = db.Column(db.String(120), nullable=True)

    is_success = db.Column(db.Boolean(), nullable=False, default=False)
    validation_status = db.Column(db.String(120), nullable=False, default=VALIDATION_STATUS[0])
    cancel_amount = db.Column(db.Integer, default=0)
    is_cancel = db.Column(db.Boolean(), nullable=False, default=False)


class CancelPayOrder(BaseModel):
    __tablename__ = 'cancelpay_orders'
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    buyer = db.relationship('User', backref=db.backref('cancelpay_buyer_set'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Order', backref=db.backref('cancelpay_order_set', cascade='all, delete-orphan'))

    ordertransaction_id = db.Column(db.Integer, db.ForeignKey('order_transactions.id', ondelete='CASCADE'))
    ordertransaction = db.relationship('OrderTransaction', backref=db.backref('cancelpay_ordertransaction_set'))

    order_title = db.Column(db.String(120))
    buyer_name = db.Column(db.String(120))
    cancel_amount = db.Column(db.Integer)
    cancel_reason = db.Column(db.String(120))
    merchant_uid = db.Column(db.String(250), nullable=False)
    type = db.Column(db.String(120), default="none")

    card_name = db.Column(db.String(120))
    card_number = db.Column(db.String(120))

    refund_holder = db.Column(db.String(120))
    refund_bank = db.Column(db.String(120))
    refund_account = db.Column(db.String(120))

    is_success = db.Column(db.Boolean(), nullable=False, default=False)


class CustomerUid(BaseModel):
    __tablename__ = 'customer_uids'
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    buyer = db.relationship('User', backref=db.backref('customeruid_buyer_set'))

    card_number = db.Column(db.String(120))
    card_expiry = db.Column(db.String(120))
    customer_uid = db.Column(db.String(250))


