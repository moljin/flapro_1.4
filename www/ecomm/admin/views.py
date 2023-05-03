from flask import Blueprint, render_template, request, g
from sqlalchemy import desc

from configs.config import ADMIN_PER_PAGE
from www.accounts.models import User, Profile
from www.commons.required import admin_required
from www.commons.utils import c_orm_id
from www.ecomm.carts.models import Cart
from www.ecomm.orders.models import Order, OrderTransaction, CancelPayOrder
from www.ecomm.products.forms import ShopForm, ProductForm
from www.ecomm.products.models import Shop, Product, ShopSubscriber, ProductCategory, ProductOption, ProductReview, ProductQuestion, ProductVoter
from www.ecomm.promotions.models import Coupon, Point

NAME = 'admin_ecomms'
admin_ecomm = Blueprint(NAME, __name__, url_prefix='/admin/ecomms')


@admin_ecomm.route('/shop/list', methods=['GET'])
@admin_required
def shop_list():
    shop_query = Shop.query.order_by(desc(Shop.id))
    page = request.args.get('page', type=int, default=1)
    pagination = shop_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    shops = pagination.items
    return render_template('ecomm/admin/shops/list.html',
                           shops=shops,
                           pagination=pagination)


@admin_ecomm.route('/shop/create', methods=['GET'])
@admin_required
def shop_create():
    form = ShopForm()
    user_objs = User.query.all()
    return render_template('ecomm/admin/shops/create.html',
                           form=form,
                           users=user_objs,
                           )


@admin_ecomm.route('/shop/<_id>/change', methods=['GET'])
@admin_required
def shop_change(_id):
    form = ShopForm()
    user_objs = User.query.all()
    target_shop = Shop.query.filter_by(id=_id).first()
    target_categories = ProductCategory.query.filter_by(shop_id=target_shop.id).all()
    target_user = User.query.filter_by(id=target_shop.user_id).first()
    profile_obj = Profile.query.filter_by(user_id=target_shop.user_id).first()
    products_query = Product.query.order_by(desc(Product.created_at)).filter_by(shop_id=target_shop.id)
    page = request.args.get('page', type=int, default=1)
    pagination = products_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    product_objs = pagination.items
    return render_template('ecomm/admin/shops/change.html',
                           form=form,
                           users=user_objs,
                           target_user=target_user,
                           target_profile=profile_obj,
                           target_shop=target_shop,
                           target_categories=target_categories,
                           target_products=product_objs,
                           orm_id=target_shop.orm_id,
                           )


@admin_ecomm.route('/shop/subscription/shop/list', methods=['GET'])
@admin_required
def subscription_shop_list():
    shops_query = Shop.query.order_by(desc(Shop.id))
    page = request.args.get('page', type=int, default=1)
    pagination = shops_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    shops = pagination.items
    users_all = User.query.all()
    return render_template('ecomm/admin/shops/subscription/shops.html',
                           shops=shops,
                           users_all=users_all,
                           pagination=pagination)


@admin_ecomm.route('/shop/<_id>/subscriber/list', methods=['GET'])
@admin_required
def shop_subscriber_list(_id):
    users_all = User.query.all()
    target_shop = Shop.query.filter_by(id=_id).first()
    target_user = User.query.filter_by(id=target_shop.user_id).first()
    subscriber_query = ShopSubscriber.query.order_by(desc(ShopSubscriber.user_id)).filter_by(shop_id=target_shop.id)

    page = request.args.get('page', type=int, default=1)
    pagination = subscriber_query.paginate(page=page,
                                           per_page=ADMIN_PER_PAGE,
                                           error_out=False)
    _subscribers = pagination.items  # AcSubscriber
    subscribers = list()  # User
    for s in _subscribers:
        user = User.query.filter_by(id=s.user_id).first()
        subscribers.append(user)
    return render_template('ecomm/admin/shops/subscription/subscribers.html',
                           users=users_all,
                           target_user=target_user,
                           target_shop=target_shop,
                           _subscribers=_subscribers,
                           subscribers=subscribers,
                           pagination=pagination)


