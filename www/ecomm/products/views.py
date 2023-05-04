import os

from flask import Blueprint, render_template, request, redirect, url_for, session, g, make_response, jsonify, flash, abort
from flask_login import current_user
from sqlalchemy import desc

from configs import db
from configs.config import BASE_DIR
from www.accounts.models import User, Profile
from www.commons.required import login_required
from www.commons.utils import c_orm_id, view_count_save, single_img_save, slugify, img_delete, new_one_obj_multiple_image_save, existing_one_obj_multiple_image_save,\
    unused_sunimage_delete, sun_image_delete, existing_req_data_check, error_400_json_data, error_401_json_data, one_obj_multiple_image_delete
from www.ecomm.products.forms import ProductCategoryForm, ShopForm, ProductForm
from www.ecomm.products.models import Shop, Product, ProductCategory, ProductOption, ProductSunImage, ProductReview, ProductReviewImage, ProductQuestion, QUESTION_TYPES, ProductAnswer
from www.ecomm.products.required import vendor_required, product_ownership_required

NAME = 'products'
products = Blueprint(NAME, __name__, url_prefix='/ecomm/products')

PRODUCT_PER_PAGE = 2


@products.route('/existing/shop/title/check/ajax', methods=['POST'])
@login_required
def existing_shop_title_check_ajax():
    user_id = request.form.get("user_id")  # 이용자단 등록/수정, 어드민단의 change
    _user_email = request.form.get("user_email")  # 어드민단의 create

    req_title = request.form.get("title")
    shop_id = request.form.get("shop_id")
    target_shop = db.session.query(Shop).filter_by(id=shop_id).first()
    existing_title_shop = Shop.query.filter_by(title=req_title).first()
    if shop_id == "create":
        if user_id:  # 이용자단의 create
            target_user = User.query.filter_by(id=user_id).first()
            if (current_user == target_user) or current_user.is_admin:
                _type = "상점이름"
                flash_message = existing_req_data_check(_type, req_title, existing_title_shop, None, None)
                return flash_message
            else:
                flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                return make_response(jsonify(flash_message))
        elif _user_email:  # 어드민단의 create
            _target_user = User.query.filter_by(email=_user_email).first()
            if _target_user:
                if current_user.is_admin:
                    _type = "상점이름"
                    flash_message = existing_req_data_check(_type, req_title, existing_title_shop, None, None)
                    return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
            else:
                flash_message = {"flash_message": "유효하지 않은 요청(Error 400)", }
                return make_response(jsonify(flash_message))
        else:  # 어드민단의 create 시에 회원 선택하지 않은 경우
            flash_message = {"flash_message": "Shop 등록을 위한 회원정보가 없네요!(Error 404)", }
            return make_response(jsonify(flash_message))
    else:
        if target_shop:
            target_user = User.query.filter_by(id=user_id).first()
            if target_user:  # 이용자단, 어드민단의 change
                if (current_user == target_user) or current_user.is_admin:
                    _type = "상점이름"
                    flash_message = existing_req_data_check(_type, req_title, existing_title_shop, target_shop, target_shop.title)
                    return flash_message
                else:
                    flash_message = {"flash_message": "자격없는 접근(Error 401)", }
                    return make_response(jsonify(flash_message))
            else:
                flash_message = {"flash_message": "Shop 등록을 위한 회원정보가 없네요!(Error 404)", }
                return make_response(jsonify(flash_message))
        else:
            flash_message = {"flash_message": "해당 Shop이 없는 유효하지 않은 요청(Error 400)", }
            return make_response(jsonify(flash_message))


@products.route('/shop/save/ajax', methods=['POST'])
def shop_save_ajax():
    req_user_id = request.form.get("user_id")  # 이용자 단 create, update, 어드민단 change
    shop_id = request.form.get("shop_id")  # 이용자 단, 어드민단 change
    user_email = request.form.get("user_email")  # 어드민단 create

    title = request.form.get('title')
    content = request.form.get('content')
    symbol_image = request.files.get("symbol_image")
    cover_image_1 = request.files.get("cover_image_1")
    cover_image_2 = request.files.get("cover_image_2")
    cover_image_3 = request.files.get("cover_image_3")
    cover_image_4 = request.files.get("cover_image_4")
    cover_image_5 = request.files.get("cover_image_5")
    cover_image_6 = request.files.get("cover_image_6")
    available_display = request.form.get("available_display")
    symbol_path = f"shops/symbol_images"
    cover_path = f"shops/cover_images"
    existing_title_shop = Shop.query.filter_by(title=title).first()

    category_title = request.form.getlist("category_title")
    category_available_display = request.form.getlist("category_available_display")

    if current_user.is_admin and "admin" in request.referrer:
        if shop_id == "create":
            if existing_title_shop:
                flash("동일한 상점이름이 있습니다.")
                return redirect(request.referrer)
            if user_email:
                target_user = User.query.filter_by(email=user_email).first()
                new_shop = new_shop_save_snippet(target_user.id, title, content, symbol_image, symbol_path, target_user,
                                                 cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6,
                                                 cover_path, available_display)

                for idx in range(len(category_title)):
                    admin_new_product_category_save(target_user.id, new_shop.id, category_title, idx, category_available_display)

                flash("Shop 등록이 완료되었습니다.")
                return redirect(url_for("admin_ecomms.shop_change", _id=new_shop.id))
            else:
                flash("회원 선택이 되지 않았습니다.")
                return redirect(request.referrer)
        else:
            target_shop = Shop.query.filter_by(id=shop_id).first()
            target_user = User.query.get_or_404(target_shop.user_id)
            if str(target_shop.user_id) == req_user_id:
                if existing_title_shop:
                    if existing_title_shop != target_shop:
                        flash("동일한 상점이름이 있습니다.")
                        return redirect(request.referrer)
                target_shop_save_snippet(target_shop, title, content, symbol_image, symbol_path, target_user,
                                         cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6,
                                         cover_path, available_display, req_user_id)

                for idx in range(len(category_title)):
                    admin_new_product_category_save(req_user_id, shop_id, category_title, idx, category_available_display)

                flash("Shop 수정이 완료되었습니다.")
                return redirect(url_for("admin_ecomms.shop_change", _id=shop_id))
            else:
                flash("자격없는 요청이거나 잘못된 접근(400)")
                return redirect(request.referrer)
    elif req_user_id:
        if str(current_user.id) == req_user_id:
            if shop_id == "create":
                if int(req_user_id) == current_user.id:
                    if existing_title_shop:
                        _response = {"flash_message": "동일한 상정이름이 있습니다."}
                        return make_response(jsonify(_response))
                    req_user = User.query.filter_by(id=req_user_id).first()
                    new_shop = new_shop_save_snippet(req_user_id, title, content, symbol_image, symbol_path, req_user,
                                                     cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6,
                                                     cover_path, available_display)

                    _type = "create"
                    _response = {
                        "_save": _type,
                        "_id": new_shop.id,
                        "slug": new_shop.slug,
                        "redirect_url": url_for("products.shop_detail", _id=new_shop.id, slug=new_shop.slug),
                    }
                    return make_response(jsonify(_response))
                else:
                    data = error_400_json_data()
                    return make_response(jsonify(data))
            else:
                target_shop = Shop.query.filter_by(id=shop_id).first()
                target_user = User.query.filter_by(id=target_shop.user_id).first()
                if (current_user == target_user) and (int(req_user_id) == target_user.id):
                    if existing_title_shop:
                        if existing_title_shop != target_shop:
                            _response = {"flash_message": "동일한 상점이름이 있습니다."}
                            return make_response(jsonify(_response))
                    target_shop_save_snippet(target_shop, title, content, symbol_image, symbol_path, target_user,
                                             cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6,
                                             cover_path, available_display, req_user_id)
                    _type = "update"
                    _response = {
                        "_save": _type,
                        "_id": target_shop.id,
                        "slug": target_shop.slug,
                        "redirect_url": url_for("products.shop_detail", _id=target_shop.id, slug=target_shop.slug),
                    }
                    return make_response(jsonify(_response))
                else:
                    data = error_401_json_data()
                    return make_response(jsonify(data))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


