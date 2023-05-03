import re

from flask import session, render_template, g
from flask_mail import Message

from configs import mail, db
from configs.config import Config
from www.accounts.models import User
from www.boards.articles.models import ArticleCategory, Article
from www.commons.utils import img_delete, img_update, save_file


subject = ""
token = ""


def token_create_send_mail(random, email, req_add_if):
    global subject
    from configs import safe_time_serializer
    random_email = random + '?' + email
    original_token = safe_time_serializer.dumps(random_email, salt='email-confirm')
    if "email" in session:
        session.pop('email', None)
    if "original_token" in session:
        session.pop('original_token', None)
    session['email'] = email
    session['original_token'] = original_token
    created_token = shortening_token(req_add_if, original_token)

    if req_add_if == "forget_password":
        subject = "[Beta-version] 비밀번호 재설정 인증번호입니다."
    elif req_add_if == "register":
        subject = "[Beta-version] 회원가입 이메일 인증번호입니다."
    elif req_add_if == "email":
        subject = "[Beta-version] 이메일 변경을 위한 인증번호입니다."
    _txt = 'includes/send_mails/mail.txt'
    _html = 'includes/send_mails/accounts/token.html'
    msg = Message(subject, sender=Config().MAIL_USERNAME, recipients=[email])
    msg.body = render_template(_txt)
    msg.html = render_template(_html, add_if=req_add_if, token=created_token, email=email)
    mail.send(msg)


def shortening_token(req_add_if, original_token):
    global token
    if "password_token" in session:
        session.pop('password_token', None)
    if "auth_token" in session:
        session.pop('auth_token', None)
    if req_add_if == "forget_password":
        session['password_token'] = original_token[0:10]
        token = session['password_token']
    elif (req_add_if == "register") or (req_add_if == "email"):
        session['auth_token'] = original_token[0:10]
        token = session['auth_token']
    return token


def email_match_check(value):
    email_reg = "^([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$"
    regex = re.compile(email_reg)
    email_match = re.search(regex, value)
    if email_match:
        return "email_match"
    else:
        return "Not email_match"


def user_check(value):
    email_match = email_match_check(value)
    if email_match == 'email_match':
        user_obj = User.query.filter_by(email=value).first()
    else:
        user_obj = User.query.filter_by(username=value).first()
    return user_obj


def existing_email_check(email):
    existing_email_user = User.query.filter_by(email=email).first()
    if existing_email_user:
        return "Existing"


def existing_username_check(username):
    existing_username_user = User.query.filter_by(username=username).first()
    if existing_username_user:
        return "Existing"


def optimal_password_check(password):
    password_reg = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*?_=+-])[A-Za-z\d!@#$%^&*?_=+-]{9,30}$"
    regex = re.compile(password_reg)
    password_optimal = re.search(regex, str(password))
    if not password:
        return "No Password"
    if not password_optimal:
        return "Not Optimal"
    else:
        return "Optimal"


def profile_cover_img_save(obj, req_path, img, user):
    existing_img_path = obj.cover_img_path
    if img:
        if existing_img_path:
            relative_path = img_update(existing_img_path, img, req_path, user)
            obj.cover_img_path = relative_path
        else:
            relative_path, _ = save_file(img, req_path, user)
            obj.cover_img_path = relative_path


def profile_profile_img_save(obj, req_path, img, user):
    existing_img_path = obj.profile_img_path
    if img:
        if existing_img_path:
            relative_path = img_update(existing_img_path, img, req_path, user)
            obj.profile_img_path = relative_path
        else:
            relative_path, _ = save_file(img, req_path, user)
            obj.profile_img_path = relative_path


def profile_corp_img_save(obj, req_path, img, user):
    existing_img_path = obj.corp_img_path
    if img:
        if existing_img_path:
            relative_path = img_update(existing_img_path, img, req_path, user)
            obj.corp_img_path = relative_path
        else:
            relative_path, _ = save_file(img, req_path, user)
            obj.corp_img_path = relative_path


def vendor_save(profile, req_corp_brand, corp_email, corp_online_marketing_number, corp_number, corp_address, main_phonenumber, main_cellphone):
    if req_corp_brand:
        profile.corp_brand = req_corp_brand
    if corp_email:
        profile.corp_email = corp_email
    if corp_online_marketing_number:
        profile.corp_online_marketing_number = corp_online_marketing_number
    if corp_number:
        profile.corp_number = corp_number
    if corp_address:
        profile.corp_address = corp_address
    if main_phonenumber:
        profile.main_phonenumber = main_phonenumber
    if main_cellphone:
        profile.main_cellphone = main_cellphone


def profile_delete(profile):
    profile_img_path = profile.profile_img_path
    cover_img_path = profile.cover_img_path
    corp_img_path = profile.corp_img_path
    try:
        if profile_img_path:
            img_delete(profile_img_path)
        if cover_img_path:
            img_delete(cover_img_path)
        if corp_img_path:
            img_delete(corp_img_path)
    except Exception as e:
        print(e)
    db.session.delete(profile)


def user_delete_articles_change(ac_objs, article_objs):
    if ac_objs:
        for ac_obj in ac_objs:
            if ac_obj.img_path:
                img_delete(ac_obj.img_path)
            target_ac_tags = ac_obj.tag_ac_set
            for ac_tag in target_ac_tags:
                db.session.delete(ac_tag)
            db.session.delete(ac_obj)
    if article_objs:
        for article in article_objs:
            """ArticleComment 는 노출상태를 display = True 로 유지한다."""
            # article_comment_objs = article.comment_article_set
            # for comment in article_comment_objs:
            #     comment.available_display = False
            #     db.session.add(comment)
            article.available_display = False
            db.session.add(article)


def user_delete_products_change(shop_objs, pc_objs, product_objs):
    if shop_objs:
        for shop in shop_objs:
            db.session.delete(shop)
    if pc_objs:
        for pc in pc_objs:
            db.session.delete(pc)
    if product_objs:
        for product in product_objs:
            product.available_display = False
            product.available_order = False
            db.session.add(product)


def accounts_related_obj_delete(target_user):
    target_ac_objs = db.session.query(ArticleCategory).filter_by(user_id=target_user.id).all()
    target_article_objs = db.session.query(Article).filter_by(user_id=target_user.id).all()
    user_delete_articles_change(target_ac_objs, target_article_objs)

    target_shop_objs = target_user.shop_user_set
    target_pc_objs = target_user.pc_user_set
    target_product_objs = target_user.product_user_set
    user_delete_products_change(target_shop_objs, target_pc_objs, target_product_objs)

    target_coupon_objs = target_user.coupon_owner_set
    """UsedCoupon(사용한 쿠폰기록)은 보존"""
    if target_coupon_objs:
        for coupon in target_coupon_objs:
            db.session.delete(coupon)

    """PointLog(사용한 포인트기록)은 보존 """
    if target_user.point_owner_set:
        target_point_obj = target_user.point_owner_set[0]
        db.session.delete(target_point_obj)



