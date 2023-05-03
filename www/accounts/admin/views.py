from flask import Blueprint, flash, redirect, url_for, session, abort, render_template, request
from flask_login import current_user, logout_user
from itsdangerous import SignatureExpired
from sqlalchemy import desc
from werkzeug import security

from configs import db
from configs.config import SUPER_ADMIN_EMAIL, ADMIN_PER_PAGE
from www.accounts.admin.forms import AuthPermitForm
from www.accounts.admin.utils import admin_login, admin_user_save, admin_send_mail, is_staff_true_save, is_admin_true_save, is_admin_staff_true_save, is_admin_staff_false_save, is_admin_false_save, \
    is_staff_false_save, admin_user_other_save
from www.accounts.forms import LoginForm, AccountsForm, ProfilesForm
from www.accounts.models import User, Profile
from www.accounts.utils import user_check, existing_email_check, optimal_password_check, existing_username_check
from www.commons.required import admin_required, login_required
from www.commons.utils import flash_form_errors

NAME = 'admin_accounts'
admin_account = Blueprint(NAME, __name__, url_prefix='/admin')


@admin_account.route('/', methods=['GET'])
def index():
    try:
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).one()
    except Exception as e:
        print("/admin approach :: ", e)
        user = None
    if current_user.is_authenticated and user.is_admin:
        return render_template('includes/admin/index.html')
    elif current_user.is_authenticated and not user.is_admin:
        abort(401)
    else:
        return redirect(url_for('admin_accounts.login', user=user))


@admin_account.route('/login', methods=['GET'])
def login():
    form = LoginForm()
    if current_user.is_authenticated and current_user.is_admin:
        flash("로그인 상태입니다!")
        return redirect(url_for("admin_accounts.index"))
    return render_template('accounts/admin/login.html', form=form)


@admin_account.route('/login/post', methods=['POST'])
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        req_value = form.username.data
        req_password = form.password.data
        user = user_check(req_value)
        if user and user.is_verified and user.is_admin:
            _login = admin_login(user, req_password)
            return _login
        abort(401)
    else:
        flash_form_errors(form)
        print("flash_form_errors(form)")
        return redirect(request.referrer)


@admin_account.route('/logout', methods=['GET'])
@admin_required
def logout():
    session.pop('email', None)
    logout_user()
    return redirect(url_for('admin_accounts.login'))


@admin_account.route('/accounts/list', methods=['GET'])
@admin_required
def user_list():
    users_query = User.query.order_by(desc(User.id))  # .all()
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        users_query = users_query.filter(User.email.ilike(search) |
                                         User.username.ilike(search)).distinct()
    """######################"""
    pagination = users_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    users = pagination.items
    return render_template('accounts/admin/users/list.html',
                           users=users,
                           pagination=pagination,
                           kw=kw)


@admin_account.route('/accounts/<int:_id>/change', methods=['GET'])
@admin_required
def user_change(_id):
    form = AccountsForm()
    user_obj = User.query.filter_by(id=_id).first()
    return render_template('accounts/admin/users/change.html', form=form, target_user=user_obj)


@admin_account.route('/accounts/create', methods=['GET'])
@admin_required
def user_create():
    form = AccountsForm()
    return render_template('accounts/admin/users/create.html', form=form)


