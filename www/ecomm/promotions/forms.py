from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired


class CouponCreateForm(FlaskForm):  # format='%Y-%m-%d %H:%M'
    code = StringField("쿠폰코드", validators=[DataRequired()], render_kw={"placeholder": "쿠폰코드"})
    use_from = DateField('시작일', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.now())#.strftime("%Y-%m-%d"))
    use_to = DateField('종료일', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.now())#.strftime("%Y-%m-%d"))
    amount = IntegerField("할인가격", validators=[DataRequired()], render_kw={"placeholder": "가격"})
    is_active = BooleanField("사용 가능여부", default=True)
    available_count = IntegerField("사용 가능횟수", validators=[DataRequired()], render_kw={"placeholder": "사용 가능횟수"})


class AddCouponForm(FlaskForm):
    code = StringField("쿠폰코드", render_kw={"placeholder": "쿠폰코드"})