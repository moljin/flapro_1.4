from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField


class VarRatioForm(FlaskForm):
    title = StringField("Title", render_kw={"placeholder": "타이틀"})
    ratio = DecimalField("Ratio", render_kw={"placeholder": "비율(소수점 4자리까지)"})


class BaseAmountForm(FlaskForm):
    title = StringField("Title", render_kw={"placeholder": "타이틀"})
    amount = IntegerField("Amount", render_kw={"placeholder": "금액"})