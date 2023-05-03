from flask_login import UserMixin

from configs import db
from www.commons.models import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(110), nullable=False)
    auth_token = db.Column(db.String(110), nullable=True)
    password_token = db.Column(db.String(110), nullable=True)
    admin_token = db.Column(db.String(110), nullable=True)

    is_use = db.Column('이용약관', db.Boolean, default=False, nullable=False)
    is_info = db.Column('개인정보수집', db.Boolean, default=False, nullable=False)
    is_email = db.Column('이메일수집거부', db.Boolean, default=False, nullable=False)
    is_bank = db.Column('전자거래', db.Boolean, default=False, nullable=False)
    is_marketing = db.Column('마케팅동의', db.Boolean, default=False, nullable=False)
    is_third = db.Column('3자제공', db.Boolean, default=False, nullable=False)

    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_vendor = db.Column(db.Boolean(), default=False, nullable=False)
    is_staff = db.Column(db.Boolean(), default=False, nullable=False)
    is_admin = db.Column(db.Boolean(), default=False, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<User('{self.id}', '{self.email}')>"


PROFILE_LEVELS = ('일반이용자', '심사중 판매사업자', '판매사업자')


class Profile(BaseModel):
    __tablename__ = 'profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('profile_user_set'))

    nickname = db.Column(db.String(100), nullable=False, unique=True)
    message = db.Column(db.Text, nullable=False)
    profile_img_path = db.Column(db.String(200), nullable=True)
    cover_img_path = db.Column(db.String(200), nullable=True)

    level = db.Column(db.String(200), nullable=False, default=PROFILE_LEVELS[0])

    corp_brand = db.Column(db.String(120), nullable=True, default=None)
    corp_email = db.Column(db.String(120), nullable=True, default=None)
    corp_number = db.Column('사업자등록번호', db.String(20), nullable=True, default=None)
    corp_online_marketing_number = db.Column('통신판매업번호', db.String(30), nullable=True, default=None)
    corp_img_path = db.Column('사업자등록증', db.String(200), nullable=True, default=None)
    corp_address = db.Column(db.String(120), nullable=True, default=None)
    main_phonenumber = db.Column(db.String(20), nullable=True, default=None)
    main_cellphone = db.Column(db.String(20), nullable=True, default=None)

    def __init__(self, nickname, message, user_id):
        self.user_id = user_id
        self.nickname = nickname
        self.message = message

    def __repr__(self):
        return f"<Profile('{self.id}', '{self.nickname}')>"
