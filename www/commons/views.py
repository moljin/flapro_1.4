import datetime
import json

from flask import Blueprint, render_template, session, request, make_response, jsonify, g, flash
from flask_login import current_user

from configs import db
from www.accounts.models import User
from www.boards.articles.models import ArticleSunImage, ArticleCommentSunImage
from www.commons.required import login_required
from www.commons.utils import base64_to_file, error_400_json_data
from www.ecomm.carts.models import Cart
from www.ecomm.orders.models import Order
from www.ecomm.products.models import ProductSunImage, Shop

NAME = 'commons'
common = Blueprint(NAME, __name__)


@common.route('/')
def index():
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
    # print(p)
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        orders = Order.query.filter_by(buyer_id=current_user.id).all()
        return render_template('commons/index.html', now=datetime.datetime.now())#, cart=cart, orders=orders)
    else:
        return render_template('commons/index.html', now=datetime.datetime.now())


@common.route('/main/')
def main():
    # return render_template('commons/test.html')
    return render_template('commons/main.html')
    # return render_template('moreLoadTest.html')


@common.route('/server/dev')
def server():
    return render_template('extra_page/server.html')


@common.route('/extra/related/dev')
def extra_dev():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
        orders = Order.query.filter_by(buyer_id=current_user.id).all()
        if cart:
            return render_template('extra_page/related_dev.html', cart=cart, orders=orders)
        else:
            return render_template('extra_page/related_dev.html', orders=orders)
    else:
        return render_template('extra_page/related_dev.html')


sun_image_obj, image_path = "", ""


@common.route('/sun/editor/images/save/ajax', methods=['POST'])
@login_required
def editor_images_save_ajax():
    global sun_image_obj, image_path
    sun_init = request.form.get("sun_init")
    email = request.form.get("user_email")

    orm_id = request.form.get("orm_id")
    image_string = request.form.get('upload_img')
    file_name = request.form.get('file_name')

    if sun_init == "article_CU":
        request_path = "articles/sun_images"
        if current_user.is_admin and "admin" in request.referrer:
            target_user = User.query.filter_by(email=email).first()
            image_path, file_name = base64_to_file(image_string, file_name, request_path, target_user)
            sun_image_obj = ArticleSunImage(user_id=target_user.id, orm_id=orm_id)
        else:
            image_path, file_name = base64_to_file(image_string, file_name, request_path, current_user)
            sun_image_obj = ArticleSunImage(user_id=g.user.id, orm_id=orm_id)

    elif sun_init == "article_comment_CU":
        request_path = "articles/comment/sun_images"
        article_id = request.form.get("article_id")

        if current_user.is_admin and "admin" in request.referrer:
            target_user = User.query.filter_by(email=email).first()
            image_path, file_name = base64_to_file(image_string, file_name, request_path, target_user)
            sun_image_obj = ArticleCommentSunImage(user_id=target_user.id, orm_id=orm_id)

        else:
            # image_path, file_name, sun_image_obj = user_path_article_sun_image(image_string, file_name, request_path, orm_id)
            image_path, file_name = base64_to_file(image_string, file_name, request_path, current_user)
            sun_image_obj = ArticleCommentSunImage(user_id=g.user.id, orm_id=orm_id)
        sun_image_obj.article_id = article_id
    elif sun_init == "product_CU":
        shop_id = request.form.get("shop_id")
        target_shop = Shop.query.filter_by(id=shop_id).first()
        request_path = f"products/sun_images"
        if current_user.is_admin and "admin" in request.referrer:
            target_user = User.query.filter_by(email=email).first()
            image_path, file_name = base64_to_file(image_string, file_name, request_path, target_user)
            sun_image_obj = ProductSunImage(user_id=target_user.id, orm_id=orm_id)
        else:
            image_path, file_name = base64_to_file(image_string, file_name, request_path, current_user)
            sun_image_obj = ProductSunImage(user_id=g.user.id, orm_id=orm_id)

    if image_path:
        sun_image_obj.img_path = image_path
        sun_image_obj.original_filename = file_name
    db.session.add(sun_image_obj)
    db.session.commit()

    context = {
        "image_path": sun_image_obj.img_path,
        "original_filename": file_name
    }
    return make_response(jsonify(context))


@common.route('/error/400', methods=['GET'])
def jsonify_error_400():
    msg = request.args.get("res_msg")
    if msg:
        flash(msg)
    return render_template('errors/400.html'), 400


@common.route('/error/401', methods=['GET'])
def jsonify_error_401():
    msg = request.args.get("res_msg")
    if msg:
        flash(msg)
    return render_template('errors/401.html'), 401


@common.route('/error/404', methods=['GET'])
def jsonify_error_404():
    msg = request.args.get("res_msg")
    if msg:
        flash(msg)
    return render_template('errors/404.html'), 404


@common.route('/internal/server/error/500', methods=['GET'])
def jsonify_error_500():
    msg = request.args.get("res_msg")
    if msg:
        flash(msg)
    return render_template('errors/500.html'), 500


@common.route('/user/email/select/ajax', methods=['POST'])
def user_email_select_ajax():
    user_email = request.form.get("user_email")
    target_user = User.query.filter_by(email=user_email).first()
    _type = request.form.get("type")
    if _type == "admin_product_create":
        user_shops = Shop.query.filter_by(user_id=target_user.id).all()
        shops_list = [shop.to_serialize() for shop in user_shops]
        response = {
            "_success": "success",
            "shops": shops_list
        }
        return make_response(jsonify(response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


