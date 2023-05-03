import re

from flask import Blueprint, session, redirect, url_for, g, render_template, request, make_response, jsonify, flash
from flask_login import current_user, login_user, logout_user
from itsdangerous import SignatureExpired
from sqlalchemy import desc
from werkzeug import security

from configs import db
from configs.config import SUPER_ADMIN_EMAIL
from www.accounts.admin.utils import admin_login
from www.accounts.forms import EmailForm, AccountsForm, LoginForm, PasswordUpdateForm, UsernameForm, ProfilesForm
from www.accounts.models import User, Profile, PROFILE_LEVELS
from www.accounts.required import account_ownership_required, profile_ownership_required
from www.accounts.utils import existing_email_check, token_create_send_mail, existing_username_check, optimal_password_check, user_check, profile_delete, vendor_save, email_match_check, \
    profile_cover_img_save, profile_profile_img_save, profile_corp_img_save, accounts_related_obj_delete
from www.boards.articles.models import ArticleCategory, Article
from www.commons.required import login_required
from www.commons.utils import random_word, flash_form_errors, any_send_mail, img_delete, existing_req_data_check, error_401_json_data, error_400_json_data
from www.ecomm.products.models import Shop, Product

NAME = 'accounts'
account = Blueprint(NAME, __name__, url_prefix='/accounts')

PROFILE_PER_PAGE = 5


@account.before_app_request
def before_app_request():
    g.user = None
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            g.user = user
        else:
            session.pop('username', None)


@account.route('/', methods=['GET'])
def index():
    """
    /accounts 로 진입하면 로그인 페이지로 보낸다.
    """
    try:
        user_id = current_user.id
        profile = Profile.query.filter_by(user_id=user_id).one()
    except Exception as e:
        print("profile = None Exception Error:: ", e)
        profile = None
    return redirect(url_for(f'{NAME}.login', profile=profile))


@account.route('/verification/token/send/<email>', methods=['GET'])
def token_send(email):
    user_obj = User.query.filter_by(email=email).first()
    add_if = request.args.get("add_if")
    return render_template("accounts/users/etc/token_send.html", user=user_obj, email=email, add_if=add_if)


@account.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("로그인 상태입니다!")
        return redirect(url_for("commons.index"))
    email_form = EmailForm()
    accounts_form = AccountsForm()
    return render_template("accounts/users/register.html", email_form=email_form, accounts_form=accounts_form)


@account.route('/token/create/ajax', methods=['POST'])
def token_create_ajax():
    """token_create_send_mail(random, email, req_add_if)을 이용해 token 을 만들고,
     session 에 담은 후에
     (session['email'], session['original_token']) 이메일를 보낸다.
    """
    email = request.form.get("email")
    req_add_if = request.form.get("add_if")
    if email:
        email_match = email_match_check(email)
        if email_match == 'email_match':
            random = random_word(15)
            if req_add_if == "register":
                if existing_email_check(email) == "Existing":
                    data = {"flash_message": "가입된 이메일이 존재합니다."}
                    return make_response(jsonify(data))
                else:
                    token_create_send_mail(random, email, req_add_if)
                    data = {"flash_message": "인증번호를 메일로 발송하였습니다."}
                    return make_response(jsonify(data))
            elif req_add_if == "forget_password":
                if existing_email_check(email) != "Existing":
                    data = {"flash_message": "등록된 이메일이 없어요!"}
                    return make_response(jsonify(data))
                else:
                    token_create_send_mail(random, email, req_add_if)
                    data = {"flash_message": "인증번호를 메일로 발송하였습니다."}
                    return make_response(jsonify(data))
            elif req_add_if == "email":
                if existing_email_check(email) != "Existing":
                    token_create_send_mail(random, email, req_add_if)
                    data = {"flash_message": "인증번호를 메일로 발송하였습니다."}
                    return make_response(jsonify(data))
                else:
                    user = User.query.filter_by(email=email).first()
                    if user == current_user:
                        data = {"flash_message": "현재 등록된 이메일과 동일하네요!"}
                        return make_response(jsonify(data))
                    data = {"flash_message": "등록된 이메일이 있어요!"}
                    return make_response(jsonify(data))
        else:
            data = {"flash_message": "입력내용은 이메일 형식이 아니에요!"}
            return make_response(jsonify(data))
    else:
        data = {"flash_message": "이메일을 입력해주세요!"}
        return make_response(jsonify(data))