@admin_ecomm.route('/product/list', methods=['GET'])
@admin_required
def product_list():
    product_query = Product.query.order_by(desc(Product.id))
    page = request.args.get('page', type=int, default=1)
    pagination = product_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    products = pagination.items
    return render_template('ecomm/admin/products/list.html',
                           products=products,
                           pagination=pagination)


@admin_ecomm.route('/product/create', methods=['GET'])
@admin_required
def product_create():
    form = ProductForm()
    user_objs = User.query.all()
    products_all = Product.query.all()
    orm_id = c_orm_id(products_all, g.user)
    return render_template('ecomm/admin/products/create.html',
                           form=form,
                           users=user_objs,
                           orm_id=orm_id)


@admin_ecomm.route('/product/<_id>/change', methods=['GET'])
@admin_required
def product_change(_id):
    form = ProductForm()
    user_objs = User.query.all()

    target_product = Product.query.filter_by(id=_id).first()
    target_options = ProductOption.query.filter_by(product_id=target_product.id).all()

    target_shop = Shop.query.filter_by(id=target_product.shop_id).first()
    target_category = ProductCategory.query.filter_by(id=target_product.pc_id).first()
    categories = ProductCategory.query.filter_by(shop_id=target_product.shop_id).all()

    target_user = User.query.filter_by(id=target_product.user_id).first()
    profile_obj = Profile.query.filter_by(user_id=target_product.user_id).first()

    reviews_query = ProductReview.query.order_by(desc(ProductReview.created_at)).filter_by(product_id=target_product.id)
    page = request.args.get('page', type=int, default=1)
    pagination = reviews_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    review_objs = pagination.items

    questions_query = ProductQuestion.query.order_by(desc(ProductQuestion.created_at)).filter_by(product_id=target_product.id)
    page_2 = request.args.get('page_2', type=int, default=1)
    pagination_2 = questions_query.paginate(page=page_2, per_page=ADMIN_PER_PAGE, error_out=False)
    question_objs = pagination_2.items
    return render_template('ecomm/admin/products/change.html',
                           form=form,
                           users=user_objs,
                           target_product=target_product,
                           target_options=target_options,
                           target_shop=target_shop,
                           target_category=target_category,
                           categories=categories,
                           target_user=target_user,
                           pagination=pagination,
                           review_objs=review_objs,
                           pagination_2=pagination_2,
                           question_objs=question_objs)


@admin_ecomm.route('/product/vote/product/list', methods=['GET'])
@admin_required
def vote_product_list():
    product_query = Product.query.order_by(desc(Product.id))
    page = request.args.get('page', type=int, default=1)
    pagination = product_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    products = pagination.items
    users_all = User.query.all()
    return render_template('ecomm/admin/products/vote/products.html',
                           products=products,
                           users_all=users_all,
                           pagination=pagination)


@admin_ecomm.route('/product/<_id>/voter/list', methods=['GET'])
@admin_required
def product_voter_list(_id):
    users_all = User.query.all()
    target_product = Product.query.filter_by(id=_id).first()
    target_user = User.query.filter_by(id=target_product.user_id).first()
    voter_query = ProductVoter.query.order_by(desc(ProductVoter.user_id)).filter_by(product_id=target_product.id)

    page = request.args.get('page', type=int, default=1)
    pagination = voter_query.paginate(page=page,
                                      per_page=ADMIN_PER_PAGE,
                                      error_out=False)
    _voters = pagination.items  # ArticleVoter
    voters = list()  # User
    for v in _voters:
        user = User.query.filter_by(id=v.user_id).first()
        voters.append(user)
    return render_template('ecomm/admin/products/vote/voters.html',
                           users=users_all,
                           target_user=target_user,
                           target_product=target_product,
                           _voters=_voters,
                           voters=voters,
                           pagination=pagination)


@admin_ecomm.route('/product/review/list', methods=['GET'])
@admin_required
def product_review_list():
    review_query = ProductReview.query.order_by(desc(ProductReview.id))
    page = request.args.get('page', type=int, default=1)
    pagination = review_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    reviews = pagination.items
    return render_template('ecomm/admin/products/reviews/list.html',
                           reviews=reviews,
                           pagination=pagination
                           )


