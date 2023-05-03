from configs import db
from www.commons.models import BaseModel

STATUS = ('old',
          'latest')


class LottoFirstWinNum(BaseModel):
    __tablename__ = 'lottos'
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), default=STATUS[1])
    latest_round_num = db.Column(db.String(100), nullable=False)
    extract_num = db.Column(db.String(100), nullable=False)