def routes_init(app):
    from www.commons import views
    app.register_blueprint(views.common)
    from www.commons.admin import views
    app.register_blueprint(views.admin_common)

    from www.lottos import views
    app.register_blueprint(views.lotto)
    from www.lottos.admin import views
    app.register_blueprint(views.admin_lotto)

    from www.accounts import views
    app.register_blueprint(views.account)
    from www.accounts.admin import views
    app.register_blueprint(views.admin_account)

    from www.boards.articles import views
    app.register_blueprint(views.articles)
    from www.boards.articles.admin import views
    app.register_blueprint(views.admin_article)

    from www.ecomm.products import views
    app.register_blueprint(views.products)
    from www.ecomm.carts import views
    app.register_blueprint(views.carts)
    from www.ecomm.orders import views
    app.register_blueprint(views.orders)
    from www.ecomm.promotions import coupons
    app.register_blueprint(coupons.coupons)
    from www.ecomm.promotions import points
    app.register_blueprint(points.points)

    from www.ecomm.admin import views
    app.register_blueprint(views.admin_ecomm)