@admin_account.route('/accounts/save', methods=['POST'])
@admin_required
def user_save():
    if request.method == 'POST':
        target_user_id = request.form.get("_id")
        req_username = request.form.get("username")
        req_email = request.form.get("email")
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        auth_token = request.form.get("auth_token")
        password_token = request.form.get("password_token")
        admin_token = request.form.get("admin_token")
        is_verified = request.form.get("is_verified")
        is_staff = request.form.get("is_staff")
        is_vendor = request.form.get("is_vendor")
        is_admin = request.form.get("is_admin")
        print("is_verified is_verified", is_verified)
        print("is_staff is_staff", is_staff)
        print("is_admin is_admin", is_admin)
        if target_user_id:
            target_user = User.query.get_or_404(target_user_id)
            if is_admin is None:  # 관리자 자신이 관리자 권한 해제 요청을 진행하는 경우
                if target_user.is_admin and current_user == target_user:
                    flash("관리자님의 관리자 권한 해제는 SUPER ADMIN만 가능합니다..")
                    return redirect(url_for("admin_accounts.auth_permit_request", email=current_user.email, is_admin="관리자 자신"))
                    # 관리자 자신은 is_admin 이외의 것은 수정할 수 있지만,
                    # is_admin 해제는 최고 관리자에게 메일 요청으로 할 수 있도록 한다.
            if target_user.email != req_email:
                if existing_email_check(req_email) == "Existing":
                    flash("가입된 이메일이 존재합니다.")
                    return redirect(request.referrer)
            target_user.email = req_email

            if password or repassword:
                if optimal_password_check(password) == "No Password":
                    flash('비밀번호(알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상)가 입력되지 않았습니다.')
                    return redirect(request.referrer)
                if password and not repassword:
                    flash("비밀번호 확인 입력란을 채워주세요!")
                    return redirect(request.referrer)
                if (password == repassword) and (optimal_password_check(password) == "Optimal"):
                    hashed_password = security.generate_password_hash(password)
                    target_user.password = hashed_password

                    admin_user_save(target_user, auth_token, password_token, admin_token, is_verified, is_staff, is_vendor, is_admin)
                    return redirect(url_for("admin_accounts.change", _id=target_user_id))
                if (password == repassword) and (optimal_password_check(password) == "Not Optimal"):
                    flash('비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.')
                    return redirect(request.referrer)
                else:
                    flash("비밀번호가 일치하지 않아요")
                    return redirect(request.referrer)
            else:
                admin_user_save(target_user, auth_token, password_token, admin_token, is_verified, is_staff, is_vendor, is_admin)
        else:
            if existing_username_check(req_username) == "Existing":
                flash("가입된 아이디가 존재합니다.")
                return redirect(request.referrer)
            if existing_email_check(req_email) == "Existing":
                flash("가입된 이메일이 존재합니다.")
                return redirect(request.referrer)
            if (password == repassword) and (optimal_password_check(password) == "Optimal"):
                hashed_password = security.generate_password_hash(password)
                new_user = User(email=req_email, password=hashed_password)
                new_user.username = req_username

                admin_user_save(new_user, auth_token, password_token, admin_token, is_verified, is_staff, is_vendor, is_admin)
                admin_user_other_save(new_user)
                return redirect(url_for("admin_accounts.user_list"))
            if (password == repassword) and (optimal_password_check(password) == "Not Optimal"):
                flash('비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.')
                return redirect(request.referrer)
            else:
                flash("비밀번호가 일치하지 않아요")
                return redirect(request.referrer)
        return redirect(url_for("admin_accounts.user_change", _id=target_user_id))
    else:
        abort(404)


@admin_account.route('/accounts/change/save', methods=['POST'])
@admin_required
def user_change_save():
    if request.method == 'POST':
        target_user_id = request.form.get("_id")
        req_email = request.form.get("email")
        is_verified = request.form.get("is_verified")
        is_staff = request.form.get("is_staff")
        is_vendor = request.form.get("is_vendor")
        is_admin = request.form.get("is_admin")
        if target_user_id:
            target_user = User.query.get_or_404(target_user_id)
            if is_admin is None:  # 관리자 자신이 관리자 권한 해제 요청을 진행하는 경우
                if target_user.is_admin and current_user == target_user:
                    flash("관리자님의 관리자 권한 해제는 SUPER ADMIN만 가능합니다..")
                    return redirect(url_for("admin_accounts.auth_permit_request", email=current_user.email, is_admin="관리자 자신"))
                    # 관리자 자신은 is_admin 이외의 것은 수정할 수 있지만,
                    # is_admin 해제는 최고 관리자에게 메일 요청으로 할 수 있도록 한다.
            if target_user.email != req_email:
                if existing_email_check(req_email) == "Existing":
                    flash("가입된 이메일이 존재합니다.")
                    return redirect(request.referrer)
            target_user.email = req_email
            admin_user_save(target_user, auth_token=None, password_token=None, admin_token=None, is_verified=is_verified, is_staff=is_staff, is_vendor=is_vendor, is_admin=is_admin)
            flash("변경내용이 저장되었습니다.")
        return redirect(url_for("admin_accounts.user_change", _id=target_user_id))
    else:
        abort(404)


@admin_account.route('/profiles/list', methods=['GET'])
@admin_required
def profile_list():
    profile_query = Profile.query.order_by(desc(Profile.id))#.all()
    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw)
        profile_query = profile_query.join(User).filter(Profile.nickname.ilike(search) |
                                                        User.email.ilike(search) |
                                                        User.username.ilike(search)).distinct()
    """######################"""
    pagination = profile_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    profiles = pagination.items
    return render_template('accounts/admin/profiles/list.html',
                           profiles=profiles,
                           pagination=pagination,
                           kw=kw)


