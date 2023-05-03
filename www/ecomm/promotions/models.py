from configs import db
from www.commons.models import BaseModel


class Coupon(BaseModel):
    __tablename__ = 'coupons'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user = db.relationship('User', backref=db.backref('coupon_owner_set'))

    code = db.Column(db.String(250), unique=True, nullable=False)
    use_from = db.Column(db.DateTime())
    use_to = db.Column(db.DateTime())
    amount = db.Column(db.Integer, default=0)
    is_active = db.Column('Active', db.Boolean(), nullable=False, default=True)
    available_count = db.Column(db.Integer, default=0)
    used_count = db.Column(db.Integer, default=0)

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f"<Coupon('ID:{self.id}', product:'{self.code}')>"


class UsedCoupon(BaseModel):
    __tablename__ = 'used_coupons'
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    owner = db.relationship('User', backref=db.backref('usedcoupon_owner_set'),
                            primaryjoin='foreign(UsedCoupon.owner_id) == remote(User.id)')

    consumer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    consumer = db.relationship('User', backref=db.backref('usedcoupon_consumer_set'),
                               primaryjoin='foreign(UsedCoupon.consumer_id) == remote(User.id)')

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='CASCADE'))
    cart = db.relationship('Cart', backref=db.backref('usedcoupon_cart_set'))

    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id', ondelete='CASCADE'))
    coupon = db.relationship('Coupon', backref=db.backref('usedcoupon_coupon_set'))

    code = db.Column(db.String(250))
    amount = db.Column(db.Integer, default=0)
    is_used = db.Column(db.Boolean(), nullable=False, default=True)
    is_cancel = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"<UsedCoupon('ID:{self.id}', code:'{self.code}')>"

    def __init__(self, cart_id, coupon_id, owner_id, consumer_id):
        self.cart_id = cart_id
        self.coupon_id = coupon_id
        self.owner_id = owner_id
        self.consumer_id = consumer_id


class Point(BaseModel):
    __tablename__ = 'points'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('point_owner_set'))

    total_accum_point = db.Column(db.Integer, default=0)
    remained_point = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Point('ID:{self.id}', product:'{self.user_id}')>"

    def __init__(self, user_id):
        self.user_id = user_id


class PointLog(BaseModel):
    __tablename__ = 'point_logs'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('pointlog_user_set'))

    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='CASCADE'))
    cart = db.relationship('Cart', backref=db.backref('pointlog_cart_set'))

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Order', backref=db.backref('pointlog_order_set', cascade='all, delete-orphan'))

    point_id = db.Column(db.Integer, db.ForeignKey('points.id', ondelete='CASCADE'))
    point = db.relationship('Point', backref=db.backref('pointlog_point_set'))

    prep_point = db.Column(db.Integer, default=0)
    used_point = db.Column(db.Integer, default=0)
    new_remained_point = db.Column(db.Integer, default=0)

    is_cancel = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"<PointLog('ID:{self.id}', cart_id:'{self.cart_id}')>"

    def __init__(self, user_id):
        self.user_id = user_id
