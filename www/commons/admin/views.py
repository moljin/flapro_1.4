from flask import Blueprint, render_template, request, redirect, url_for

from configs import db
from www.commons.admin.forms import VarRatioForm, BaseAmountForm
from www.commons.models import VarRatio, BaseAmount
from www.commons.required import admin_required

NAME = 'admin_commons'
admin_common = Blueprint(NAME, __name__, url_prefix='/admin/commons')


@admin_common.route('/pay/ratio-amount/list', methods=['GET'])
@admin_required
def pay_ratio_amount_list():
    """결제 기본설정"""
    ratio_objs = VarRatio.query.all()
    amount_objs = BaseAmount.query.all()
    return render_template('commons/admin/pay_ratio_amount/list.html', ratio_objs=ratio_objs, amount_objs=amount_objs)


form = ""


@admin_common.route('/common/create', methods=['GET'])
@admin_required
def common_create():
    global form
    _type = request.args.get("_type")
    if _type == "ratio":
        form = VarRatioForm()
    elif _type == "amount":
        form = BaseAmountForm()
    return render_template('commons/admin/pay_ratio_amount/create.html', form=form, _type=_type)


@admin_common.route('/common/ratio/change/<int:_id>', methods=['GET'])
@admin_required
def ratio_change(_id):
    _form = VarRatioForm()
    ratio = VarRatio.query.filter_by(id=_id).first()
    return render_template('commons/admin/pay_ratio_amount/ratio_change.html', form=_form, target_ratio=ratio)


@admin_common.route('/common/amount/change/<int:_id>', methods=['GET'])
@admin_required
def amount_change(_id):
    _form = BaseAmountForm()
    amount = BaseAmount.query.filter_by(id=_id).first()
    return render_template('commons/admin/pay_ratio_amount/amount_change.html', form=_form, target_amount=amount)


@admin_common.route('/common/ratio/save', methods=['POST'])
@admin_required
def ratio_save():
    ratio_id = request.form.get("ratio_id")
    title = request.form.get("title")
    ratio = request.form.get("ratio")
    if ratio_id:
        target_ratio = VarRatio.query.filter_by(id=ratio_id).first()
        target_ratio.ratio = ratio
        db.session.add(target_ratio)
    else:
        new_ratio = VarRatio()
        new_ratio.title = title
        new_ratio.ratio = ratio
        db.session.add(new_ratio)
    db.session.commit()
    return redirect(url_for("admin_commons.common_list"))


@admin_common.route('/common/amount/save', methods=['POST'])
@admin_required
def amount_save():
    amount_id = request.form.get("amount_id")
    title = request.form.get("title")
    amount = request.form.get("amount")
    if amount_id:
        target_amount = BaseAmount.query.filter_by(id=amount_id).first()
        target_amount.amount = amount
        db.session.add(target_amount)
    else:
        new_amount = BaseAmount()
        new_amount.title = title
        new_amount.amount = amount
        db.session.add(new_amount)
    db.session.commit()
    return redirect(url_for("admin_commons.common_list"))



