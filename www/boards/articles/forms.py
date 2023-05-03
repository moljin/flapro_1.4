from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, BooleanField
from wtforms.validators import Length


class ArticleForm(FlaskForm):
    """ArticleCategory 와 Article 동시에 적용"""
    title = StringField("제목", validators=[Length(min=4, max=45)], render_kw={"placeholder": "타이틀"})
    meta_description = TextAreaField("웹페이지 요약 메타설명", render_kw={"placeholder": "웹페이지 요약 메타설명(최적 80자, 최대 160자 이내)"})
    content = TextAreaField("내용", render_kw={"placeholder": "내용"})
    image = FileField("이미지")

    available_display = BooleanField('노출 여부', default=True)

    site_title = StringField("사이트 제목", validators=[Length(min=4, max=45)], render_kw={"placeholder": "참고사이트 제목"})
    site_url = TextAreaField("사이트 주소", render_kw={"placeholder": "참고사이트 주소"})