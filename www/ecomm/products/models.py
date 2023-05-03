from sqlalchemy import func

from configs import db
from www.commons.models import BaseModel
from www.commons.utils import slugify


class ShopSubscriber(db.Model):
    __tablename__ = 'shop_subscribers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ShopSubscriber(user_id:'{self.user_id}', shop_id:'{self.shop_id}')>"


class Shop(BaseModel):
    __tablename__ = 'shops'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('shop_user_set'))

    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # meta_description 과 겸용으로 사용

    img_path_1 = db.Column(db.String(200), nullable=True)
    img_path_2 = db.Column(db.String(200), nullable=True)
    img_path_3 = db.Column(db.String(200), nullable=True)
    img_path_4 = db.Column(db.String(200), nullable=True)
    img_path_5 = db.Column(db.String(200), nullable=True)
    img_path_6 = db.Column(db.String(200), nullable=True)

    img_path = db.Column(db.String(200), nullable=True)  # symbol image
    view_count = db.Column(db.Integer, default=0)

    available_display = db.Column('Display', db.Boolean(), nullable=False, default=True)

    subscribers = db.relationship('User', secondary='shop_subscribers', backref=db.backref('shop_subscriber_set'))

    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title
        self.slug = slugify(self.title, allow_unicode=True)

    def __repr__(self):
        return f"<Shop('{self.id}', '{self.title}')>"

    def to_serialize(self):
        return {'id': self.id, 'title': self.title}


class ProductCategory(BaseModel):
    __tablename__ = 'product_categories'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('pc_user_set'))

    title = db.Column(db.String(200), nullable=False)

    available_display = db.Column('Display', db.Boolean(), nullable=False, default=True)

    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    shop = db.relationship('Shop', backref=db.backref('pc_shop_set', cascade='all, delete-orphan'))

    def to_serialize(self):
        return {'id': self.id, 'title': self.title}


class ProductVoter(db.Model):
    __tablename__ = 'product_voters'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class Product(BaseModel):
    __tablename__ = 'products'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('product_user_set'))

    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id', ondelete='CASCADE'))
    shop = db.relationship('Shop', backref=db.backref('product_shop_set'))

    pc_id = db.Column(db.Integer, db.ForeignKey('product_categories.id', ondelete='CASCADE'))
    pc = db.relationship('ProductCategory', backref=db.backref('product_pc_set'))

    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_description = db.Column(db.Text, nullable=True)

    img_path_1 = db.Column(db.String(200), nullable=True)
    img_path_2 = db.Column(db.String(200), nullable=True)
    img_path_3 = db.Column(db.String(200), nullable=True)

    view_count = db.Column(db.Integer, default=0)

    price = db.Column(db.Integer, nullable=True)  # default="")
    stock = db.Column(db.Integer)
    base_dc_amount = db.Column(db.Integer, nullable=True)  # 기본 할인금액
    delivery_pay = db.Column(db.Integer, nullable=True)  # 배송비

    available_display = db.Column('Display', db.Boolean(), nullable=False, default=True)
    available_order = db.Column('Order', db.Boolean(), nullable=False, default=True)

    voters = db.relationship('User', secondary='product_voters', backref=db.backref('product_voter_set'))

    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title
        self.slug = slugify(self.title, allow_unicode=True)

    def __repr__(self):
        return f"<Product('ID: {self.id}', 제목: '{self.title}')>"


class ProductSunImage(BaseModel):
    __tablename__ = 'product_sun_images'
    """Please set confirm_deleted_row s=False within the mapper configuration to prevent this warning."""
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('productsunimage_user_set'))

    img_path = db.Column(db.String(350), nullable=False)
    original_filename = db.Column(db.String(350), nullable=False)

    product = db.relationship('Product', backref=db.backref('sunimage_product_set', cascade='all, delete-orphan'),
                              primaryjoin='foreign(ProductSunImage.orm_id) == remote(Product.orm_id)')


class ProductOption(BaseModel):
    __tablename__ = 'product_options'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('productoption_user_set'))

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('productoption_product_set', cascade='all, delete-orphan'))

    title = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=True)

    available_display = db.Column('Display', db.Boolean(), nullable=False, default=True)
    available_order = db.Column('Order', db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return f"<ProductOption('ID: {self.id}', 제목: '{self.title}')>"


class ProductReview(BaseModel):
    __tablename__ = 'product_reviews'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('productreview_user_set'))

    content = db.Column(db.Text(), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('productreview_product_set', cascade='all, delete-orphan'))


class ProductReviewImage(BaseModel):
    __tablename__ = 'productreview_images'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('productreviewimage_user_set'))

    img_path = db.Column(db.String(350), nullable=False)
    original_filename = db.Column(db.String(350), nullable=True)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('productreviewimage_product_set', cascade='all, delete-orphan'))

    review_id = db.Column(db.Integer, db.ForeignKey('product_reviews.id'), nullable=False)
    product_review = db.relationship('ProductReview', backref=db.backref('productreview_image_set', cascade='all, delete-orphan'))


QUESTION_TYPES = ('상품', '배송', '반품/취소', '교환/변경', '기타')


class ProductQuestion(BaseModel):
    __tablename__ = 'product_questions'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('productquestion_user_set'))

    title = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(200), nullable=False, default=QUESTION_TYPES[0])
    content = db.Column(db.Text(), nullable=False)
    is_secret = db.Column(db.Boolean(), nullable=False, default=False)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('productquestion_product_set', cascade='all, delete-orphan'))


class ProductAnswer(BaseModel):
    __tablename__ = 'product_answers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('productanswer_user_set'))

    content = db.Column(db.Text(), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('productanswer_product_set', cascade='all, delete-orphan'))

    question_id = db.Column(db.Integer, db.ForeignKey('product_questions.id'), nullable=False)
    question = db.relationship('ProductQuestion', backref=db.backref('productanswer_question_set', cascade='all, delete-orphan'))