@account.route('/token/confirm/ajax', methods=['POST'])
def token_confirm_ajax():
    req_token = request.form.get("token")
    if req_token:
        from configs import safe_time_serializer
        random_email = safe_time_serializer.loads(session['original_token'], salt='email-confirm', max_age=43200)
        email = random_email.split('?')[1]  # random 부분을 제거

        if "_user_id" in session:
            print("session['_user_id']", session['_user_id'])
        if "email" in session:
            print("session['email']", session['email'])
        if "username" in session:
            print("session['username']", session['username'])
        if "original_token" in session:
            print("original_token", session['original_token'])
        if "auth_token" in session:
            print("original_token", session['auth_token'])

        if 'auth_token' in session:
            auth_token = session['auth_token']
            if req_token == auth_token:
                try:
                    if email == session['email']:
                        data = {"_success": "success"}
                        return make_response(jsonify(data))
                    else:  # 이런경우는 실제 없겠지만...
                        data = {"flash_message": "이메일이 일치하지 않아요! 다시 시도해 주세요!"}
                        return make_response(jsonify(data))
                except SignatureExpired:
                    data = {"flash_message": '인증번호 유효시간이 만료되었어요! 다시 시도해 주세요!'}
                    return make_response(jsonify(data))
            else:
                data = {"flash_message": "인증번호가 다르네요. . ."}
                return make_response(jsonify(data))
        elif 'password_token' in session:
            password_token = session['password_token']
            if req_token == password_token:
                try:
                    if email == session['email']:
                        data = {"_success": "success"}
                        return make_response(jsonify(data))
                    else:  # 이런경우는 실제 없겠지만...
                        data = {"flash_message": "이메일이 일치하지 않아요! 다시 시도해 주세요!"}
                        return make_response(jsonify(data))
                except SignatureExpired:
                    data = {"flash_message": '인증번호 유효시간이 만료되었어요! 다시 시도해 주세요!'}
                    return make_response(jsonify(data))
            else:
                data = {"flash_message": "인증번호가 다르네요. . ."}
                return make_response(jsonify(data))
        else:
            data = {"flash_message": "인증번호 받기를 진행해주세요!"}
            return make_response(jsonify(data))
    else:
        data = {"flash_message": "인증번호 입력이 필요해요!"}
        return make_response(jsonify(data))


@account.route('/register/save/ajax', methods=['POST'])
def register_save_ajax():
    is_use = request.form.get("is_use")
    is_info = request.form.get("is_info")
    is_email = request.form.get("is_email")
    is_bank = request.form.get("is_bank")
    is_marketing = request.form.get("is_marketing")
    is_third = request.form.get("is_third")

    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    repassword = request.form.get("repassword")

    regex = re.compile("^[a-zA-Z0-9]*$")
    pattern_match = re.search(regex, str(username))

    if not pattern_match:
        data = {"flash_message": "아이디는 영문, 숫자로만 작성해주세요! "}
        return make_response(jsonify(data))
    if existing_username_check(username) == "Existing":
        data = {"flash_message": "가입된 아이디가 존재합니다."}
        return make_response(jsonify(data))
    if password != repassword:
        data = {"flash_message": "비밀번호가 일치하지 않아요!"}
        return make_response(jsonify(data))
    if optimal_password_check(password) == "Not Optimal":
        data = {"flash_message": '비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.'}
        return make_response(jsonify(data))
    hashed_password = security.generate_password_hash(password)
    new_user = User(
        email=email,
        password=hashed_password
    )
    new_user.username = username
    new_user.auth_token = session['original_token']
    new_user.is_verified = True

    if is_use is not None:
        new_user.is_use = True
    else:
        new_user.is_use = False

    if is_info is not None:
        new_user.is_info = True
    else:
        new_user.is_info = False

    if is_email is not None:
        new_user.is_email = True
    else:
        new_user.is_email = False

    if is_bank is not None:
        new_user.is_bank = True
    else:
        new_user.is_bank = False

    if is_marketing is not None:
        new_user.is_marketing = True
    else:
        new_user.is_marketing = False

    if is_third is not None:
        new_user.is_third = True
    else:
        new_user.is_third = False

    db.session.add(new_user)
    db.session.commit()

    session.pop('auth_token', None)
    session.pop('original_token', None)
    session.pop('email', None)
    data = {"_success": "success",
            "res_msg": "환영합니다. 회원가입이 완료되었어요!",
            "redirect_url": url_for("accounts.login")}
    return make_response(jsonify(data))


@account.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        flash("로그인 상태입니다!")
        return redirect(url_for("commons.index"))
    res_msg = request.args.get("res_msg")
    if res_msg:
        flash(res_msg)
    form = LoginForm()
    return render_template('accounts/users/login.html', form=form)