def new_shop_save_snippet(req_user_id, title, content, symbol_image, symbol_path, req_user,
                          cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6,
                          cover_path, available_display):
    new_shop = Shop(user_id=req_user_id, title=title)
    new_shop.content = content

    if symbol_image:
        single_img_save(new_shop, symbol_path, symbol_image, req_user, None)

    images = [cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6]
    for idx, image in enumerate(images):
        new_one_obj_multiple_image_save(new_shop, image, cover_path, req_user, idx + 1)
    available_display_save(available_display, new_shop, req_user_id)

    db.session.add(new_shop)
    db.session.commit()
    return new_shop


def target_shop_save_snippet(target_shop, title, content, symbol_image, symbol_path, target_user,
                             cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5,
                             cover_image_6, cover_path, available_display, req_user_id):
    target_shop.title = title
    target_shop.slug = slugify(title, allow_unicode=True)
    target_shop.content = content

    if symbol_image:
        single_img_save(target_shop, symbol_path, symbol_image, target_user, None)

    images = [cover_image_1, cover_image_2, cover_image_3, cover_image_4, cover_image_5, cover_image_6]
    for idx, image in enumerate(images):
        existing_one_obj_multiple_image_save(target_shop, image, cover_path, target_user, idx + 1)

    available_display_save(available_display, target_shop, req_user_id)

    db.session.add(target_shop)
    db.session.commit()


def available_display_save(available_display, target_shop, req_user_id):
    # form save check ==> (on), check X ==> None
    # Ajax save check ==> true, check X ==> false
    if current_user.is_admin and "admin" in request.referrer:
        if available_display is not None:
            target_shop.available_display = True
        else:
            target_shop.available_display = False
    elif req_user_id:
        if available_display == "true":
            target_shop.available_display = True
        else:
            target_shop.available_display = False


def admin_new_product_category_save(req_user_id, shop_id, category_title, idx, category_available_display):
    new_category = ProductCategory(user_id=req_user_id, shop_id=shop_id)
    new_category.title = category_title[idx]
    if str(idx) in category_available_display:  # form POST action="{{...}}" 로 보낼때
        new_category.available_display = True
    else:
        new_category.available_display = False
    db.session.add(new_category)
    db.session.commit()


@products.route('/shop/cover_images/check/ajax', methods=['POST'])
def shop_cover_image_check_ajax():
    """기존 커버이미지 삭제전에 체크"""
    req_user_id = request.form.get("user_id")
    shop_id = request.form.get("shop_id")
    img_path_1 = request.form.get("cover_image_1")
    img_path_2 = request.form.get("cover_image_2")
    img_path_3 = request.form.get("cover_image_3")
    img_path_4 = request.form.get("cover_image_4")
    img_path_5 = request.form.get("cover_image_5")
    img_path_6 = request.form.get("cover_image_6")

    target_shop = Shop.query.filter_by(id=shop_id).first()
    target_user = User.query.filter_by(id=target_shop.user_id).first()

    if (current_user == target_user) and (int(req_user_id) == target_user.id):

        if img_path_1:
            old_image_abs_path = os.path.join(BASE_DIR, "www/" + img_path_1)
            if os.path.isfile(old_image_abs_path):
                print(os.path.isfile(old_image_abs_path))
                return make_response(jsonify({"_checked": "OK"}))
        if img_path_2:
            old_image_abs_path = os.path.join(BASE_DIR, "www/" + img_path_2)
            if os.path.isfile(old_image_abs_path):
                print(os.path.isfile(old_image_abs_path))
                return make_response(jsonify({"_checked": "OK"}))
        if img_path_3:
            old_image_abs_path = os.path.join(BASE_DIR, "www/" + img_path_3)
            if os.path.isfile(old_image_abs_path):
                print(os.path.isfile(old_image_abs_path))
                return make_response(jsonify({"_checked": "OK"}))
        if img_path_4:
            old_image_abs_path = os.path.join(BASE_DIR, "www/" + img_path_4)
            if os.path.isfile(old_image_abs_path):
                print(os.path.isfile(old_image_abs_path))
                return make_response(jsonify({"_checked": "OK"}))
        if img_path_5:
            old_image_abs_path = os.path.join(BASE_DIR, "www/" + img_path_5)
            if os.path.isfile(old_image_abs_path):
                print(os.path.isfile(old_image_abs_path))
                return make_response(jsonify({"_checked": "OK"}))
        if img_path_6:
            old_image_abs_path = os.path.join(BASE_DIR, "www/" + img_path_6)
            if os.path.isfile(old_image_abs_path):
                print(os.path.isfile(old_image_abs_path))
                return make_response(jsonify({"_checked": "OK"}))
    return make_response(jsonify({"_checked": "OOPS"}))


@products.route('/shop/cover_images/delete/ajax', methods=['POST'])
def shop_cover_image_delete_ajax():
    """이용자단에서 1개씩 삭제할때 사용"""
    req_user_id = request.form.get("user_id")
    shop_id = request.form.get("shop_id")
    img_path_1 = request.form.get("cover_image_1")
    img_path_2 = request.form.get("cover_image_2")
    img_path_3 = request.form.get("cover_image_3")
    img_path_4 = request.form.get("cover_image_4")
    img_path_5 = request.form.get("cover_image_5")
    img_path_6 = request.form.get("cover_image_6")

    target_shop = Shop.query.filter_by(id=shop_id).first()
    target_user = User.query.filter_by(id=target_shop.user_id).first()
    if (current_user == target_user) and (int(req_user_id) == target_user.id):
        if img_path_1:
            img_delete(target_shop.img_path_1)
            target_shop.img_path_1 = None
        if img_path_2:
            img_delete(target_shop.img_path_2)
            target_shop.img_path_2 = None
        if img_path_3:
            img_delete(target_shop.img_path_3)
            target_shop.img_path_3 = None
        if img_path_4:
            img_delete(target_shop.img_path_4)
            target_shop.img_path_4 = None
        if img_path_5:
            img_delete(target_shop.img_path_5)
            target_shop.img_path_5 = None
        if img_path_6:
            img_delete(target_shop.img_path_6)
            target_shop.img_path_6 = None
    db.session.add(target_shop)
    db.session.commit()
    shop_response = {"flash_message": "삭제 선택한 커버이미지가 삭제되었습니다."}
    return make_response(jsonify(shop_response))


