from flask_wtf import FlaskForm
from wtforms import EmailField, BooleanField
from wtforms.validators import InputRequired, Length


class AuthPermitForm(FlaskForm):
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=120)], render_kw={"placeholder": "이메일"})
    is_verified = BooleanField('회원 인증')
    is_staff = BooleanField('중간관리자 인증')
    is_admin = BooleanField('관리자 인증')
