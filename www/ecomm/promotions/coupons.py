import datetime

from flask import Blueprint, redirect, url_for, render_template, request, make_response, jsonify, flash
from flask_login import current_user
from sqlalchemy import desc

from configs import db
from www.accounts.models import User, Profile
from www.commons.models import VarRatio, BaseAmount
from www.commons.required import login_required
from www.commons.utils import existing_req_data_check
from www.ecomm.carts.models import Cart
from www.ecomm.products.required import vendor_required
from www.ecomm.promotions.forms import CouponCreateForm
from www.ecomm.promotions.models import Coupon, Point, PointLog, UsedCoupon
from www.ecomm.promotions.required import coupon_ownership_required
from www.ecomm.promotions.utils import point_log_update, coupon_save

NAME = 'coupons'
coupons = Blueprint(NAME, __name__, url_prefix='/promotions/coupons')


@coupons.route('/create', methods=['GET'])
@vendor_required
def create():
    form = CouponCreateForm()
    return render_template('ecomm/promotions/coupons/create.html', form=form)


@coupons.route('/code/check/ajax', methods=['POST'])
@vendor_required
def coupon_code_check_ajax():
    user_id = request.form.get("user_id")  # 이용자단 등록/수정, 어드민단의 change
    _user_email = request.form.get("user_email")  # 어드민단의 create

    coupon_id = request.form.get("coupon_id")
    req_code = request.form.get("code")

    target_user = User.query.filter_by(id=user_id).first()
    target_profile = db.session.query(Profile).filter_by(user_id=user_id).first()
    target_coupon = Coupon.query.filter_by(id=coupon_id).first()
    existing_code_coupon = Coupon.query.filter_by(code=req_code).first()
    if coupon_id == "none":
        if user_id:   # 이용자단의 create
            if current_user == target_user:
                if target_profile and (target_profile.level == "판매사업자"):
                    _type = "쿠폰코드"
                    flash_message = existing_req_data_check(_type, req_code, existing_code_coupon, None, None)
                    return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
        elif _user_email:  # 어드민단의 create
            _target_user = User.query.filter_by(email=_user_email).first()
            if _target_user:
                if current_user.is_admin:
                    _type = "쿠폰코드"
                    flash_message = existing_req_data_check(_type, req_code, existing_code_coupon, None, None)
                    return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
            else:
                flash_message = {"flash_message": "유효하지 않은 요청(Error 400)", }
                return make_response(jsonify(flash_message))
        else:  # 어드민단의 create 시에 회원 선택하지 않은 경우
            flash_message = {"flash_message": "쿠폰 등록을 위한 회원정보가 없네요!(Error 404)", }
            return make_response(jsonify(flash_message))
    else:
        if target_coupon:
            if target_user:
                if current_user == target_user:
                    if target_profile and (target_profile.level == "판매사업자") and (target_user.id == target_coupon.user_id):
                        _type = "쿠폰코드"
                        flash_message = existing_req_data_check(_type, req_code, existing_code_coupon, target_coupon, target_coupon.code)
                        return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
            else:
                flash_message = {"flash_message": "쿠폰 등록을 위한 회원정보가 없네요!(Error 404)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "해당 쿠폰이 없는 유효하지 않은 요청(Error 400)", }
            return make_response(jsonify(flash_message))


@coupons.route('/save', methods=['POST'])
@vendor_required
def save():
    form = CouponCreateForm()

    profile_id = request.form.get("profile_id")
    coupon_id = request.form.get("coupon_id")

    req_code = form.code.data
    use_from = form.use_from.data
    use_to = form.use_to.data
    amount = form.amount.data
    available_count = form.available_count.data
    is_active = request.form.get("is_active")

    existing_code_coupon = Coupon.query.filter_by(code=req_code).first()

    if coupon_id == "none":
        if existing_code_coupon:
            flash("동일한 쿠폰코드가 존재합니다.")
            return redirect(request.referrer)

        if form.validate_on_submit():
            new_coupon = Coupon(user_id=current_user.id)
            coupon_save(new_coupon, req_code, use_from, use_to, amount, is_active, available_count)
            return redirect(url_for('coupons._list', _id=current_user.id))
    else:
        own_coupon = Coupon.query.get_or_404(coupon_id)
        if existing_code_coupon:
            if (existing_code_coupon.code == req_code) and (existing_code_coupon.id != int(coupon_id)):
                flash("동일한 쿠폰코드가 존재합니다.")
                return redirect(request.referrer)
            if (existing_code_coupon.code == req_code) and (existing_code_coupon.id == int(coupon_id)):
                coupon_save(own_coupon, req_code, use_from, use_to, amount, is_active, available_count)
                return redirect(url_for('coupons._list', _id=current_user.id))
        else:
            if form.validate_on_submit():
                coupon_save(own_coupon, req_code, use_from, use_to, amount, is_active, available_count)
                return redirect(url_for('coupons._list', _id=current_user.id))


@coupons.route('/detail/<int:_id>', methods=['GET'])
@coupon_ownership_required
def change(_id):
    form = CouponCreateForm()
    coupon_obj = db.session.query(Coupon).filter_by(id=_id).first()
    owner_obj = User.query.get_or_404(coupon_obj.user_id)
    return render_template('ecomm/promotions/coupons/change.html', owner=owner_obj, coupon=coupon_obj, form=form)


@coupons.route('/list/<int:_id>', methods=['GET'])
@vendor_required
def _list(_id):
    user_obj = User.query.get_or_404(_id)
    print(user_obj)
    profile_obj = Profile.query.filter_by(user_id=_id).first()
    page = request.args.get('page', type=int, default=1)
    coupon_objs = Coupon.query.filter_by(user_id=_id).order_by(desc(Coupon.created_at))  # id))  # .all()
    # try:
    #     coupons = Coupon.query.filter_by(user_id=pk_id).order_by(desc(Coupon.created_at))#id))  # .all()
    # except:
    #     coupons = None

    """
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        sub_query = db_session.query(Answer.question_id,
                                     Answer.content,
                                     Profile.nickname).join(Profile, Answer.user_id == Profile.user_id).subquery()
        print('00000000000000000000000==sub_query', sub_query)
        questions = questions.join(User, Profile).outerjoin(sub_query, sub_query.c.question_id == Question.id)\
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    Profile.nickname.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.nickname.ilike(search)).distinct()  # 답변작성자
        """
    pagination = coupon_objs.paginate(page=page, per_page=10, error_out=False)
    coupon_objs = pagination.items
    print(coupon_objs)
    return render_template('ecomm/promotions/coupons/list.html',
                           target_user=user_obj,
                           coupons=coupon_objs, pagination=pagination)  # , kw=kw)


message = ''
new_used_coupon = ''
new_used_coupon_amount = ''
will_dct_amount = ''
new_prep_point = ''


@coupons.route('/add/ajax', methods=["POST"])
@login_required
def add_coupon_ajax():
    now = datetime.datetime.now()
    global message, will_dct_amount, new_used_coupon_amount, new_prep_point, new_used_coupon
    cart_id = request.form.get('cart_id')
    cart = Cart.query.get_or_404(cart_id)
    old_coupon_total = cart.coupon_discount_total()
    old_get_total = cart.get_total_price()

    point_ratio = VarRatio.query.get(2).ratio
    point_obj = Point.query.filter_by(user_id=current_user.id).first()
    point_log = PointLog.query.filter_by(cart_id=cart.id).first()  # add_to_cart_ajax에서 PointLog 만들었다.

    code = request.form.get('code')
    available_coupon = Coupon.query.filter_by(code=code, is_active=True).filter(Coupon.use_from <= now,
                                                                                Coupon.use_to >= now,
                                                                                Coupon.available_count > 0).first()
    if available_coupon:
        old_used_coupon = UsedCoupon.query.filter_by(coupon_id=available_coupon.id,
                                                     code=code,
                                                     owner_id=available_coupon.user.id,
                                                     consumer_id=current_user.id,
                                                     is_used=True,
                                                     is_cancel=False).first()
        if old_used_coupon:
            new_used_coupon_amount = 0
            if point_log.used_point:  # cart.coupon_discount_total()는 이미 사용된 쿠폰 총합
                will_dct_amount = old_coupon_total + new_used_coupon_amount + point_log.used_point
            else:
                will_dct_amount = old_coupon_total
            message = '이미 사용된 쿠폰이에요!!'
        else:
            try:
                base_pay_amount = BaseAmount.query.get_or_404(1).amount  # 기본 최소 결제금액(id=1)
            except Exception as e:
                print("base_minimal_pay_amount Error", e)
                base_pay_amount = 500  # 강제로 기본 최소 결제금액을 500원으로 맞춘것이다.
            if cart.get_total_price() >= available_coupon.amount + base_pay_amount:
                new_used_coupon = UsedCoupon(cart_id=cart.id,
                                             coupon_id=available_coupon.id,
                                             owner_id=available_coupon.user.id,
                                             consumer_id=current_user.id,
                                             )
                new_used_coupon.code = code
                new_used_coupon.amount = available_coupon.amount
                db.session.add(new_used_coupon)
                db.session.commit()

                available_coupon.available_count -= 1
                available_coupon.used_count += 1
                current_db_sessions = db.session.object_session(available_coupon)
                current_db_sessions.add(available_coupon)
                db.session.commit()

                new_used_coupon_amount = new_used_coupon.amount
                if point_log.used_point:  # cart.coupon_discount_total()는 이미 사용된 쿠폰 총합
                    will_dct_amount = old_coupon_total + new_used_coupon_amount + point_log.used_point

                    new_prep_point = round(float(cart.subtotal_price() - will_dct_amount) * float(point_ratio))
                    point_log_update(cart, point_obj, point_log, point_log.used_point, new_prep_point)
                else:
                    will_dct_amount = old_coupon_total + new_used_coupon_amount

                    new_prep_point = round(float(cart.subtotal_price() - will_dct_amount) * float(point_ratio))
                    point_log_update(cart, point_obj, point_log, point_log.used_point, new_prep_point)
                message = '쿠폰이 적용 되었습니다.'

                new_coupon_total = old_coupon_total + new_used_coupon_amount
                new_get_total = cart.get_total_price()

                sell_charge_ratio = VarRatio.query.get_or_404(1).ratio
                new_sell_charge = round(float(new_get_total) * float(sell_charge_ratio))
                # cart_point_log_create(cart, point_obj) ### 이것을 여기에 넣으면 """원복"""되버린다.
                context = {'cart_id': cart.id,
                           'flash_message': message,
                           'used_coupon_code': new_used_coupon.code,
                           'used_coupon_id': new_used_coupon.id,
                           'used_coupon_use_from': new_used_coupon.coupon.use_from.strftime('%y.%m.%d'),
                           'used_coupon_use_to': new_used_coupon.coupon.use_to.strftime('%y.%m.%d'),
                           'used_coupon_amount': new_used_coupon_amount,
                           'new_coupon_total': new_coupon_total,
                           'dct_amount': will_dct_amount,  # 총 할인금액
                           'prep_point': new_prep_point,
                           'new_remained_point': point_log.new_remained_point,
                           'cart_new_remained_point': point_log.new_remained_point,
                           'sell_charge': new_sell_charge,
                           'get_total_price': new_get_total,
                           "get_total_delivery_pay": cart.get_total_delivery_pay()
                           }
                return make_response(jsonify(context))
            elif cart.get_total_price() < available_coupon.amount + base_pay_amount:
                message = '쿠폰 금액이 너무 많아요!! 총 결제금액이 최소 500원 이상은 되어야 해요!!'
            else:
                message = '문제가 발생하여, 쿠폰이 적용되지 않습니다.'
    else:
        message = '유효한 쿠폰을 입력해주세요. . .'
    context = {'flash_message': message}
    return make_response(jsonify(context))


@coupons.route('/cancel/ajax', methods=["POST"])
@login_required
def cancel_coupon_ajax():
    """used_coupon 의 _id를 사용하면 굳이 code, cart_id는 필요없다."""
    _id = request.form.get('_id')

    cart_id = request.form.get('cart_id')
    cart = Cart.query.get_or_404(cart_id)

    point_ratio = VarRatio.query.get(2).ratio
    point_obj = Point.query.filter_by(user_id=current_user.id).first()
    point_log = PointLog.query.filter_by(cart_id=cart.id).first()

    used_coupon = UsedCoupon.query.filter_by(id=_id).first()
    if used_coupon:
        coupon_id = used_coupon.coupon_id

        current_db_sessions = db.session.object_session(used_coupon)
        current_db_sessions.delete(used_coupon)
        db.session.commit()

        _will_dct_amount = cart.discount_total_amount()
        _new_prep_point = round(float(cart.subtotal_price() - _will_dct_amount) * float(point_ratio))
        point_log_update(cart, point_obj, point_log, point_log.used_point, _new_prep_point)

        coupon_obj = Coupon.query.filter_by(id=coupon_id).first()
        coupon_obj.available_count += 1
        current_db_sessions = db.session.object_session(coupon_obj)
        current_db_sessions.add(coupon_obj)
        db.session.commit()
        """
        if point_log.used_point:  # cart.coupon_discount_total()는 이미 사용된 쿠폰 총합
            # will_dct_amount = old_coupon_total + new_used_coupon_amount + point_log.used_point
            will_dct_amount = cart.discount_total_amount()
            new_prep_point = round(float(cart.subtotal_price() - will_dct_amount) * float(point_ratio))
            point_log_update(cart, point_obj, point_log, point_log.used_point, new_prep_point)
        else:
            # will_dct_amount = old_coupon_total + new_used_coupon_amount
            will_dct_amount = cart.discount_total_amount()
            new_prep_point = round(float(cart.subtotal_price() - will_dct_amount) * float(point_ratio))
            point_log_update(cart, point_obj, point_log, point_log.used_point, new_prep_point)
        """

        context = {
            'flash_message': "쿠폰적용이 취소되었습니다.",
            'prep_point': point_log.prep_point,
            'new_remained_point': point_log.new_remained_point,
            'get_total_price': cart.get_total_price(),
            "get_total_delivery_pay": cart.get_total_delivery_pay()
        }
        return make_response(jsonify(context))
    else:
        context = {'unnecessary_ajax': "",}
        return make_response(jsonify(context))