@products.route('/shop/delete/ajax', methods=['POST'])
def shop_delete_ajax():
    """symbol_path and cover_image_path 둘다 삭제해야 한다."""
    req_user_id = request.form.get("user_id")
    related_all_delete = request.form.get("related_all_delete")

    shop_id = request.form.get("shop_id")
    print("shop_id=====================", type(shop_id), shop_id)
    print("related_all_delete", related_all_delete)
    target_shop = Shop.query.filter_by(id=shop_id).first()
    target_user = User.query.filter_by(id=target_shop.user_id).first()
    target_product_objs = target_shop.product_shop_set
    if current_user.is_admin and "admin" in request.referrer:
        if target_shop:
            if related_all_delete != "undefined":
                if related_all_delete == "true":
                    if target_shop.img_path:  # symbol_path
                        img_delete(target_shop.img_path)
                    one_obj_multiple_image_delete(target_shop, 7)  # 커버이미지 6개 삭제
                    db.session.delete(target_shop)
                    for product in target_product_objs:
                        one_obj_multiple_image_delete(product, 4)  # 썸네일 3개 삭제
                        product_related_all_delete(product)
                else:
                    target_shop.available_display = False
                    for product in target_product_objs:
                        product.available_display = False
                        product.available_order = False
                        db.session.add(product)
                db.session.commit()
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for("admin_ecomms.shop_list")
                }
                return make_response(jsonify(_response))
            else:
                data = error_400_json_data()
                return make_response(jsonify(data))
        else:
            data = error_400_json_data()
            return make_response(jsonify(data))
    elif req_user_id:
        if target_shop:
            if (current_user == target_user) and (int(req_user_id) == target_user.id):
                # if target_shop.img_path:  # symbol_path
                #     img_delete(target_shop.img_path)
                # one_obj_multiple_image_delete(target_shop, 7)  # 커버이미지 6개 삭제
                # db.session.delete(target_shop)
                target_shop.available_display = False
                for product in target_product_objs:
                    product.available_display = False
                    product.available_order = False
                    db.session.add(product)
                db.session.commit()

                flash("Shop이 삭제되었습니다.")
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for("products.user_shop_list", _id=req_user_id)
                }
                return make_response(jsonify(_response))
            else:
                data = error_400_json_data()
                return make_response(jsonify(data))
        else:
            data = error_400_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/shop/detail/<_id>/<slug>', methods=['GET'])
def shop_detail(_id, slug):
    shop_form = ShopForm()
    pc_form = ProductCategoryForm()
    if _id == "create":
        if current_user.is_authenticated:
            shop = None
            target_user = "create"
            return render_template('ecomm/products/shop/detail.html',
                                   shop_form=shop_form,
                                   pc_form=pc_form,
                                   target_shop=shop,
                                   target_user=target_user)
        else:
            try:
                session['previous_url'] = request.path
            except Exception as e:
                print("login_required(function) Exception::: ", e)
                session['previous_url'] = None
            return redirect(url_for('accounts.login'))
    else:
        target_shop = Shop.query.filter_by(id=_id, slug=slug).first()
        target_user = User.query.filter_by(id=target_shop.user_id).first()
        target_categories = ProductCategory.query.filter_by(shop_id=target_shop.id).all()
        obj_str = "shop"
        view_count_save(target_user, target_shop, obj_str)

        target_user_all_products = Product.query.filter_by(user_id=target_user.id).all()
        products_query = Product.query.order_by(desc(Product.created_at)).filter_by(shop_id=target_shop.id, available_display=True)
        page = request.args.get('page', type=int, default=1)

        """######## 검색 ########"""
        kw = request.args.get('kw', type=str, default='')
        if kw:
            search = f'%%{kw}%%'  # '%%{}%%'.format(kw))
            products_query = products_query.filter(Product.title.ilike(search)).distinct()
        """######################"""
        pagination = products_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
        product_objs = pagination.items
        return render_template('ecomm/products/shop/detail.html',
                               shop_form=shop_form,
                               pc_form=pc_form,
                               target_shop=target_shop,
                               target_categories=target_categories,
                               target_user=target_user,
                               target_user_all_products=target_user_all_products,
                               target_products=product_objs,
                               pagination=pagination,
                               kw=kw)


@products.route('/all/shop/list', methods=['GET'])
def all_shop_list():
    if current_user.is_authenticated:
        shops_query = Shop.query.filter_by(available_display=True).order_by(desc(Shop.created_at)).filter(Shop.user_id != current_user.id)
    else:
        shops_query = Shop.query.filter_by(available_display=True).order_by(desc(Shop.created_at))
    page = request.args.get('page', type=int, default=1)

    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw))
        shops_query = shops_query.filter(Shop.title.ilike(search)).distinct()
    """######################"""
    pagination = shops_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
    shops = pagination.items
    return render_template('ecomm/products/shop/list.html',
                           shops=shops,
                           pagination=pagination,
                           kw=kw)


@products.route('/user/<_id>/shop/list', methods=['GET'])
def user_shop_list(_id):
    target_user = User.query.filter_by(id=_id).first()
    shops_query = Shop.query.filter_by(available_display=True).order_by(desc(Shop.created_at)).filter_by(user_id=_id)  # .all()

    page = request.args.get('page', type=int, default=1)
    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw))
        shops_query = shops_query.filter(Shop.title.ilike(search)).distinct()
    """######################"""
    pagination = shops_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
    shops = pagination.items
    return render_template('ecomm/products/shop/list.html',
                           shops=shops,
                           target_user=target_user,
                           pagination=pagination,
                           kw=kw)


@products.route('/product/category/save', methods=['POST'])
def product_category_new_save():
    req_user_id = request.form.get("user_id")
    shop_id = request.form.get("shop_id")
    target_shop = Shop.query.filter_by(id=shop_id).first()
    target_user = User.query.filter_by(id=target_shop.user_id).first()

    title = request.form.getlist("title")
    available_display = request.form.getlist("available_display")
    print(available_display)
    if req_user_id:
        if (current_user == target_user) and (int(req_user_id) == target_user.id):
            for idx in range(len(title)):
                new_category = ProductCategory(user_id=req_user_id, shop_id=shop_id)
                new_category.title = title[idx]
                if str(idx) in available_display:  # form POST action="{{...}}" 로 보낼때
                    new_category.available_display = True
                else:
                    new_category.available_display = False
                db.session.add(new_category)
                db.session.commit()
            return redirect(url_for("products.product_create", shop_id=target_shop.id, shop_title=target_shop.title, ss=target_shop.slug))
        abort(401)
    abort(400)


change_response = ""


