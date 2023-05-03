from flask_wtf import FlaskForm
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired, Length, InputRequired


class OrderCreateForm(FlaskForm):
    name = StringField("이름", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "이름"})
    email = EmailField('email', validators=[InputRequired(), Length(min=5, max=120)], render_kw={"placeholder": "이메일"})
    phonenumber = StringField("휴대폰번호", validators=[DataRequired()], render_kw={"placeholder": "휴대폰번호"})

    postal_code = StringField("우편번호", validators=[DataRequired()], render_kw={"placeholder": "우편번호"})
    address = StringField("수령주소", validators=[DataRequired()], render_kw={"placeholder": "받으실 주소"})
    detail_address = StringField("상세주소", validators=[DataRequired()], render_kw={"placeholder": "상세주소"})
    extra_address = StringField("주소 참고항목", render_kw={"placeholder": "주소 참고항목"})
    order_memo = StringField("주문메모", render_kw={"placeholder": "주문메모"})