@admin_account.route('/profiles/<int:_id>/change', methods=['GET'])
@admin_required
def profile_change(_id):
    form = ProfilesForm()
    user_objs = User.query.all()
    profile_obj = Profile.query.filter_by(id=_id).first()
    user_obj = User.query.filter_by(id=profile_obj.user_id).first()
    levels = ['일반이용자', '심사중 판매사업자', '판매사업자']
    # cover_img_obj = db.session.query(ProfileCoverImage).filter_by(profile_id=profile_obj.id).first()
    return render_template('accounts/admin/profiles/change.html',
                           form=form,
                           users=user_objs,
                           target_user=user_obj,
                           target_profile=profile_obj,
                           levels=levels)


@admin_account.route('/profiles/create', methods=['GET'])
@admin_required
def profile_create():
    form = ProfilesForm()
    user_objs = User.query.all()
    levels = ['일반이용자', '심사중 판매사업자', '판매사업자']
    return render_template('accounts/admin/profiles/create.html', form=form, users=user_objs, levels=levels)


# ######################## admin 신청 ########################


@admin_account.route('auth/permission/request/<email>', methods=['GET', 'POST'])
@login_required
def auth_permit_request(email):
    form = AuthPermitForm()
    user_obj = User.query.filter_by(email=email).first()
    print(request.form.get("email"))
    if request.method == 'POST' and email == request.form.get("email"):
        is_staff = request.form.get("is_staff")
        is_admin = request.form.get("is_admin")
        admin = request.form.get("admin")  # 관리자가 본인 관리자 권한 해제 요청시
        from configs import safe_time_serializer
        admin_token = safe_time_serializer.dumps(email, salt='email-confirm')
        user_obj.admin_token = admin_token
        db.session.add(user_obj)
        db.session.commit()

        if not admin:  # 비관리자 회원이 관리자 혹은 스태프 권한 요청시
            add_if = "auth_permission"
        else:  # 관리자가 본인 관리자 권한 해제 요청시
            add_if = "not_admin"

        subject = "β-0.4 관리자 인증용 메일"
        authorizer_email = SUPER_ADMIN_EMAIL
        req_email = email  # 관리자로 승인을 요청한 회원의 메일이다.
        msg_txt = 'includes/send_mails/mail.txt'
        msg_html = 'accounts/admin/send_mails/auth_permission_mail.html'
        """auth_permit 을 신청한 회원 이메일을 send_mail 에 딸려 보내야 하는데...."""
        # send_mail_for_any(subject, authorizer_email, admin_token, msg_txt, msg_html, add_if)
        if is_staff == "y":
            is_staff = "y"
        else:
            is_staff = "n"

        if is_admin == "y":
            is_admin = "y"
        else:
            is_admin = "n"
        admin_send_mail(subject, authorizer_email, admin_token, msg_txt, msg_html, add_if, req_email, is_staff, is_admin)
        flash('이메일을 전송하였습니다. 메일을 확인하세요')
        return redirect(url_for('accounts.token_send', user=user_obj, email=email, add_if=add_if))  # 이렇게 token_send로 이메일을 넘겨 줄수도 있다.
    else:
        if user_obj and current_user.is_authenticated:
            if (email == current_user.email) and current_user.is_admin:
                return render_template('accounts/admin/auth.html', target_user=user_obj, form=form, admin="관리자 자신")
            if (email == current_user.email) and not current_user.is_admin:
                return render_template('accounts/admin/auth.html', target_user=user_obj, form=form, admin="not admin")
            else:
                abort(401)


@admin_account.route('auth/confirm/<add_if>/<token>')
@admin_required
def auth_confirm_email(add_if, token):
    """SuperAdmin 의 이메일에 첨부된 링크된 주소이고, 그 링크를 클릭하면 여기로 이동"""
    req_email = request.args.get("req_email")
    print("auth_confirm(add_if, token): req_email", req_email)
    is_staff = request.args.get("is_staff")
    is_admin = request.args.get("is_admin")
    return render_template('accounts/admin/auth_confirm.html',
                           add_if=add_if,
                           token=token,
                           req_email=req_email,
                           is_staff=is_staff,
                           is_admin=is_admin)


