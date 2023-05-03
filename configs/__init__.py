from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from configs.config import TEMPLATE_ROOT, STATIC_ROOT, DevelopmentConfig, ProductionConfig
from configs.utils import hooks_init, errorhandler, template_filter, context_processor
from configs.routes import routes_init

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()


def create_app(config_name=None):
    application = Flask(__name__, template_folder=TEMPLATE_ROOT, static_folder=STATIC_ROOT)

    if not config_name:
        if application.config['DEBUG']:
            config_name = DevelopmentConfig()
        else:
            config_name = ProductionConfig()
    application.config.from_object(config_name)

    csrf.init_app(application)

    db.init_app(application)
    if application.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate.init_app(application, db, render_as_batch=True)
    else:
        migrate.init_app(application, db)
    from www.accounts import models
    from www.boards.articles import models

    from www.ecomm.products import models
    from www.ecomm.carts import models
    from www.ecomm.promotions import models
    from www.ecomm.orders import models

    from www.lottos import models

    login_manager.init_app(application)
    login_manager.login_view = 'login'
    mail.init_app(application)

    @login_manager.user_loader
    def load_user(_id):
        from www.accounts.models import User
        user = User.query.get(int(_id))
        return user

    routes_init(application)
    hooks_init(application)
    errorhandler(application)
    template_filter(application)
    context_processor(application)

    return application


app = create_app()
safe_time_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
