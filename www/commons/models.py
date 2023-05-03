from sqlalchemy import func

from configs import db

"""
class ProductReview(BaseModel):
    # ....
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
           # cf. db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    # prod_review.product_id ===> products.id 와 연결 
    # ondelete='CASCADE' :: product delete 하면 null 로 된다. nullable=True 로 설정해야된다.
    # nullable 기본값은 True (nullable 을 따로 설정하지 않으면 해당 속성은 기본으로 빈값을 허용)
    
    product = db.relationship('Product', backref=db.backref('productreviewimage_product_set', cascade='all, delete-orphan'))
    # cascade='all, delete-orphan' : product 를 삭제하면 review data 도 삭제된다. 
        # 이 옵션을 적용하지 않으면 product_id 만 삭제되어 null 로 된다. 물론 product_id 의 nullable=True 로 설정해야된다.
    # ....     
# 이미지가 있는 object 를 삭제할때는, 해당 경로에 저장된 이미지까지 삭제해줘야 한다.!!!
"""


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    """orm_id : 특정 객체 하위에 객체를 관계형으로 생성하고자 할때, 
    상위의 특정 객체의 고유 ID가 생성되지 않은 경우(상위와 하위 객체를 동시에 생성할 때)에, orm_id를 기준으로 관계형성을 하기위해 사용한다. (sunImage 와 Tag 에서 사용했다.)
    cf. 상위 특정객체 고유 ID를 생성하게 commit()을 먼저 시행한 후에는, 상위 특정객체 고유 ID를 관계형성에 사용할 수 있다."""
    orm_id = db.Column(db.String(250), nullable=True)


class VarRatio(BaseModel):
    __tablename__ = 'var_ratios'
    title = db.Column(db.String(100), nullable=False)
    ratio = db.Column(db.Numeric(10, 4))


class BaseAmount(BaseModel):
    __tablename__ = 'base_amounts'
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, default="")


"""
# https://realpython.com/python-web-applications-with-flask-part-ii/
class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    # We will also proxy Flask-SqlAlchemy's get_or_44
    # for symmetry
    @classmethod
    def get_or_404(cls, id):
        return cls.query.get_or_404(id)

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()
"""
