"""
https://www.google.com/search?q=flask+after_request&oq=flask+afte&aqs=chrome.0.0i512j69i57j0i512l8.4197j0j7&sourceid=chrome&ie=UTF-8
"""
from datetime import datetime

from flask import g, render_template
from werkzeug import security
from flask_login import current_user
from pytz import timezone


def hooks_init(app):
    from configs import db
    """템플릿단에서 loop break : {% break %}"""
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.globals.update(
        zip=zip,
        enumerate=enumerate,
    )

    @app.before_first_request
    def before_first_request():
        """
        앱 첫 request 시에 admin 존재여부 확인하고 기본 등록하기 
        """
        from www.accounts.models import User
        if not User.query.filter_by(is_admin=True).first():
            from www.accounts.models import Profile
            email = "admin@admin.com"
            password = security.generate_password_hash("admin@1234")
            admin_user = User(email=email, password=password)
            admin_user.username = "admin"
            admin_user.is_verified = True
            admin_user.is_vendor = True
            admin_user.is_staff = True
            admin_user.is_admin = True
            db.session.add(admin_user)
            db.session.commit()

            admin_profile = Profile(user_id=admin_user.id, nickname="관리자", message="최고 관리자입니다.")
            db.session.add(admin_profile)
            db.session.commit()

        from www.commons.models import BaseAmount, VarRatio
        if not BaseAmount.query.filter_by(id=1).first():
            base_pay_amount = BaseAmount(title="기본 최소 결제금액", amount=500)
            db.session.add(base_pay_amount)
            db.session.commit()
        if not VarRatio.query.filter_by(id=1).first():
            sell_charge_ratio = VarRatio(title="판매수수료율", ratio=0.07)
            db.session.add(sell_charge_ratio)
            db.session.commit()
        if not VarRatio.query.filter_by(id=2).first():
            point_ratio = VarRatio(title="포인트율", ratio=0.002)
            db.session.add(point_ratio)
            db.session.commit()

        app.logger.info('BEFORE_FIRST_REQUEST :: 앱 기동하고 맨처음 요청 직전의 응답')

    @app.before_request
    def before_request():
        """
        g.db and g.user 를 사용하기 위해???
        """
        g.db = db.session
        g.user = current_user
        app.logger.info('BEFORE_REQUEST :: 매 요청 직전에 실행')

    @app.after_request
    def after_request(response):
        app.logger.info("AFTER_REQUEST :: 매 요청이 처리되고 나서 실행")
        return response

    @app.teardown_request
    def teardown_request(exception):
        app.logger.info('TEARDOWN_REQUEST :: 브라우저가 응답하고 실행')
        if hasattr(g, 'db'):
            g.db.close()
        return "브라우저가 응답하고 실행"

    @app.teardown_appcontext
    def teardown_appcontext(exception=None):
        app.logger.info('TEARDOWN_CONTEXT :: HTTP 요청 애플리케이션 컨텍스트가 종료될 때 실행')
        db.session.remove()


