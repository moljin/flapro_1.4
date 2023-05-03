from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length


class ShopForm(FlaskForm):
    title = StringField("상점 타이틀", validators=[Length(min=1, max=100)], render_kw={"placeholder": "상점 이름"})
    content = TextAreaField("간단한 소개글", validators=[Length(min=2, max=100)], render_kw={"placeholder": "간단한 소개글(최적 80자, 최대 160자 이내)"})

    cover_image_1 = FileField()
    cover_image_2 = FileField()
    cover_image_3 = FileField()
    cover_image_4 = FileField()
    cover_image_5 = FileField()
    cover_image_6 = FileField()
    symbol_image = FileField("Shop 심볼")

    available_display = BooleanField("Display", default=True)


class ProductCategoryForm(FlaskForm):
    title = StringField("상품 카테고리 이름", validators=[Length(min=1, max=200)], render_kw={"placeholder": "상품 카테고리 이름"})

    available_display = BooleanField("Display", default=True)


class ProductForm(FlaskForm):
    title = StringField("타이틀", validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "타이틀"})

    image1 = FileField()
    image2 = FileField()
    image3 = FileField()

    content = TextAreaField("내용", validators=[DataRequired()], render_kw={"placeholder": "내용"})
    meta_description = TextAreaField("메타설명", validators=[DataRequired(), Length(min=2, max=160)], render_kw={"placeholder": "메타 설명"})

    price = IntegerField("가격", validators=[DataRequired()], render_kw={"placeholder": "가격"})
    stock = IntegerField("재고", validators=[DataRequired()], render_kw={"placeholder": "재고"})
    base_dc_amount = IntegerField("기본 할인금액", default=0, render_kw={"placeholder": "기본 할인금액"})
    delivery_pay = IntegerField("배송비", default=0, render_kw={"placeholder": "배송비"})

    available_display = BooleanField("전시여부", default=True)
    available_order = BooleanField("주문가능", default=True)