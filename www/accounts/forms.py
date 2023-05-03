from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, EmailField, PasswordField, BooleanField
from wtforms.validators import Length, EqualTo, InputRequired


class AccountsForm(FlaskForm):
    username = StringField("username", validators=[Length(min=3, max=30)], render_kw={"placeholder": "아이디"})
    email = EmailField('email', validators=[Length(min=5, max=120)], render_kw={"placeholder": "이메일"})
    password = PasswordField('password', validators=[Length(min=9, max=20), EqualTo('repassword', message='입력한 비밀번호가 서로 달라요 . . .')], render_kw={"placeholder": "비밀번호"})
    repassword = PasswordField('repassword', validators=[Length(min=9, max=20)], render_kw={"placeholder": "비밀번호 확인"})
    auth_token = StringField("인증토큰", validators=[Length(min=2, max=100)], render_kw={"placeholder": "인증토큰"})
    password_token = StringField("비밀번호 토큰", validators=[Length(min=2, max=100)], render_kw={"placeholder": "비밀번호 토큰"})
    admin_token = StringField("관리자 토큰", validators=[Length(min=2, max=100)], render_kw={"placeholder": "관리자 토큰"})
    is_verified = BooleanField('회원 인증')
    is_staff = BooleanField('중간관리자 인증')
    is_vendor = BooleanField('판매사업자 신청가능')
    is_admin = BooleanField('관리자 인증')


class LoginForm(FlaskForm):
    username = StringField("username", validators=[InputRequired(), Length(min=3, max=30)], render_kw={"placeholder": "아이디"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "비밀번호"})


class UsernameForm(FlaskForm):
    username = StringField("username", validators=[InputRequired(), Length(min=3, max=30)], render_kw={"placeholder": "아이디"})


class EmailForm(FlaskForm):
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=120)], render_kw={"placeholder": "이메일"})


class PasswordUpdateForm(FlaskForm):
    password = PasswordField('password', validators=[InputRequired(), Length(min=9, max=20), EqualTo('repassword', message='입력한 비밀번호가 서로 달라요 . . .')], render_kw={"placeholder": "비밀번호"})
    repassword = PasswordField('repassword', validators=[InputRequired(), Length(min=9, max=20)], render_kw={"placeholder": "비밀번호 확인"})


class ProfilesForm(FlaskForm):
    nickname = StringField("닉네임", validators=[Length(min=2, max=100)], render_kw={"placeholder": "닉네임"})
    message = TextAreaField("메시지", validators=[Length(min=2, max=100)], render_kw={"placeholder": "간단 메시지"})
    profile_image = FileField("프로필 이미지",  render_kw={"placeholder": "프로필 이미지"})
    cover_image = FileField("커버 이미지", render_kw={"placeholder": "커버 이미지"})

    corp_brand = StringField("회사명", validators=[Length(min=1, max=100)], render_kw={"placeholder": "회사명"})
    corp_email = StringField("사업자용 이메일", validators=[Length(min=5, max=120)], render_kw={"placeholder": "사업자용 이메일"})
    corp_number = StringField("사업자 등록번호", render_kw={"placeholder": "사업자 등록번호"})
    corp_online_marketing_number = StringField("통신판매업번호", render_kw={"placeholder": "통신판매업번호"})
    corp_image = FileField("사업자 등록증", render_kw={"placeholder": "사업자 등록증"})
    corp_address = StringField("사업자 주소", render_kw={"placeholder": "사업자 주소"})
    main_phonenumber = StringField("대표 전화번호", render_kw={"placeholder": "대표 전화번호"})
    main_cellphone = StringField("사업자 휴대폰", render_kw={"placeholder": "사업자 휴대폰"})