from flask_wtf import FlaskForm
from wtforms import StringField


class LottoForm(FlaskForm):
    title = StringField("title", render_kw={"placeholder": "타이틀"})
    status = StringField("status", render_kw={"placeholder": "상태"})
    latest_round_num = StringField("round_num", render_kw={"placeholder": " 회차"})
    extract_num = StringField("extract_num", render_kw={"placeholder": "추출번호"})