@admin_account.route('auth/confirm/email/<add_if>/<token>')
@admin_required
def auth_confirm(add_if, token):
    """SuperAdmin 이 def auth_confirm(add_if, token) 페이지에서 승인을 클릭하면 여기서 승인완료가 이루어진다."""
    from configs import safe_time_serializer
    email = safe_time_serializer.loads(token, salt='email-confirm', max_age=86400)  # 24시간 cf. 60 == 60초 즉, 1분
    try:
        user_obj = User.query.filter_by(email=email).first()
        req_email = request.args.get("req_email")
        print("req_email", req_email)
        is_staff = request.args.get("is_staff")
        is_admin = request.args.get("is_admin")
        if (is_admin == "y") and (is_staff == "y"):
            if user_obj and user_obj.is_admin and user_obj.is_staff and (add_if == "auth_permission"):
                flash('관리자와 스태프 권한 인증이 이미 되어 있어요!')
            if user_obj and user_obj.is_admin and not user_obj.is_staff and (add_if == "auth_permission"):
                is_staff_true_save(user_obj)
                flash('관리자 권한 인증은 이미 되어 있었고, 스태프 권한 인증은 완료되었습니다.')
            if user_obj and not user_obj.is_admin and user_obj.is_staff and (add_if == "auth_permission"):
                is_admin_true_save(user_obj)
                flash('스태프 권한 인증은 이미 되어 있었고, 관리자 권한 인증은 완료되었습니다.')
            if user_obj and not user_obj.is_admin and not user_obj.is_staff and (add_if == "auth_permission"):
                is_admin_staff_true_save(user_obj)
                flash('관리자와 스태프 권한 인증이 완료되었습니다.')
            return redirect(url_for("admin_accounts.user_change", _id=user_obj.id))
        if (is_admin == "n") and (is_staff == "n"):
            if user_obj and user_obj.is_admin and user_obj.is_staff and ((add_if == "auth_permission") or (add_if == "not_admin")):
                is_admin_staff_false_save(user_obj)
            if user_obj and user_obj.is_admin and not user_obj.is_staff and ((add_if == "auth_permission") or (add_if == "not_admin")):
                is_admin_false_save(user_obj)
            if user_obj and not user_obj.is_admin and user_obj.is_staff and ((add_if == "auth_permission") or (add_if == "not_admin")):
                is_staff_false_save(user_obj)
            flash(f'권한해제가 완료되어, {user_obj.email}님은 관리자와 스태프 권한 모두 없습니다.')
            return redirect(url_for("admin_accounts.user_change", _id=user_obj.id))
        if (is_admin == "y" or "n") or (is_staff == "y" or "n"):
            if (is_admin == "y") and (is_staff == "n"):
                if user_obj and user_obj.is_admin and (add_if == "auth_permission"):
                    flash('관리자 권한 인증은 이미 되어 있어요!')
                if user_obj and not user_obj.is_admin and (add_if == "auth_permission"):
                    is_admin_true_save(user_obj)
                    flash('관리자 권한 인증이 완료되었습니다.')
                if user_obj and user_obj.is_staff and (add_if == "auth_permission"):
                    is_staff_false_save(user_obj)
                return redirect(url_for("admin_accounts.user_change", _id=user_obj.id))
            if (is_admin == "n") and (is_staff == "y"):
                if user_obj and user_obj.is_staff and ((add_if == "auth_permission") or (add_if == "not_admin")):
                    flash('스태프 권한 인증이 이미 되어 있어요!')
                if user_obj and not user_obj.is_staff and ((add_if == "auth_permission") or (add_if == "not_admin")):
                    is_staff_true_save(user_obj)
                    flash('스태프 권한 인증이 완료되었습니다.')
                if user_obj and user_obj.is_admin and ((add_if == "auth_permission") or (add_if == "not_admin")):
                    is_admin_false_save(user_obj)
                # 스태프 인증되면 리다이렉트 할 페이지 == 스태프들만 보는 index page
                return redirect(url_for("admin_accounts.user_change", _id=user_obj.id))
            return redirect(url_for('commons.index'))  # 스태프도 어드민도 아닌 경우 리디렉트 page
        elif not (is_admin == "y" or "n") or not (is_staff == "y" or "n"):
            flash('가입한 내용이 없거나 . . . 문제가 발생했습니다.')
            return redirect(url_for('commons.index'))
    except SignatureExpired:
        flash('토큰이 죽었어요...!')
        # confirm_expired_msg = '토큰이 죽었어요...!'
        # return confirm_expired_msg
    # 가입도 안된 토큰으로 시도할 때 flash를 안고 돌아간다.... #'<h1>토큰이 살아 있어요....</h1>'  # True 로 바꿔주고, 링크를 클릭하면 인증완료된다.
    return redirect(url_for('admin_accounts.auth_permit_request', email=email))