@account.route('/login/post', methods=['POST'])
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        req_value = form.username.data
        req_password = form.password.data
        user = user_check(req_value)
        """user_check(req_value)는 입력받은 username 이 
                email 인지의 여부를 확인하여 user_obj 를 리턴해준다."""
        if not user:
            flash('등록되어 있지 않아요!')
            return redirect(url_for('accounts.register'))
        else:
            if user.is_verified and user.is_admin:
                _login = admin_login(user, req_password)
                return _login
            elif user.is_verified and not user.is_admin:
                profile = Profile.query.filter_by(user_id=user.id).first()
                if security.check_password_hash(user.password, form.password.data):
                    """만일에라도, 회원정보 변경과정에 남아있던 세션이 있으면 모두 지우고...로그인
                    (session.clear()로 하면 session['previous_url']도 지워져버린다.)"""
                    if "_user_id" in session:
                        session.pop('_user_id', None)
                    if "email" in session:
                        session.pop('email', None)
                    if "username" in session:
                        session.pop('username', None)
                    if "original_token" in session:
                        session.pop('original_token', None)
                    if "auth_token" in session:
                        session.pop('auth_token', None)
                    if "password_token" in session:
                        session.pop('password_token', None)
                    login_user(user)
                    session['username'] = user.username

                    if profile:
                        if "previous_url" in session:
                            path_redirect = session['previous_url']
                            session.pop('previous_url', None)
                            return redirect(path_redirect)
                        else:
                            return redirect('/')
                    else:
                        return redirect(url_for('accounts.account_detail', _id=user.id))

                else:
                    flash("비밀번호를 확인하세요 . . . ")
                    return redirect(request.referrer)
            else:
                flash('이메일 인증이 되지 않았습니다. 메일을 확인하세요.')
                return redirect(url_for('accounts.login'))
    else:
        flash_form_errors(form)
        return redirect(request.referrer)