def errorhandler(app):
    @app.errorhandler(400)
    def page_400(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def page_401(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(404)
    def page_404(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        from configs import db
        db.session.rollback()
        return render_template('errors/500.html'), 500


def context_processor(app):
    from configs import db
    from www.accounts.models import Profile

    @app.context_processor
    def inject_now():
        now_time = datetime.now(timezone('Asia/Seoul')).today()
        return dict(now=now_time)

    @app.context_processor
    def inject_profile():
        try:
            if current_user.is_authenticated:
                profile_obj = db.session.query(Profile).filter_by(user_id=current_user.id).first()
                return dict(current_profile=profile_obj)
            else:
                return dict(current_user=g.user)
        except Exception as e:
            print(e)

    @app.context_processor
    def ac_display_true():
        from www.boards.articles.models import ArticleCategory
        try:
            if current_user.is_authenticated:
                if ArticleCategory.query.filter_by(user_id=current_user.id, available_display=True).all():
                    return dict(current_user_ac_display_true_list=True)
                else:
                    return dict(current_user_ac_display_true_list=False)
            else:
                return dict(current_user_ac_display_true_list=False)
        except Exception as e:
            print(e)

    @app.context_processor
    def article_display_true():
        from www.boards.articles.models import Article
        try:
            if current_user.is_authenticated:
                if Article.query.filter_by(user_id=current_user.id, available_display=True).all():
                    return dict(current_user_article_display_true_list=True)
                else:
                    return dict(current_user_ac_display_true_list=False)
            else:
                return dict(current_user_article_display_true_list=False)
        except Exception as e:
            print(e)

    @app.context_processor
    def shop_display_true():
        from www.ecomm.products.models import Shop
        try:
            if current_user.is_authenticated:
                if Shop.query.filter_by(user_id=current_user.id, available_display=True).all():
                    return dict(current_user_shop_display_true_list=True)
                else:
                    return dict(current_user_ac_display_true_list=False)
            else:
                return dict(current_user_shop_display_true_list=False)
        except Exception as e:
            print(e)

    @app.context_processor
    def product_display_true():
        from www.ecomm.products.models import Product
        try:
            if current_user.is_authenticated:
                if Product.query.filter_by(user_id=current_user.id, available_display=True).all():
                    return dict(current_user_product_display_true_list=True)
                else:
                    return dict(current_user_ac_display_true_list=False)
            else:
                return dict(current_user_product_display_true_list=False)
        except Exception as e:
            print(e)

    @app.context_processor
    def cart_items_total_count():
        from www.ecomm.carts.models import Cart
        from www.ecomm.carts.models import CartProduct
        try:
            if current_user.is_authenticated:
                if current_user.cart_user_set:
                    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
                    if cart:
                        diff_time = datetime.now() - cart.updated_at
                        beyond_days = diff_time.days
                        if beyond_days < 31:
                            cart_products = CartProduct.query.filter_by(cart_id=cart.id).all()
                            return dict(cart_items_total_count=len(cart_products), current_cart=cart)
                        else:  # 카트가 있어도, 1개월이 지나면...
                            return dict(current_cart=None)
                    else:  # 카트가 없는 경우
                        return dict(current_cart=None)
                else:
                    return dict(current_cart=None)
            else:
                return dict(current_cart=None)
        except Exception as e:
            print(e)

    @app.context_processor
    def complete_orders():
        from www.ecomm.orders.models import Order
        try:
            if current_user.is_authenticated:
                order_objs = Order.query.filter_by(buyer_id=current_user.id, is_paid=True, is_display=True).all()
                if order_objs:
                    return dict(complete_orders=order_objs)
                else:
                    return dict(complete_orders=None)
            else:
                return dict(complete_orders=None)
        except Exception as e:
            print(e)

    @app.context_processor
    def is_lotto_extract():
        from www.lottos.models import LottoFirstWinNum
        try:
            latest_extract_num = LottoFirstWinNum.query.filter_by(status="latest").first()
            if latest_extract_num:
                return dict(is_lotto_extract=latest_extract_num)
            else:
                return dict(is_lotto_extract=None)
        except Exception as e:
            print(e)


def template_filter(app):
    @app.template_filter('daytime')
    def _format_datetime(value, _type=None):
        """
        템플릿단 예시: what_date|daytime("full")
        """
        if _type == "full":
            _format = '%Y.%m.%d %H:%M:%S %p'
        elif _type == "medium":
            _format = '%Y.%m.%d %H:%M'
        elif _type == "small":
            _format = '%Y.%m.%d'
        elif _type == "small_dash":
            _format = '%Y-%m-%d'
        else:
            _format = '%y.%m.%d'
        return value.strftime(_format)

    @app.template_filter('class_name')
    def model_class_name(value):
        return value.__class__.__name__

    @app.template_filter('timesince')
    def time_since(created_at, default="지금 바로"):
        """
        https://github.com/fengsp/flask-snippets/blob/master/templatetricks/timesince_filter.py
        """
        now_time = datetime.now(timezone('Asia/Seoul')).today()
        diff = now_time - created_at
        diff_sec = diff.seconds
        diff_hour = int((diff.seconds / 60 / 60))
        diff_day = diff.days

        year = int((diff.days / 365))
        remained_month = int(int((diff.days % 365)) / 30)
        month = int(diff.days / 30)
        remained_day = int(diff.days % 30)
        hour = int(diff.seconds / 60 / 60)
        minute = int(diff.seconds / 60)
        remained_min = int(diff.seconds / 60 - (int(diff.seconds / 60 / 60)) * 60)

        if diff_day >= 365:
            if remained_month == 0:
                return f'{year}년전'
            else:
                return f'{year}년 {remained_month}개월전'
        if 365 > diff_day >= 32:
            if remained_day == 0:
                return f'{month}개월전'
            else:
                return f'{month}개월 {remained_day}일전'
        if 31 > diff_day >= 1:
            return f'{diff.days}일 {hour}시간전'
        if (1 > diff_day) and (24 > diff_hour >= 1):
            if remained_min == 0:
                return f'{hour}시간전'
            else:
                return f'{hour}시간 {remained_min}분전'
        if 3600 > diff.seconds:
            return f'{minute}분전'
        return default

    @app.template_filter('intcomma')
    def num_intcomma(value):
        """
        최고 간단방법, 위(flask-babel 을 이용한 방법)와 같다. https://cosmosproject.tistory.com/373
        """
        # intcomma = '{:,}'.format(value)
        intcomma = f"{value:,}"
        return intcomma

    @app.template_filter('cleanhtml')
    def clean_html(html):
        """https://calssess.tistory.com/88"""
        from bs4 import BeautifulSoup
        clean_text = BeautifulSoup(html, "lxml").text
        return clean_text

