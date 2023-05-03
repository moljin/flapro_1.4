from flask import session, redirect, url_for, flash, request, render_template
from flask_login import login_user
from flask_mail import Message
from werkzeug import security

from configs import db, mail
from configs.config import Config


def admin_login(user, req_password):
    if security.check_password_hash(user.password, req_password):
        session.clear()
        login_user(user)
        session['username'] = user.username  # 추가
        return redirect(url_for("admin_accounts.index"))
    else:
        flash("비밀번호를 확인하세요 . . . ")
        return redirect(request.referrer)


def admin_user_save(user, auth_token, password_token, admin_token, is_verified, is_staff, is_vendor, is_admin):
    if auth_token is not None:
        user.auth_token = auth_token
    if password_token is not None:
        user.password_token = password_token
    if admin_token is not None:
        user.admin_token = admin_token
    print("is_verified", is_verified)
    print("is_staff", is_staff)
    print("is_admin", is_admin)
    """checked 이면 on, not checked 이면 None 으로 리턴된다."""
    if is_verified is not None:
        user.is_verified = True
    else:
        user.is_verified = False

    if is_staff is not None:
        user.is_staff = True
    else:
        user.is_staff = False

    if is_vendor is not None:
        user.is_vendor = True
    else:
        user.is_vendor = False

    if is_admin is not None:
        user.is_admin = True
    else:
        user.is_admin = False
    db.session.add(user)
    db.session.commit()


def admin_user_other_save(user):
    user.is_use = True
    user.is_info = True
    user.is_email = True
    user.is_bank = True
    user.is_marketing = True
    user.is_third = True
    db.session.add(user)
    db.session.commit()


def admin_send_mail(subject, authorizer_email, token, msg_txt, msg_html, add_if, req_email, is_staff, is_admin):
    msg = Message(subject, sender=Config().MAIL_USERNAME, recipients=[authorizer_email])
    admin_page = "http://127.0.0.1:5000/admin"#url_for("admin_accounts.index",) # url_for는 왜 안되지???
    print('admin_page = url_for("admin_accounts.index")', admin_page)
    if add_if == "auth_permission" or "not_admin":
        confirm_page = url_for('admin_accounts.auth_confirm_email',
                               token=token,
                               add_if=add_if,
                               req_email=req_email,
                               is_staff=is_staff,
                               is_admin=is_admin,
                               _external=True)
        print("confirm_page::::", confirm_page)
    else:
        confirm_page = None
    msg.body = render_template(msg_txt)
    msg.html = render_template(msg_html,
                               admin=admin_page,
                               confirm=confirm_page,
                               email=authorizer_email,
                               add_if=add_if,
                               req_email=req_email,
                               is_staff=is_staff,
                               is_admin=is_admin)
    mail.send(msg)

    # return True


def is_admin_true_save(user_obj):
    user_obj.is_admin = True
    db.session.add(user_obj)
    db.session.commit()


def is_staff_true_save(user_obj):
    user_obj.is_staff = True
    db.session.add(user_obj)
    db.session.commit()


def is_admin_staff_true_save(user_obj):
    user_obj.is_admin = True
    user_obj.is_staff = True
    db.session.add(user_obj)
    db.session.commit()


def is_admin_false_save(user_obj):
    user_obj.is_admin = False
    db.session.add(user_obj)
    db.session.commit()


def is_staff_false_save(user_obj):
    user_obj.is_staff = False
    db.session.add(user_obj)
    db.session.commit()


def is_admin_staff_false_save(user_obj):
    user_obj.is_admin = False
    user_obj.is_staff = False
    db.session.add(user_obj)
    db.session.commit()