@admin_ecomm.route('/product/review/<_id>/change', methods=['GET'])
@admin_required
def product_review_change(_id):
    target_review = ProductReview.query.filter_by(id=_id).first()
    target_product = Product.query.filter_by(id=target_review.product_id).first()
    target_user = User.query.filter_by(id=target_review.user_id).first()
    users_all = User.query.all()
    return render_template('ecomm/admin/products/reviews/change.html',
                           users=users_all,
                           target_review=target_review,
                           target_user=target_user,
                           target_product=target_product)


@admin_ecomm.route('/product/review/create', methods=['GET'])
@admin_required
def product_review_create():
    return render_template('ecomm/admin/products/reviews/create.html')


@admin_ecomm.route('/product/question/list', methods=['GET'])
@admin_required
def product_question_list():
    return render_template('ecomm/admin/products/qandas/questions/list.html')


@admin_ecomm.route('/product/question/change', methods=['GET'])
@admin_required
def product_question_change():
    return render_template('ecomm/admin/products/qandas/questions/change.html')


@admin_ecomm.route('/product/question/create', methods=['GET'])
@admin_required
def product_question_create():
    return render_template('ecomm/admin/products/qandas/questions/create.html')


@admin_ecomm.route('/product/answer/list', methods=['GET'])
@admin_required
def product_answer_list():
    return render_template('ecomm/admin/products/qandas/answers/list.html')


@admin_ecomm.route('/product/answer/change', methods=['GET'])
@admin_required
def product_answer_change():
    return render_template('ecomm/admin/products/qandas/answers/change.html')


@admin_ecomm.route('/product/answer/create', methods=['GET'])
@admin_required
def product_answer_create():
    return render_template('ecomm/admin/products/qandas/answers/create.html')


@admin_ecomm.route('/order/list', methods=['GET'])
@admin_required
def order_list():
    order_query = Order.query.order_by(desc(Order.id))
    page = request.args.get('page', type=int, default=1)
    pagination = order_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    orders = pagination.items
    return render_template('ecomm/admin/orders/list.html',
                           orders=orders,
                           pagination=pagination)


@admin_ecomm.route('/cart/list', methods=['GET'])
@admin_required
def cart_list():
    cart_query = Cart.query.order_by(desc(Cart.id))
    page = request.args.get('page', type=int, default=1)
    pagination = cart_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    carts = pagination.items
    return render_template('ecomm/admin/carts/list.html',
                           carts=carts,
                           pagination=pagination)


@admin_ecomm.route('/order/transaction/list', methods=['GET'])
@admin_required
def order_transaction_list():
    order_transaction_query = OrderTransaction.query.order_by(desc(OrderTransaction.id))
    page = request.args.get('page', type=int, default=1)
    pagination = order_transaction_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    order_transactions = pagination.items
    return render_template('ecomm/admin/orders/transaction_list.html',
                           order_transactions=order_transactions,
                           pagination=pagination)


@admin_ecomm.route('/order/cancel/pay/list', methods=['GET'])
@admin_required
def order_cancel_pay_list():
    order_cancel_pay_query = CancelPayOrder.query.order_by(desc(CancelPayOrder.id))
    page = request.args.get('page', type=int, default=1)
    pagination = order_cancel_pay_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    order_cancel_pays = pagination.items
    return render_template('ecomm/admin/orders/cancel_pay_list.html',
                           order_cancel_pays=order_cancel_pays,
                           pagination=pagination)


@admin_ecomm.route('/coupon/list', methods=['GET'])
@admin_required
def coupon_list():
    coupon_query = Coupon.query.order_by(desc(Coupon.id))
    page = request.args.get('page', type=int, default=1)
    pagination = coupon_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    coupons = pagination.items
    return render_template('ecomm/admin/promotions/coupons/list.html',
                           coupons=coupons,
                           pagination=pagination)


@admin_ecomm.route('/point/list', methods=['GET'])
@admin_required
def point_list():
    point_query = Point.query.order_by(desc(Point.id))
    page = request.args.get('page', type=int, default=1)
    pagination = point_query.paginate(page=page, per_page=ADMIN_PER_PAGE, error_out=False)
    points = pagination.items
    return render_template('ecomm/admin/promotions/points/list.html',
                           points=points,
                           pagination=pagination)