@products.route('/product/category/change/check/ajax', methods=['POST'])
def product_category_change_check_ajax():
    category_id = request.form.get("category_id")
    check_type = request.form.get("check_type")
    target_category = ProductCategory.query.filter_by(id=category_id).first()
    if check_type == "change":
        _response = {
            "_obj": 'product_category',
            "_check": "change_check",
            "_title": target_category.title,
            "available_display": target_category.available_display
        }
        return make_response(jsonify(_response))
    elif check_type == "delete":
        _response = {
            "_obj": 'product_category',
            "_check": "delete_check",
            "user_id": target_category.user_id,
            "shop_id": target_category.shop_id,
            "category_id": target_category.id,
            "category_title": target_category.title
        }
        return make_response(jsonify(_response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/product/category/change/save/ajax', methods=['POST'])
def product_category_change_save_ajax():
    global change_response
    req_user_id = request.form.get("user_id")
    req_shop_id = request.form.get("shop_id")

    category_id = request.form.get("category_id")
    title = request.form.get("title")
    available_display = request.form.get("available_display")
    target_category = ProductCategory.query.filter_by(id=category_id).first()
    target_user = User.query.filter_by(id=target_category.user_id).first()
    if current_user.is_admin and "admin" in request.referrer and target_category:
        target_category.title = title
        print(available_display)
        if available_display == "true":
            target_category.available_display = True
        else:
            target_category.available_display = False
        db.session.add(target_category)
        db.session.commit()
        change_response = {"flash_message": f'정상적으로 카테고리가 수정되었습니다.'}
        return make_response(jsonify(change_response))
    elif req_user_id and category_id:
        if (current_user == target_user) \
                and (int(req_user_id) == target_user.id) \
                and (int(req_shop_id) == target_category.shop_id):
            if target_category.title == title:
                if target_category.available_display:
                    if available_display == "true":
                        change_response = {
                            "_obj": 'product_category',
                            "o_save": "save",
                            "flash_message": "수정된 내용이 없습니다.",
                            "_title": target_category.title,
                            "available_display": target_category.available_display
                        }
                    else:
                        target_category.available_display = False
                        db.session.add(target_category)
                        db.session.commit()
                        change_response = {
                            "_obj": 'product_category',
                            "o_save": "save",
                            "flash_message": f'"{title}" 카테고리가 "비노출"로 수정되었습니다.',
                            "_title": target_category.title,
                            "available_display": target_category.available_display
                        }
                else:
                    if available_display == "false":
                        change_response = {
                            "_obj": 'product_category',
                            "o_save": "save",
                            "flash_message": "수정된 내용이 없습니다.",
                            "_title": target_category.title,
                            "available_display": target_category.available_display
                        }
                    else:
                        target_category.available_display = True
                        db.session.add(target_category)
                        db.session.commit()
                        change_response = {
                            "_obj": 'product_category',
                            "o_save": "save",
                            "flash_message": f'"{title}" 카테고리가 "노출"로 수정되었습니다.',
                            "_title": target_category.title,
                            "available_display": target_category.available_display
                        }
            else:
                target_category.title = title
                if available_display == "true":  # true false ajax 로 보낼때
                    target_category.available_display = True
                else:
                    target_category.available_display = False
                db.session.add(target_category)
                db.session.commit()
                change_response = {
                    "_obj": 'product_category',
                    "o_save": "save",
                    "flash_message": f'"{title}" 카테고리가 수정되었습니다.',
                    "_title": target_category.title,
                    "available_display": target_category.available_display
                }
            return make_response(jsonify(change_response))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/product/category/delete/ajax', methods=['POST'])
def product_category_delete_ajax():
    req_user_id = request.form.get("user_id")
    req_shop_id = request.form.get("shop_id")

    category_id = request.form.get("category_id")
    target_category = ProductCategory.query.filter_by(id=category_id).first()
    target_user = User.query.filter_by(id=target_category.user_id).first()
    if current_user.is_admin and "admin" in request.referrer:
        db.session.delete(target_category)
        db.session.commit()
        _response = {
            "flash_message": f'"{target_category.title}" 카테고리가 삭제되었습니다.'
        }
        return make_response(jsonify(_response))
    elif (current_user == target_user) \
            and (int(req_user_id) == target_user.id) \
            and (int(req_shop_id) == target_category.shop_id):
        db.session.delete(target_category)
        db.session.commit()
        _response = {
            "flash_message": f'"{target_category.title}" 카테고리가 삭제되었습니다.'
        }
        return make_response(jsonify(_response))
    else:
        data = error_401_json_data()
        return make_response(jsonify(data))


@products.route('/product/create', methods=['GET'])
@vendor_required
def product_create():
    form = ProductForm()
    """링크에 임의로 지정한 get param 을 붙여서 넘어온다."""
    shop_id = int(request.full_path.split("?")[1].split("&")[0].split("=")[1])
    print("shop_id", shop_id)
    target_shop = Shop.query.filter_by(id=shop_id).first()
    target_user = User.query.filter_by(id=target_shop.user_id).first()
    target_profile = Profile.query.filter_by(user_id=target_shop.user_id).first()

    products_all = Product.query.all()
    orm_id = c_orm_id(products_all, g.user)

    target_categories = ProductCategory.query.filter_by(shop_id=shop_id).all()

    return render_template('ecomm/products/product/create.html',
                           form=form,
                           target_shop=target_shop,
                           target_user=target_user,
                           target_profile=target_profile,
                           target_categories=target_categories,
                           orm_id=orm_id)


@products.route('/product/save', methods=['POST'])
def product_save():
    req_user_id = request.form.get("user_id")  # 이용자단, 어드민단 change
    user_email = request.form.get("user_email")  # 어드민단 create
    shop_id = request.form.get("shop_id")
    target_shop = Shop.query.filter_by(id=shop_id).first()
    orm_id = request.form.get('orm_id')
    product_id = request.form.get("product_id")

    category_id = request.form.get("category_id")
    title = request.form.get("title")
    content = request.form.get('content')
    meta_description = request.form.get('meta_description')
    thumbnail_1 = request.files.get("image1")
    thumbnail_2 = request.files.get("image2")
    thumbnail_3 = request.files.get("image3")

    price = request.form.get('price')
    stock = request.form.get('stock')
    base_dc_amount = request.form.get('base_dc_amount')
    delivery_pay = request.form.get('delivery_pay')
    available_display = request.form.get('available_display')
    available_order = request.form.get('available_order')

    op_id = request.form.getlist("op_id")
    op_title = request.form.getlist("op_title")
    op_price = request.form.getlist('op_price')
    op_stock = request.form.getlist('op_stock')

    op_available_display = request.form.getlist('op_available_display')
    op_available_order = request.form.getlist('op_available_order')

    request_path = f"products/thumbnail_images"
    thumbnails = [thumbnail_1, thumbnail_2, thumbnail_3]

    if current_user.is_admin and "admin" in request.referrer:
        if product_id == "create":
            target_user = User.query.filter_by(email=user_email).first()
            new_product = new_product_save_snippet(target_user.id, title, shop_id, category_id, orm_id, content, meta_description, price, stock, base_dc_amount,
                                                   delivery_pay, available_display, available_order, thumbnails, request_path, target_user)
            for idx in range(len(op_title)):
                new_product_option_save_snippet(new_product, target_user, idx, op_title, op_price, op_stock, op_available_display, op_available_order)
            if (not new_product.img_path_1) or (not new_product.img_path_2) or (not new_product.img_path_3):
                flash('대표이미지 3개를 모두 업로드해주세요.')
            flash("아티클 등록이 완료되었습니다.")
            return redirect(url_for('admin_ecomms.product_change', _id=new_product.id))
        else:
            print("existing Product")
            target_product = Product.query.filter_by(id=product_id).first()
            target_options = ProductOption.query.filter_by(product_id=product_id).all()
            target_user = User.query.get_or_404(target_product.user_id)
            if str(target_product.user_id) == req_user_id:
                target_product_save_snippet(target_product, title, category_id, content, meta_description, price, stock, base_dc_amount, delivery_pay,
                                            available_display, available_order, thumbnails, request_path, target_user)

                used_options = []
                for idx in range(len(op_title)):
                    if op_id[idx] == "none":
                        new_product_option_save_snippet(target_product, g.user, idx, op_title, op_price, op_stock, op_available_display, op_available_order)

                    else:
                        option_obj = target_product_option_save_snippet(idx, op_id, op_title, op_price, op_stock, op_available_display, op_available_order)
                        used_options.append(option_obj)
                try:
                    unused_options = set(target_options) - set(used_options)
                    if unused_options:
                        for unused_option in unused_options:
                            db.session.delete(unused_option)
                            db.session.commit()
                except Exception as e:
                    print('productoption update exception error::', e)

                """ # 저장후에 content 의 src 를, DB와 비교해서, DB 에 있으나 content 에는 없는 image(file, path)를 삭제"""
                db_img_objs_all = target_product.sunimage_product_set
                unused_sunimage_delete(db_img_objs_all, target_product, ProductSunImage)
                if (not target_product.img_path_1) or (not target_product.img_path_2) or (not target_product.img_path_3):
                    flash('대표이미지 3개를 모두 업로드해주세요.')
                flash("상품 수정이 완료되었습니다.")
                return redirect(request.referrer)
            else:
                flash("자격없는 요청이거나 잘못된 접근(400)")
                return redirect(request.referrer)
    elif req_user_id:
        if product_id:
            target_product = Product.query.filter_by(id=product_id).first()
            target_options = ProductOption.query.filter_by(product_id=product_id).all()
            target_user = User.query.filter_by(id=target_product.user_id).first()
            if current_user != target_user:
                flash('수정권한이 없습니다')
                return redirect(url_for('products.product_detail', _id=target_product.id, slug=target_product.slug))
            if (current_user == target_user) and (int(req_user_id) == target_user.id):
                target_product_save_snippet(target_product, title, category_id, content, meta_description, price, stock, base_dc_amount, delivery_pay,
                                            available_display, available_order, thumbnails, request_path, current_user)

                used_options = []
                for idx in range(len(op_title)):
                    if op_id[idx] == "none":
                        new_product_option_save_snippet(target_product, g.user, idx, op_title, op_price, op_stock, op_available_display, op_available_order)

                    else:
                        option_obj = target_product_option_save_snippet(idx, op_id, op_title, op_price, op_stock, op_available_display, op_available_order)
                        used_options.append(option_obj)
                try:
                    unused_options = set(target_options) - set(used_options)
                    if unused_options:
                        for unused_option in unused_options:
                            db.session.delete(unused_option)
                            db.session.commit()
                except Exception as e:
                    print('productoption update exception error::', e)

                """ # 저장후에 content 의 src 를, DB와 비교해서, DB 에 있으나 content 에는 없는 image(file, path)를 삭제"""
                db_img_objs_all = target_product.sunimage_product_set
                unused_sunimage_delete(db_img_objs_all, target_product, ProductSunImage)
                if (not target_product.img_path_1) or (not target_product.img_path_2) or (not target_product.img_path_3):
                    flash('대표이미지 3개를 모두 업로드해주세요.')
                return redirect(url_for("products.product_detail", _id=target_product.id, slug=target_product.slug))
            else:
                abort(400)
        else:
            if int(req_user_id) == current_user.id:
                new_product = new_product_save_snippet(req_user_id, title, shop_id, category_id, orm_id, content, meta_description, price, stock, base_dc_amount,
                                                       delivery_pay, available_display, available_order, thumbnails, request_path, current_user)
                for idx in range(len(op_title)):
                    new_product_option_save_snippet(new_product, g.user, idx, op_title, op_price, op_stock, op_available_display, op_available_order)
                if (not new_product.img_path_1) or (not new_product.img_path_2) or (not new_product.img_path_3):
                    flash('대표이미지 3개를 모두 업로드해주세요.')
                return redirect(url_for("products.product_detail", _id=new_product.id, slug=new_product.slug))
            else:
                abort(401)
    else:
        abort(400)


def new_product_save_snippet(req_user_id, title, shop_id, category_id, orm_id, content, meta_description, price, stock, base_dc_amount,
                             delivery_pay, available_display, available_order, thumbnails, request_path, user):
    new_product = Product(user_id=req_user_id, title=title)
    new_product.shop_id = shop_id
    if category_id:
        new_product.pc_id = category_id
    new_product.orm_id = orm_id
    new_product.content = content
    new_product.meta_description = meta_description
    new_product.price = price
    new_product.stock = stock
    new_product.base_dc_amount = base_dc_amount
    new_product.delivery_pay = delivery_pay

    if available_display is not None:
        new_product.available_display = True
    else:
        new_product.available_display = False

    if available_order is not None:
        new_product.available_order = True
    else:
        new_product.available_order = False

    for idx, image in enumerate(thumbnails):
        new_one_obj_multiple_image_save(new_product, image, request_path, user, idx + 1)

    db.session.add(new_product)
    db.session.commit()
    return new_product


def target_product_save_snippet(target_product, title, category_id, content, meta_description, price, stock, base_dc_amount, delivery_pay,
                                available_display, available_order, thumbnails, request_path, user):
    target_product.title = title
    if category_id:
        target_product.pc_id = category_id
    target_product.content = content
    target_product.meta_description = meta_description
    target_product.price = price
    target_product.stock = stock
    target_product.base_dc_amount = base_dc_amount
    target_product.delivery_pay = delivery_pay

    if available_display is not None:
        target_product.available_display = True
    else:
        target_product.available_display = False

    if available_order is not None:
        target_product.available_order = True
    else:
        target_product.available_order = False

    for idx, image in enumerate(thumbnails):
        existing_one_obj_multiple_image_save(target_product, image, request_path, user, idx + 1)

    db.session.add(target_product)
    db.session.commit()


def new_product_option_save_snippet(product, user, idx, op_title, op_price, op_stock, op_available_display, op_available_order):
    new_option = ProductOption(
        user_id=user.id,
        title=op_title[idx]
    )
    new_option.product_id = product.id
    new_option.price = op_price[idx]
    new_option.stock = op_stock[idx]

    if str(idx) in op_available_display:
        new_option.available_display = True
    else:
        new_option.available_display = False

    if str(idx) in op_available_order:
        new_option.available_order = True
    else:
        new_option.available_order = False
    db.session.bulk_save_objects([new_option])
    db.session.commit()


def target_product_option_save_snippet(idx, op_id, op_title, op_price, op_stock, op_available_display, op_available_order):
    option_obj = ProductOption.query.get_or_404(op_id[idx])
    option_obj.title = op_title[idx]
    option_obj.price = op_price[idx]
    option_obj.stock = op_stock[idx]

    if str(idx) in op_available_display:
        option_obj.available_display = True
    else:
        option_obj.available_display = False

    if str(idx) in op_available_order:
        option_obj.available_order = True
    else:
        option_obj.available_order = False
    db.session.bulk_save_objects([option_obj])
    db.session.commit()
    return option_obj


@products.route('/shop/select/ajax', methods=['POST'])
def shop_select_ajax():
    shop_id = request.form.get("shop_id")
    target_shop = User.query.filter_by(id=shop_id).first()
    _type = request.form.get("type")
    if _type == "admin_product_create":
        product_categories = ProductCategory.query.filter_by(shop_id=shop_id).all()
        categories_list = [category.to_serialize() for category in product_categories]
        response = {
            "_success": "success",
            "categories": categories_list
        }
        return make_response(jsonify(response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/product/update/<int:_id>/<slug>', methods=['GET'])
@product_ownership_required
def product_update(_id, slug):
    target_product = Product.query.filter_by(id=_id, slug=slug).first()
    target_options = ProductOption.query.filter_by(product_id=target_product.id).all()
    target_shop = Shop.query.filter_by(id=target_product.shop_id).first()
    if target_shop:
        target_categories = ProductCategory.query.filter_by(shop_id=target_shop.id).all()
    else:
        target_categories = None
    target_user = User.query.filter_by(id=target_product.user_id).first()
    target_profile = Profile.query.filter_by(user_id=target_product.user_id).first()

    orm_id = target_product.orm_id
    form = ProductForm()
    return render_template('ecomm/products/product/update.html', form=form,
                           target_user=target_user,
                           target_profile=target_profile,
                           target_product=target_product,
                           target_options=target_options,
                           target_shop=target_shop,
                           target_categories=target_categories,
                           orm_id=orm_id)


@products.route('/product/delete/ajax', methods=['POST'])
def product_delete_ajax():
    product_id = request.form.get("_id")
    req_user_id = request.form.get("user_id")  # 이용자단
    related_all_delete = request.form.get("related_all_delete")
    target_product = Product.query.get_or_404(product_id)
    target_shop = Shop.query.filter_by(id=target_product.shop_id).first()
    target_user = User.query.filter_by(id=target_product.user_id).first()
    if target_product:
        if current_user.is_admin and "admin" in request.referrer:
            if related_all_delete != "undefined":
                if related_all_delete == "true":
                    one_obj_multiple_image_delete(target_product, 4)  # 썸네일 3개 삭제
                    product_related_all_delete(target_product)
                    """product_sunimage, product_option, product_review 들의 db table 은 삭제하지 않아도,
                         한꺼번에 삭제된다.(model 에 cascade='all, delete-orphan' 설정때문에) 
                         그러나,db 에 저장된 실제 product의 sunimage와 dropzone으로 올린 review의 image 들은 직접 삭제해줘야 한다."""
                    db.session.commit()
                    _response = {
                        "_success": "success",
                        "_delete": "delete",
                        "redirect_url": url_for('admin_ecomms.product_list')
                    }
                    return make_response(jsonify(_response))
                else:
                    target_product.available_display = False
                    target_product.available_order = False
                    db.session.add(target_product)
                    db.session.commit()
                    _response = {
                        "_success": "success",
                        "_delete": "delete",
                        "redirect_url": url_for('admin_ecomms.product_change', _id=target_product.id)
                    }
                    return make_response(jsonify(_response))
            else:
                data = error_400_json_data()
                return make_response(jsonify(data))
        elif (current_user == target_user) and (int(req_user_id) == target_user.id):
            target_product.available_display = False
            target_product.available_order = False
            db.session.add(target_product)
            db.session.commit()

            if target_shop:
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for('products.shop_detail', _id=target_shop.id, slug=target_shop.slug)
                }
            else:  # # target_shop 이 먼저 삭제된 경우
                _response = {
                    "_success": "success",
                    "_delete": "delete",
                    "redirect_url": url_for('products.user_product_list', _id=target_user.id)
                }
            return make_response(jsonify(_response))
        else:
            data = error_401_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


def product_related_all_delete(product):
    existing_sunimages = product.sunimage_product_set
    if existing_sunimages:
        sun_image_delete(existing_sunimages)
    existing_reviews = product.productreview_product_set
    for review in existing_reviews:
        review_images = review.productreview_image_set  # dropzone images
        for image in review_images:
            try:
                img_delete(image.img_path)
            except Exception as e:
                print(e)
            db.session.delete(image)
            db.session.commit()
    db.session.delete(product)


@products.route('/product/detail/<int:_id>/<slug>', methods=['GET'])
@login_required
def product_detail(_id, slug):
    target_product = Product.query.filter_by(id=_id).first()

    # target_product_reviews = ProductReview.query.filter_by(product_id=target_product.id).all()
    target_product_review_query = ProductReview.query.order_by(desc(ProductReview.created_at)).filter_by(product_id=target_product.id)  # .all()
    page = request.args.get('page', type=int, default=1)
    pagination = target_product_review_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
    target_product_reviews = pagination.items

    target_options = ProductOption.query.filter_by(product_id=target_product.id).all()
    target_shop = Shop.query.filter_by(id=target_product.shop_id).first()
    target_category = ProductCategory.query.filter_by(id=target_product.pc_id).first()

    # target_questions = target_product.productquestion_product_set
    target_question_query = ProductQuestion.query.order_by(desc(ProductQuestion.created_at)).filter_by(product_id=target_product.id)
    page_2 = request.args.get('page_2', type=int, default=1)
    pagination_2 = target_question_query.paginate(page=page_2, per_page=PRODUCT_PER_PAGE, error_out=False)
    target_questions = pagination_2.items

    target_user = User.query.filter_by(id=target_product.user_id).first()
    target_profile = Profile.query.filter_by(user_id=target_product.user_id).first()

    res_msg = request.args.get("res_msg")
    if res_msg:
        flash(res_msg)
    return render_template('ecomm/products/product/detail.html',
                           target_product=target_product,

                           target_product_reviews=target_product_reviews,
                           pagination=pagination,
                           page_obj="review",
                           question_types=QUESTION_TYPES,
                           target_questions=target_questions,
                           pagination_2=pagination_2,
                           page_obj_2="question",

                           target_options=target_options,
                           target_shop=target_shop,
                           target_category=target_category,
                           target_user=target_user,
                           target_profile=target_profile)


@products.route('/all/product/list', methods=['GET'])
def all_product_list():
    if current_user.is_authenticated:
        products_query = Product.query.filter_by(available_display=True).order_by(desc(Product.created_at)).filter(Product.user_id != current_user.id)
    else:
        products_query = Product.query.filter_by(available_display=True).order_by(desc(Product.created_at))
    page = request.args.get('page', type=int, default=1)

    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    print(kw)
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw))
        products_query = products_query.filter(Product.title.ilike(search)).distinct()
    """######################"""
    pagination = products_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
    product_objs = pagination.items
    return render_template('ecomm/products/product/list.html',
                           products=product_objs,
                           pagination=pagination,
                           kw=kw)


@products.route('/user/<_id>/product/list', methods=['GET'])
def user_product_list(_id):
    target_user = User.query.filter_by(id=_id).first()
    products_query = Product.query.order_by(desc(Product.created_at)).filter_by(user_id=_id, available_display=True)
    page = request.args.get('page', type=int, default=1)

    """######## 검색 ########"""
    kw = request.args.get('kw', type=str, default='')
    print(kw)
    if kw:
        search = f'%%{kw}%%'  # '%%{}%%'.format(kw))
        products_query = products_query.filter(Product.title.ilike(search)).distinct()
    """######################"""
    pagination = products_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
    product_objs = pagination.items
    return render_template('ecomm/products/product/list.html',
                           products=product_objs,
                           target_user=target_user,
                           pagination=pagination,
                           kw=kw)


@products.route('/category/product/list', methods=['GET'])
def category_product_list():
    shop_form = ShopForm()
    pc_form = ProductCategoryForm()
    shop_id = request.args.get("shop_id")
    category_id = request.args.get("category_id")
    target_category = ProductCategory.query.filter_by(id=category_id).first()
    target_shop = Shop.query.filter_by(id=shop_id).first()
    target_categories = ProductCategory.query.filter_by(shop_id=target_shop.id).all()
    target_user = User.query.filter_by(id=target_shop.user_id).first()
    products_query = Product.query.order_by(desc(Product.created_at)).filter_by(pc_id=category_id)
    page = request.args.get('page', type=int, default=1)
    pagination = products_query.paginate(page=page, per_page=PRODUCT_PER_PAGE, error_out=False)
    product_objs = pagination.items
    return render_template('ecomm/products/shop/detail.html',
                           shop_form=shop_form,
                           pc_form=pc_form,
                           target_shop=target_shop,
                           target_category=target_category,
                           target_categories=target_categories,
                           target_user=target_user,
                           target_products=product_objs,
                           pagination=pagination)


subs_response = ""


@products.route('/shop/subscribe/ajax', methods=['POST'])
@login_required
def shop_subscribe_ajax():
    global subs_response
    _id = request.form.get("shop_id")
    req_email = request.form.get("user_email")  # 어드민단
    target_shop = Shop.query.get_or_404(_id)
    if current_user.is_admin and "admin" in request.referrer:
        admin_req_user = User.query.filter_by(email=req_email).first()
        if target_shop.user == admin_req_user:
            flash("작성자는 구독할수 없습니다")
        else:
            target_shop.subscribers.append(admin_req_user)
            db.session.commit()
            flash("구독자가 추가 되었습니다.")
        subs_response = {"admin_success": "admin success",
                         "redirect_url": url_for('admin_ecomms.shop_subscriber_list', _id=target_shop.id)}
        return make_response(jsonify(subs_response))
    elif g.user == target_shop.user:
        subs_response = {"checked_message": "본인의 Shop은 구독할수 없습니다"}
        return make_response(jsonify(subs_response))
    else:
        if current_user in target_shop.subscribers:
            subs_response = {"checked_message": "이미 구독하고 계세요!"}
        else:
            target_shop.subscribers.append(g.user)
            db.session.commit()
            subscribe_count = len(target_shop.subscribers)
            subs_response = {"flash_message": '오! 구독하셨네요. 감사합니다!',
                             "subscribe_count": subscribe_count}
        return make_response(jsonify(subs_response))


@products.route('/shop/subscribe/cancel/ajax', methods=['POST'])
@login_required
def shop_subscribe_cancel_ajax():
    global subs_response
    shop_id = request.form.get("shop_id")
    user_id = request.form.get("user_id")  # 어드민단
    target_shop = Shop.query.get_or_404(shop_id)
    if current_user.is_admin and "admin" in request.referrer:
        target_user = User.query.filter_by(id=user_id).first()
        target_shop.subscribers.remove(target_user)
        db.session.commit()
        subs_response = {
            "admin_success": "admin success",
            "redirect_url": url_for('admin_ecomms.shop_subscriber_list', _id=target_shop.id)
        }
    else:
        if current_user in target_shop.subscribers:
            target_shop.subscribers.remove(g.user)
            db.session.commit()
            subscribe_count = len(target_shop.subscribers)
            subs_response = {
                "flash_message": "그동안 구독해주셔서 감사해요!",
                "subscribe_count": subscribe_count
            }
        else:
            subs_response = {"no_auth_message": "구독했던 유저만 취소가 가능해요!"}
    return make_response(jsonify(subs_response))


vote_response = ""


@products.route('/product/vote/ajax', methods=['POST'])
@login_required
def product_vote_ajax():
    global vote_response
    _id = request.form.get("product_id")
    req_email = request.form.get("user_email")  # 어드민단
    target_product = Product.query.get_or_404(_id)
    if current_user.is_admin and "admin" in request.referrer:
        admin_req_user = User.query.filter_by(email=req_email).first()
        if target_product.user == admin_req_user:
            flash("작성자는 추천할수 없습니다")
        else:
            target_product.voters.append(admin_req_user)
            db.session.commit()
            flash("추천인이 추가 되었습니다.")
        vote_response = {"admin_success": "admin success",
                         "redirect_url": url_for('admin_ecomms.product_voter_list', _id=target_product.id)}
        return make_response(jsonify(vote_response))
    elif g.user == target_product.user:
        vote_response = {"checked_message": "본인이 작성한 글은 추천할수 없습니다"}
        return make_response(jsonify(vote_response))
    else:
        if current_user in target_product.voters:
            vote_response = {"checked_message": "이미 추천하고 계세요!"}
        else:
            target_product.voters.append(g.user)
            db.session.commit()
            vote_count = len(target_product.voters)
            vote_response = {"flash_message": "오! 추천하셨군요. 감사합니다!",
                             "vote_count": vote_count}
        return make_response(jsonify(vote_response))


@products.route('/product/vote/cancel/ajax', methods=['POST'])
@login_required
def product_vote_cancel_ajax():
    global vote_response
    product_id = request.form.get("product_id")
    print(product_id)
    user_id = request.form.get("user_id")  # 어드민단
    target_product = Product.query.get_or_404(product_id)
    if current_user.is_admin and "admin" in request.referrer:
        target_user = User.query.filter_by(id=user_id).first()
        target_product.voters.remove(target_user)
        db.session.commit()
        vote_response = {
            "admin_success": "admin success",
            "redirect_url": url_for('admin_ecomms.product_voter_list', _id=target_product.id)
        }
    else:
        if current_user in target_product.voters:
            target_product.voters.remove(g.user)
            db.session.commit()
            vote_count = len(target_product.voters)
            vote_response = {
                "flash_message": "그동안 추천해주셔서 감사해요!",
                "vote_count": vote_count
            }
        else:
            vote_response = {"checked_count": "추천했던 유저만 취소가 가능해요!"}
    return make_response(jsonify(vote_response))


@products.route('/product/option/ajax', methods=['POST'])
def option_select_ajax():
    _id = request.form.get("_id")
    _get = request.form.get("_get")
    option = ProductOption.query.filter_by(id=_id).first()
    if option and _get and (_get == "get_option"):
        option_data_response = {
            "_id": option.id,
            "pd_id": option.product_id,
            "_title": option.title,
            "_price": option.price,
        }
        return make_response(jsonify(option_data_response))
    elif _get is None:
        option_data_response = {
            "_data_r": "data",
        }
        return make_response(jsonify(option_data_response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/product/review/save', methods=['POST'])
@login_required
def product_review_save():
    current_path = request.form.get("current_path")
    print(current_path)

    user_id = request.form.get("user_id")
    product_id = request.form.get("product_id")
    review_id = request.form.get("review_id")
    print(review_id)
    existing_image_ids = request.form.getlist("image_id")  # 기존 이미지에서 취소 버튼을 눌러 tag 를 remove 하고 남은 id 들
    # images = request.files.getlist("image")  # 기존 이미지를 변경한 것과 새로운 이미지들 모두...
    content = request.form.get("content")
    target_product = Product.query.filter_by(id=product_id).first()
    request_path = "products/review_images"
    ###########################################
    file_dict_lists = list(request.files.listvalues())
    images = request.files.to_dict().values()
    # dropzone 에서 다발로 넘어온 파일들은 ImmutableMultiDict 이라 이것을 딕셔너리로 바꾸고, 그것도 value 만을 리스트로 바꾼다.

    target_user = User.query.filter_by(id=target_product.user_id).first()

    if review_id:
        target_review = ProductReview.query.filter_by(id=review_id).first()
        if (current_user.is_admin and "admin" in request.referrer) or (current_user == target_review.user):
            target_review.content = content
            db.session.add(target_review)
            if images:
                for image in images:
                    new_dz_image = ProductReviewImage(user_id=target_user.id, product_id=product_id, review_id=review_id)
                    single_img_save(new_dz_image, request_path, image, target_user, image.filename)
                    g.db.add(new_dz_image)
            db.session.commit()

            if current_user.is_admin and "admin" in request.referrer:
                print("admin")
                board_response = {
                    "_success": "success",
                    "flash_message": "보드 수정성공",
                    "redirect_url": url_for("admin_ecomms.product_review_change", _id=review_id),
                    # "redirect_url": current_path
                }
                return make_response(jsonify(board_response))
            else:
                print("user")
                board_response = {
                    "_success": "success",
                    "flash_message": "보드 수정성공",
                    "redirect_url": current_path + f'#board_{str(target_review.id)}',
                }
                return make_response(jsonify(board_response))
        else:
            print("400")
            data = error_400_json_data()
            return make_response(jsonify(data))
    else:
        if (current_user.is_admin and "admin" in request.referrer) or (current_user.id == user_id):
            new_review = ProductReview(user_id=user_id, product_id=product_id)
            new_review.content = content
            db.session.add(new_review)
            db.session.commit()

            # if file_dict_lists:  # 아래와 같다.
            #     for files in file_dict_lists:
            #         print(files)  # files == FileStorage 를 한개씩 담고 있는 리스트!! files[0] 를 해줘야 한다.
            #         new_dz_image = ProductReviewImage(user_id=target_user.id, product_id=product_id, board_id=new_review.id)
            #         single_img_save(new_dz_image, request_path, files[0], target_user, files[0].filename)
            #         g.db.add(new_dz_image)
            #     g.db.commit()
            if images:
                for image in images:
                    new_dz_image = ProductReviewImage(user_id=target_user.id, product_id=product_id, review_id=new_review.id)
                    single_img_save(new_dz_image, request_path, image, target_user, image.filename)
                    g.db.add(new_dz_image)
                db.session.commit()

            board_response = {
                "_success": "success",
                "flash_message": "리뷰 등록성공",
                "redirect_url": current_path + f'#board_{str(new_review.id)}',
            }
            return make_response(jsonify(board_response))
        else:
            data = error_400_json_data()
            return make_response(jsonify(data))


@products.route('/product/review/delete/ajax', methods=['POST'])
def product_review_delete_ajax():
    review_id = request.form.get("review_id")
    current_path = request.form.get("current_path")
    target_review = ProductReview.query.filter_by(id=review_id).first()
    target_dz_images = target_review.productreview_image_set
    if review_id:
        if target_dz_images:
            for image in target_dz_images:
                img_delete(image.img_path)
                db.session.delete(image)
        db.session.delete(target_review)
        db.session.commit()
        _response = {
            "_success": "success",
            # "flash_message": "리뷰 삭제성공",  # 이게 되나?
            "redirect_url": current_path,
        }
        return make_response(jsonify(_response))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/product/review/dz/image/delete/ajax', methods=['POST'])
def product_review_dz_image_delete_ajax():
    checked = request.form.get("checked")
    review_id = request.form.get("review_id")
    image_id = request.form.get("image_id")
    if (checked == "confirm") and review_id and image_id:
        _response = {
            "_success": "success",
            "flash_message": f'success:{review_id}:{image_id}',
        }
        return make_response(jsonify(_response))
    else:
        target_image = ProductReviewImage.query.filter_by(id=image_id).first()
        if target_image.img_path:
            img_delete(target_image.img_path)
        db.session.delete(target_image)
        db.session.commit()
        _response = {
            "_success": "success",
            "flash_message": "성공적으로 삭제되었습니다.",
        }
        return make_response(jsonify(_response))


@products.route('/product/question/save', methods=['POST'])
def product_question_save():
    current_path = request.form.get("current_path")
    user_id = request.form.get("user_id")
    product_id = request.form.get("product_id")
    target_product = Product.query.filter_by(id=product_id).first()

    question_id = request.form.get("question_id")
    question_type = request.form.get("question_type")
    is_secret = request.form.get("is_secret")  # check on, not None
    title = request.form.get("title")
    content = request.form.get("content")
    if question_id:
        target_question = ProductQuestion.query.filter_by(id=question_id).first()
        if question_type:
            target_question.type = question_type
        else:
            target_question.type = QUESTION_TYPES[0]

        if is_secret is not None:
            target_question.is_secret = True
        else:
            target_question.is_secret = False
        target_question.title = title
        target_question.content = content
        db.session.add(target_question)
        db.session.commit()

        return redirect(current_path)
    else:
        new_question = ProductQuestion(user_id=user_id, product_id=product_id)
        if question_type:
            new_question.type = question_type
        else:
            new_question.type = QUESTION_TYPES[0]

        if is_secret is not None:
            new_question.is_secret = True
        else:
            new_question.is_secret = False
        new_question.title = title
        new_question.content = content
        db.session.add(new_question)
        db.session.commit()

        return redirect(url_for("products.product_detail", _id=target_product.id, slug=target_product.slug) + "#question_" + str(new_question.id))


@products.route('/product/question/delete/ajax', methods=['POST'])
def product_question_delete_ajax():  # 답변이 달리고 나면, 삭제는 안되게(삭제 버튼 없슴, 정책)
    user_id = request.form.get("user_id")
    current_path = request.form.get("current_path")
    question_id = request.form.get("question_id")

    if user_id:
        if question_id:
            target_question = ProductQuestion.query.filter_by(id=question_id).first()
            if int(user_id) == target_question.user_id:
                db.session.delete(target_question)
                db.session.commit()

                _response = {
                    "_success": "success",
                    # "flash_message": "질문 삭제성공",
                    "redirect_url": current_path,
                }
                return make_response(jsonify(_response))
            else:
                data = error_401_json_data()
                return make_response(jsonify(data))
        else:
            data = error_400_json_data()
            return make_response(jsonify(data))
    else:
        data = error_400_json_data()
        return make_response(jsonify(data))


@products.route('/product/question/reply/save', methods=['POST'])
def product_question_reply_save():
    current_path = request.form.get("current_path")
    user_id = request.form.get("user_id")
    req_user = User.query.filter_by(id=user_id).first()
    product_id = request.form.get("product_id")
    question_id = request.form.get("question_id")
    reply_id = request.form.get("reply_id")
    content = request.form.get("content")

    target_product = Product.query.filter_by(id=product_id).first()
    target_question = ProductQuestion.query.filter_by(id=question_id).first()
    if req_user.is_admin or req_user.is_staff or target_product.user:
        """# 답변은 어드민 혹은 스태프 혹은 상품등록회원(판매사업자)만 가능하므로..."""
        if reply_id:
            target_reply = ProductAnswer.query.filter_by(id=reply_id).first()
            target_reply.content = content
            db.session.add(target_reply)
            db.session.commit()
        else:
            new_reply = ProductAnswer(user_id=user_id, product_id=product_id, question_id=question_id)
            new_reply.content = content
            db.session.add(new_reply)

            target_question.is_completed = True
            db.session.add(target_question)
            db.session.commit()
        return redirect(current_path)
    abort(401)