@account.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    session.pop('username', None) 대신에, 혹시 있을지 모를 다른 세션들까지 모두 clear
    """
    session.clear()
    logout_user()
    """로그인시 flask 가 생성 session["_user_id"]은 
    로그아웃과 동시에 저절로 삭제된다. 탈퇴시에는 이것을 삭제해줘야 모든 세션이 삭제된다."""
    return redirect(url_for('accounts.login'))


@account.route('/forget/password', methods=['GET'])
def forget_password():
    email_form = EmailForm()
    password_form = PasswordUpdateForm()
    return render_template('accounts/users/password.html',
                           email_form=email_form,
                           password_form=password_form,
                           password="forget")


@account.route('/password/update/<int:_id>', methods=['GET'])
@account_ownership_required
def password_update(_id):
    """로그인 상태: detail page 의 모달창으로 대체함
    password.html 의 if -- else 구문의 else 부위"""
    email_form = EmailForm()
    password_form = PasswordUpdateForm()
    return render_template('accounts/users/password.html',
                           email_form=email_form,
                           password_form=password_form)


@account.route('/password/save/ajax', methods=['POST'])
def password_save_ajax():
    if "_user_id" in session:
        print("session['_user_id']", session['_user_id'])
    if "email" in session:
        print("session['email']", session['email'])
    if "username" in session:
        print("session['username']", session['username'])
    if "original_token" in session:
        print("original_token", session['original_token'])
    if "auth_token" in session:
        print("auth_token", session['auth_token'])
    if "password_token" in session:
        print("password_token", session['password_token'])

    password = request.form.get("password")
    repassword = request.form.get("repassword")
    _id = request.form.get("user_id")
    if password != repassword:
        message = "비밀번호가 일치하지 않아요!"
        data = {"flash_message": message}
        return make_response(jsonify(data))
    if optimal_password_check(password) == "Not Optimal":
        password_not_optimal_msg = '비밀번호는 알파벳, 특수문자와 숫자를 모두 포함한 9자리 이상이어야 합니다.'
        data = {"flash_message": password_not_optimal_msg}
        return make_response(jsonify(data))
    hashed_password = security.generate_password_hash(password)
    if "password_token" in session:
        """이메일 잊어먹고 비로그인 상태에서 비밀번호 변경시"""
        """인증토큰 발행시 만들어진 password_token 세션을 확인하는 단계"""
        user_obj = User.query.filter_by(email=session['email']).first()
        user_obj.password = hashed_password
        user_obj.password_token = session['original_token']
        db.session.add(user_obj)
        db.session.commit()

        session.clear()
        password_data = {"_success": "success",
                         "res_msg": "비밀번호 재설정이 완료되었어요!",
                         "redirect_url": url_for("accounts.login")}
        return make_response(jsonify(password_data))
    elif "username" in session:
        """로그인 상태에서 비밀번호 변경시"""
        user_obj = User.query.filter_by(username=session['username']).first()
        """ownership 확인단계 if user_obj.id == int(_id):"""
        if user_obj.id == int(_id):
            user_obj.password = hashed_password
            db.session.add(user_obj)
            db.session.commit()

            session.clear()
            logout_user()
            password_data = {"_success": "success",
                             "res_msg": "비밀번호 재설정이 완료되었어요!",
                             "redirect_url": url_for("accounts.login")}
            return make_response(jsonify(password_data))
        else:
            password_data = error_401_json_data()
            return make_response(jsonify(password_data))
    else:
        password_data = error_401_json_data()
        return make_response(jsonify(password_data))


@account.route('/<add_if>/update/<int:_id>', methods=['GET'])
@account_ownership_required
def username_email_update(_id, add_if):
    """모달 형식이 아닌 방법: 여기서는 사용하지 않았다.
    아이디(username)은 수정불가능으로 정책을 정하고 사용하지 않음"""
    if add_if == "username":
        form = UsernameForm()
        return render_template("accounts/users/username.html", form=form)
    elif add_if == "email":
        form = EmailForm()
        return render_template("accounts/users/email.html", form=form)


@account.route('/email/update/ajax/<int:_id>', methods=['POST'])
@account_ownership_required
def email_update_ajax(_id):
    email = request.form.get("email")
    _id = request.form.get("user_id")
    target_user = User.query.filter_by(id=_id, is_verified=True).first()
    if target_user == current_user:
        target_user.email = email
        db.session.add(target_user)
        db.session.commit()

        session.pop('auth_token', None)
        session.pop('original_token', None)
        session.pop('email', None)
        flash("이메일변경이 완료되었어요!")
        data = {"_success": "success",
                "redirect_url": url_for("accounts.account_detail", _id=target_user.id)}
        return make_response(jsonify(data))
    else:
        data = error_401_json_data()
        return make_response(jsonify(data))


@account.route('/delete/ajax', methods=['POST'])
def delete_ajax():
    _id = request.form.get("_id")
    target_user = db.session.query(User).filter_by(id=_id).first()
    if target_user:
        target_profile = db.session.query(Profile).filter_by(user_id=target_user.id).first()
        if target_profile and ((current_user == target_user) or current_user.is_admin):
            profile_delete(target_profile)

        accounts_related_obj_delete(target_user)

        db.session.delete(target_user)
        db.session.commit()

        if current_user.is_authenticated and current_user.is_admin:
            _data_response = {"_success": "success",
                              "redirect_url": url_for('admin_accounts.user_list')}
            return make_response(jsonify(_data_response))
        else:
            session.clear()
            logout_user()
            # session.pop('username', None)
            # session.pop('_user_id', None)
            """로그인시 flask 가 생성 session["_user_id"]은 
                로그아웃과 동시에 저절로 삭제된다. 
                그러나 탈퇴시에는 이것을 삭제해줘야 모든 세션이 삭제된다."""
            _data_response = {"_success": "success",
                              "_delete": "delete",
                              "redirect_url": url_for('commons.index')}
            return make_response(jsonify(_data_response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@account.route('/profiles/existing/nickname/check/ajax', methods=['POST'])
@login_required
def existing_nickname_check_ajax():
    """이용자/관리자 단 통합(existing_req_data_check): 닉네임과 회사명을 체크하는 ajax"""
    profile_id = request.form.get("profile_id")  # 이용자단, 어드민단의 change
    _user_email = request.form.get("user_email")  # 어드민단의 create
    req_nickname = request.form.get("nickname")

    target_profile = db.session.query(Profile).filter_by(id=profile_id).first()
    existing_nickname_profile = Profile.query.filter_by(nickname=req_nickname).first()

    if target_profile:  # 이용자단 change, 어드민단의 change
        target_user = User.query.filter_by(id=target_profile.user_id).first()
        if target_user:
            """이용자단이든 어드민 단이든 프로필이 있으면 target_user 를 당연히 찾을 수있다."""
            if (current_user == target_user) or current_user.is_admin:
                _type = "닉네임"
                flash_message = existing_req_data_check(_type, req_nickname, existing_nickname_profile, target_profile, target_profile.nickname)
                return flash_message
            else:
                flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "유효하지 않은 요청(Error 400)", }
            return make_response(jsonify(flash_message))
    elif _user_email:  # 이용자단의 create, 어드민단의 create
        _target_user = User.query.filter_by(email=_user_email).first()
        if _target_user:
            if (current_user == _target_user) or current_user.is_admin:
                _type = "닉네임"
                flash_message = existing_req_data_check(_type, req_nickname, existing_nickname_profile, None, None)
                return flash_message
            else:
                flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "유효하지 않은 요청(Error 400)", }
            return make_response(jsonify(flash_message))
    else:
        flash_message = {"flash_message": "프로필 등록을 위한 회원정보가 없네요!(Error 404)", }
        return make_response(jsonify(flash_message))


@account.route('/profile/existing/corp_brand/check/ajax', methods=['POST'])
def existing_corp_brand_check_ajax():
    """이용자/관리자 단 통합: 닉네임과 회사명을 체크하는 ajax"""
    profile_id = request.form.get("profile_id")  # 이용자단, 어드민단의 change
    # user_id = request.form.get("user_id")
    _user_email = request.form.get("user_email")  # 어드민단의 create

    req_corp_brand = request.form.get("corp_brand")
    target_profile = db.session.query(Profile).filter_by(id=profile_id).first()
    existing_corp_brand_profile = Profile.query.filter_by(corp_brand=req_corp_brand).first()

    if target_profile:
        """target_profile 이 있으면, 이용자단이든 어드민 단이든 target_user 를 당연히 찾을 수있다."""
        target_user = User.query.filter_by(id=target_profile.user_id).first()
        if target_user:
            if (current_user == target_user) or current_user.is_admin:
                _type = "회사명"
                flash_message = existing_req_data_check(_type, req_corp_brand, existing_corp_brand_profile, target_profile, target_profile.corp_brand)
                return flash_message
            else:
                flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "유효하지 않은 요청(Error 400)", }
            return make_response(jsonify(flash_message))
    elif _user_email:  # 어드민단의 create
        _target_user = User.query.filter_by(email=_user_email).first()
        if _target_user:
            if current_user.is_admin:
                _type = "회사명"
                flash_message = existing_req_data_check(_type, req_corp_brand, existing_corp_brand_profile, None, None)
                return flash_message
            else:
                flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "유효하지 않은 요청(Error 400))", }
            return make_response(jsonify(flash_message))
    else:
        flash_message = {"flash_message": "회사명 등록을 위한 회원정보가 없네요!(Error 404)", }
        return make_response(jsonify(flash_message))


_response = ""


@account.route('/profile/save/ajax', methods=['POST'])
def profile_save_ajax():
    """이용자 단 기본 프로필과 어드민단 기본/판매자 프로필을 통합했다.
    이용자단의 판매자 신청은 vendor_update_ajax 로 분리했다."""
    global _response
    user_id = request.form.get("user_id")  # user 단

    req_email = request.form.get("user_email")  # admin 단 profile_create
    req_profile_id = request.form.get("profile_id")  # admin 단 (create:None) update
    print(req_profile_id)

    req_nickname = request.form.get("nickname")
    message = request.form.get("message")
    level = request.form.get("level")  # admin 단
    cover_image = request.files.get('cover_image')
    profile_image = request.files.get('profile_image')

    req_corp_brand = request.form.get("corp_brand")
    corp_email = request.form.get("corp_email")
    corp_online_marketing_number = request.form.get("corp_online_marketing_number")
    corp_number = request.form.get("corp_number")
    corp_image = request.files.get("corp_image")
    corp_address = request.form.get("corp_address")
    main_phonenumber = request.form.get("main_phonenumber")
    main_cellphone = request.form.get("main_cellphone")

    existing_nickname_profile = Profile.query.filter_by(nickname=req_nickname).first()
    existing_corp_brand_profile = Profile.query.filter_by(corp_brand=req_corp_brand).first()
    cover_img_request_path = "profiles/cover_images"
    profile_img_request_path = "profiles/profile_images"
    corp_img_request_path = "profiles/corp_images"

    if current_user.is_admin:
        req_user = User.query.filter_by(email=req_email).first()  # admin 단
        if req_profile_id != "None":
            target_profile = Profile.query.filter_by(id=req_profile_id).first()  # admin 단
            target_user = User.query.get_or_404(target_profile.user_id)
            if existing_nickname_profile and existing_corp_brand_profile:
                if req_corp_brand != "None":
                    if target_user != existing_nickname_profile.user:
                        if target_user != existing_corp_brand_profile.user:
                            flash("동일한 닉네임과 회사명이 존재합니다.")
                            return redirect(request.referrer)
            elif existing_nickname_profile:
                if target_user != existing_nickname_profile.user:
                    flash("동일한 닉네임이 존재합니다...")
                    return redirect(request.referrer)
            elif existing_corp_brand_profile:
                if req_corp_brand != "None":
                    if target_user != existing_corp_brand_profile.user:
                        flash("동일한 회사명이 존재합니다.")
                        return redirect(request.referrer)
            if req_nickname and not existing_nickname_profile:
                target_profile.nickname = req_nickname
            if message:
                target_profile.message = message
            target_profile.level = level
            vendor_save(target_profile, req_corp_brand, corp_email, corp_online_marketing_number, corp_number, corp_address, main_phonenumber, main_cellphone)

            if cover_image:
                profile_cover_img_save(target_profile, cover_img_request_path, cover_image, target_user)
            if profile_image:
                profile_profile_img_save(target_profile, profile_img_request_path, profile_image, target_user)
            if corp_image:
                profile_corp_img_save(target_profile, corp_img_request_path, corp_image, target_user)
            db.session.add(target_profile)
            db.session.commit()
            flash("프로필 수정이 완료되었습니다.")
            return redirect(request.referrer)
        else:
            """new profile 생성"""
            if not req_user:
                flash("프로필 등록을 위한 회원정보가 없네요!(Error 404)")
                return redirect(request.referrer)
            if existing_nickname_profile and existing_corp_brand_profile:
                flash("동일한 닉네임과 회사명이 존재합니다.")
                return redirect(request.referrer)
            if existing_nickname_profile:
                flash("동일한 닉네임이 존재합니다.")
                return redirect(request.referrer)
            if existing_corp_brand_profile:
                flash("동일한 회사명이 존재합니다.")
                return redirect(request.referrer)
            new_profile = Profile(
                nickname=req_nickname,
                message=message,
                user_id=req_user.id
            )
            new_profile.level = level
            vendor_save(new_profile, req_corp_brand, corp_email, corp_online_marketing_number, corp_number, corp_address, main_phonenumber, main_cellphone)

            if cover_image:
                profile_cover_img_save(new_profile, cover_img_request_path, cover_image, req_user)
            if profile_image:
                profile_profile_img_save(new_profile, profile_img_request_path, profile_image, req_user)
            if corp_image:
                profile_corp_img_save(new_profile, corp_img_request_path, corp_image, req_user)
            db.session.add(new_profile)
            db.session.commit()
            flash("프로필 등록이 완료되었습니다.")
            return redirect(url_for("admin_accounts.profile_change", _id=new_profile.id))
    elif user_id:
        """이용자 단"""
        target_user = User.query.filter_by(id=user_id).first()  # 이용자 단
        target_profile = Profile.query.filter_by(user_id=user_id).first()  # 이용자 단
        if current_user == target_user:
            if req_nickname:
                if message:
                    if target_profile:
                        if existing_nickname_profile and (req_nickname != target_profile.nickname):
                            _response = {"flash_message": "동일한 닉네임이 존재합니다."}
                        else:
                            target_profile.nickname = req_nickname
                            target_profile.message = message

                            if cover_image:
                                profile_cover_img_save(target_profile, cover_img_request_path, cover_image, target_user)
                            if profile_image:
                                profile_profile_img_save(target_profile, profile_img_request_path, profile_image, target_user)
                            db.session.add(target_profile)
                            db.session.commit()
                            _response = {"_save": "update",
                                         "profile_id": target_profile.id,
                                         "nickname": req_nickname,
                                         "_message": message,
                                         "profile_img_path": target_profile.profile_img_path,
                                         "cover_img_path": target_profile.cover_img_path}
                    else:
                        """new profile 생성"""
                        if existing_nickname_profile:
                            _response = {"flash_message": "동일한 닉네임이 존재합니다."}
                        else:
                            new_profile = Profile(
                                user_id=user_id,
                                nickname=req_nickname,
                                message=message,
                            )
                            if cover_image and profile_image:
                                profile_cover_img_save(new_profile, cover_img_request_path, cover_image, target_user)
                                profile_profile_img_save(new_profile, profile_img_request_path, profile_image, target_user)
                            elif not cover_image and profile_image:
                                _response = {"flash_message": "커버이미지를 등록 해주세요!"}
                            elif cover_image and not profile_image:
                                _response = {"flash_message": "프로필이미지를 등록 해주세요!"}
                            elif not cover_image and not profile_image:
                                _response = {"flash_message": "커버이미지와 프로필이미지를 등록 해주세요!"}
                            db.session.add(new_profile)
                            db.session.commit()
                            _response = {"_save": "create",
                                         "profile_id": new_profile.id,
                                         "nickname": req_nickname,
                                         "_message": message,
                                         "profile_img_path": new_profile.profile_img_path,
                                         "cover_img_path": new_profile.cover_img_path}
                else:
                    _response = {"flash_message": "간단 메시지를 작성해주세요!"}
            else:
                _response = {"flash_message": "닉네임을 작성해주세요!"}
            return make_response(jsonify(_response))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_401_json_data()
        return make_response(jsonify(data))


data_response = ""


@account.route('/profile/vendor/update/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_update_ajax(_id):
    """이용자의 판매자신청 요건: 프로필이 있어야 하고, is_vendor True 이어야 판매자 신청 버튼 활성화된다."""
    global data_response
    profile = db.session.query(Profile).filter_by(id=_id).first()
    real_level = profile.level
    if profile:
        req_corp_brand = request.form.get("corp_brand")
        corp_email = request.form.get("corp_email")
        corp_number = request.form.get("corp_number")
        corp_online_marketing_number = request.form.get("corp_online_marketing_number")
        corp_address = request.form.get("corp_address")
        main_phonenumber = request.form.get("main_phonenumber")
        main_cellphone = request.form.get("main_cellphone")
        corp_image = request.files.get('corp_image')

        existing_corp_brand_profile = Profile.query.filter_by(corp_brand=req_corp_brand).first()            # if corp_brand:  # != profile.corp_brand:
        if existing_corp_brand_profile:
            if req_corp_brand != profile.corp_brand:
                data_response = {
                    "flash_message": "동일한 회사명이 존재합니다.",
                }
                return make_response(jsonify(data_response))

        if req_corp_brand and corp_email and corp_number and corp_online_marketing_number and corp_address and main_phonenumber and main_cellphone:

            req_level = request.form.get("level")  # 이용자 단
            if req_level == real_level:
                if profile.level == "일반이용자":
                    profile.level = PROFILE_LEVELS[1]  # 심사중 판매사업자로 update

                vendor_save(profile, req_corp_brand, corp_email, corp_online_marketing_number, corp_number, corp_address, main_phonenumber, main_cellphone)
                if corp_image:
                    request_path = "profiles/corp_images"
                    profile_corp_img_save(profile, request_path, corp_image, current_user)
                elif not corp_image:
                    if not profile.corp_img_path:
                        data_response = {"flash_message": "사업자등록증을 채워주세요!",}
                        return make_response(jsonify(data_response))

                db.session.add(profile)
                db.session.commit()

                if real_level == "일반이용자":
                    add_if = "vendor_request"
                    add_if_admin = "vendor_request_admin"
                    subject = f"{current_user.email}님의 판매사업자 신청메일"
                elif real_level == "심사중 판매사업자":
                    add_if = "vendor_pending"
                    add_if_admin = "vendor_pending_admin"
                    subject = f"{current_user.email}님의 판매사업자 신청정보 변경메일"
                else:
                    add_if = "vendor_update"
                    add_if_admin = "vendor_update_admin"
                    subject = f"{current_user.email}님의 판매사업자정보 변경메일"
                user_email = current_user.email
                admin_email = SUPER_ADMIN_EMAIL
                token = "None"
                msg_txt = 'includes/send_mails/mail.txt'
                msg_html = 'includes/send_mails/accounts/accounts_mail.html'
                any_send_mail(subject, current_user, user_email, token, msg_txt, msg_html, add_if)
                any_send_mail(subject, current_user, admin_email, token, msg_txt, msg_html, add_if_admin)

                flash("판매자정보 작성이 완료되었습니다.(첫 작성시는 신청완료됨)")

                """data_response 는 넘겨도 사용하고 있지는 않고 있다."""
                data_response = {
                    "_success": "success",
                    "corp_brand": profile.corp_brand,
                    "corp_email": profile.corp_email,
                    "corp_number": profile.corp_number,
                    "corp_online_marketing_number": profile.corp_online_marketing_number,
                    "corp_image_path": profile.corp_img_path,
                    "corp_address": profile.corp_address,
                    "main_phonenumber": profile.main_phonenumber,
                    "main_cellphone": profile.main_cellphone,
                    "profile_level": profile.level
                }

                return make_response(jsonify(data_response))
            else:
                data_response = {"flash_message": "실제 이용자 레벨과 다르네요!",}
                return make_response(jsonify(data_response))
        elif not req_corp_brand:
            data_response = {"flash_message": "회사명을 채워주세요!",}
        elif not corp_email:
            data_response = {"flash_message": "사업자용 이메일을 채워주세요!",}
        elif not corp_online_marketing_number:
            data_response = {"flash_message": "통신판매업번호를 채워주세요!",}
        elif not corp_number:
            data_response = {"flash_message": "사업자등록번호를 채워주세요!",}
        elif not corp_address:
            data_response = {"flash_message": "사업자주소를 채워주세요!",}
        elif not main_phonenumber:
            data_response = {"flash_message": "대표전화번호를 채워주세요!",}
        elif not main_cellphone:
            data_response = {"flash_message": "사업자휴대폰번호를 채워주세요!",}
        return make_response(jsonify(data_response))

    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@account.route('/profile/vendor/delete/ajax/<int:_id>', methods=['POST'])
@profile_ownership_required
def vendor_delete_ajax(_id):
    profile = db.session.query(Profile).filter_by(id=_id).first()
    if profile:
        if profile.level != "일반이용자":
            profile.level = "일반이용자"
        profile.corp_brand = ""
        profile.corp_email = ""
        profile.corp_number = ""
        profile.corp_online_marketing_number = ""

        existing_corp_image_path = profile.corp_img_path
        if existing_corp_image_path:
            img_delete(existing_corp_image_path)
        profile.corp_img_path = ""

        profile.corp_address = ""
        profile.main_phonenumber = ""
        profile.main_cellphone = ""
        db.session.add(profile)
        db.session.commit()

        """판매자정보 삭제시 해당 프로필주인이 생성한 판매관련 obj 들 중에서 
            disable 하거나 삭제 필요한 다른 obj(shop 혹은 상품 등) 처리"""
        flash("판매자 정보가 성공적으로 삭제되었습니다.")
        empty_data_response = {"_success": "success"}
        return make_response(jsonify(empty_data_response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@account.route('profiles/account/detail/<int:_id>', methods=['GET'])
@login_required
def account_detail(_id):
    """
    _id 는 User.id 임 : 가입하고 인증완료되면 로그인 화면에서 여기로 리디렉션 되기 때문(프로필이 없으므로 User.id를 사용)
    """
    form = ProfilesForm()
    user = User.query.get_or_404(_id)
    profile = Profile.query.filter_by(user_id=_id).first()
    email_form = EmailForm()
    password_form = PasswordUpdateForm()

    target_ac_query = ArticleCategory.query.order_by(desc(ArticleCategory.created_at)).filter_by(user_id=user.id, available_display=True)
    page = request.args.get('page', type=int, default=1)
    pagination = target_ac_query.paginate(page=page, per_page=PROFILE_PER_PAGE, error_out=False)
    target_ac_objs = pagination.items

    target_article_query = Article.query.order_by(desc(Article.created_at)).filter_by(user_id=user.id, available_display=True)
    page_2 = request.args.get('page_2', type=int, default=1)
    pagination_2 = target_article_query.paginate(page=page_2, per_page=PROFILE_PER_PAGE, error_out=False)
    target_article_objs = pagination_2.items

    target_shop_query = Shop.query.order_by(desc(Shop.created_at)).filter_by(user_id=user.id, available_display=True)
    page_3 = request.args.get('page_3', type=int, default=1)
    pagination_3 = target_shop_query.paginate(page=page_3, per_page=PROFILE_PER_PAGE, error_out=False)
    target_shop_objs = pagination_3.items

    target_product_query = Product.query.order_by(desc(Product.created_at)).filter_by(user_id=user.id, available_display=True)
    page_4 = request.args.get('page_4', type=int, default=1)
    pagination_4 = target_product_query.paginate(page=page_4, per_page=PROFILE_PER_PAGE, error_out=False)
    target_product_objs = pagination_4.items

    return render_template('accounts/profiles/detail.html',
                           form=form,
                           target_user=user,
                           target_profile=profile,
                           email_form=email_form,
                           password_form=password_form,

                           target_acs=target_ac_objs,
                           pagination=pagination,

                           target_articles=target_article_objs,
                           pagination_2=pagination_2,

                           target_shops=target_shop_objs,
                           pagination_3=pagination_3,

                           target_products=target_product_objs,
                           pagination_4=pagination_4
                           )


@account.route('profiles/detail/<int:_id>', methods=['GET'])
@login_required
def profile_detail(_id):
    """
    _id 는 Profile.id 임 : profile 이 만들어 진후에는 여기로도 진입이 가능하다.
    """
    form = ProfilesForm()
    profile = Profile.query.get_or_404(_id)
    user = User.query.filter_by(id=profile.user_id).first()
    email_form = EmailForm()
    password_form = PasswordUpdateForm()
    return render_template('accounts/profiles/detail.html',
                           form=form,
                           target_user=user,
                           target_profile=profile,
                           email_form=email_form,
                           password_form=password_form,
                           )


delete_response = ""


@account.route('/profile/delete/ajax', methods=['POST'])
def profile_delete_ajax():
    global delete_response
    _id = request.form.get("profile_id")
    if _id:
        target_profile = db.session.query(Profile).filter_by(id=_id).first()
        if target_profile:
            target_user = User.query.filter_by(id=target_profile.user_id).first()
            if target_user:
                """#### ownership 과 admin 을 체크하고 진행 ####"""
                if (current_user == target_user) or current_user.is_admin:
                    profile_delete(target_profile)

                    accounts_related_obj_delete(target_user)
                    """프로필 삭제시 해당 프로필주인이 생성한 obj 들 중에서 
                    disable 하거나 삭제 필요한 다른 obj(shop 혹은 상품 등) 처리"""

                    db.session.commit()
                    if current_user == target_user:
                        flash("프로필이 삭제되었어요!")
                        delete_response = {"_success": "success",
                                           "_delete": "delete",
                                           "redirect_url": url_for('accounts.account_detail', _id=target_user.id)}
                        return make_response(jsonify(delete_response))
                    if current_user.is_admin:
                        # flash("프로필이 삭제되었어요!")  # 어드민 리스트에서 여러개 삭제시 메시지가 반복하므로 사용안함
                        delete_response = {
                            "_success": "success",
                            "_delete": "delete",
                            "redirect_url": url_for('admin_accounts.profile_list')
                        }
                        return make_response(jsonify(delete_response))
                else:
                    data = error_401_json_data()
                    return make_response(jsonify(data))
            else:
                data = error_400_json_data()
                return make_response(jsonify(data))
        else:
            data = error_400_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))
