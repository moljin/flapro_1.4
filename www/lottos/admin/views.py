from flask import Blueprint, request, render_template, redirect, url_for
from sqlalchemy import desc

from configs import db
from configs.config import ADMIN_PER_PAGE
from www.commons.required import admin_required
from www.lottos.admin.forms import LottoForm
from www.lottos.models import LottoFirstWinNum

NAME = 'admin_lottos'
admin_lotto = Blueprint(NAME, __name__, url_prefix='/admin/lotto')


@admin_lotto.route('/num/list', methods=['GET'])
@admin_required
def lotto_num_list():
    lotto_nums_query = LottoFirstWinNum.query.order_by(desc(LottoFirstWinNum.id))
    page = request.args.get('page', type=int, default=1)
    pagination = lotto_nums_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    lotto_nums = pagination.items
    print(lotto_nums)
    return render_template('lottos/admin/list.html',
                           lotto_nums=lotto_nums,
                           pagination=pagination)


@admin_lotto.route('/num/change/<int:_id>', methods=['GET'])
@admin_required
def lotto_num_change(_id):
    form = LottoForm()
    lotto_num = LottoFirstWinNum.query.filter_by(id=_id).first()
    return render_template('lottos/admin/change.html', form=form, lotto_num=lotto_num)


@admin_lotto.route('/num/create', methods=['GET'])
@admin_required
def lotto_num_create():
    form = LottoForm()
    return render_template('lottos/admin/create.html', form=form)


@admin_lotto.route('/num/save', methods=['POST'])
@admin_required
def lotto_num_save():
    num_id = request.form.get("num-id")
    title = request.form.get("title")
    status = request.form.get("status")
    latest_round_num = request.form.get("latest_round_num")
    extract_num = request.form.get("extract_num")
    if num_id:
        target_lotto_num = LottoFirstWinNum.query.filter_by(id=num_id).first()
        target_lotto_num.status = status
        db.session.add(target_lotto_num)
        db.session.commit()
    else:
        new_lotto_num = LottoFirstWinNum()
        new_lotto_num.title = title
        new_lotto_num.status = status
        new_lotto_num.latest_round_num = latest_round_num
        new_lotto_num.extract_num = extract_num
        db.session.add(new_lotto_num)
        db.session.commit()
    return redirect(url_for("admin_lottos.lotto_num_list"))



