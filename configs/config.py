import datetime
import os
from os.path import join, dirname

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_ROOT = os.path.join(BASE_DIR, 'www/templates')
STATIC_ROOT = os.path.join(BASE_DIR, 'www/static')

# cf. # date=str(now.date()), # UTC
SUPER_ADMIN_EMAIL = "moljin@naver.com"
ADMIN_PER_PAGE = 5

dotenv_path = join(dirname(__file__), '.env')  # dirname(__file__): 현재 디렉토리, Path to .env file
load_dotenv(dotenv_path)


def read_secret(secret_name):
    file = open('/run/secrets/' + secret_name)
    secret = file.read()
    secret = secret.rstrip().lstrip()
    file.close()
    return secret


class Config(object):
    DEBUG = False
    TESTING = False

    NUM_WORKERS = 10
    TIMEOUT = 1200  # 초

    SESSION_COOKIE_NAME = 'FLAPRO_1.4'
    TIMEZONE = 'Asia/Seoul'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_ECHO = True  # lazy='dynamic' lazy='select' lazy='joined' lazy='subquery'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # 파일 업로드 용량 제한 단위:바이트 16MB
    # (cf. 20MB: 20 * 1024 * 1024)
    # nginx.conf 파일에서도 조정한다.

    """
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465  # 587 : 이거는 장고
    MAIL_USERNAME = "khandure00@gmail.com"#"khandure05@gmail.com"
    MAIL_PASSWORD = os.environ.get("KHANDURE00_MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    """
    MAIL_SERVER = "mw-002.cafe24.com"
    MAIL_PORT = 587  # 25
    MAIL_USERNAME = "flask05@rgmong.kr"
    MAIL_PASSWORD = "rgmoljin!@1011"
    # MAIL_PASSWORD = os.environ.get("CAFE24_MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False

    # IAMPORT_KEY = os.environ.get("IAMPORT_KEY")
    # IAMPORT_SECRET = os.environ.get("IAMPORT_SECRET")
    IAMPORT_KEY = "9977587767482490"
    IAMPORT_SECRET = "VemzzClTRGQltTW0E0PXqB0iQaNJHd1Drnc0ZxUReLdIFaJjaygBahU1sIK9VMMnaZoaxj1L4fuJpd2A"


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SEND_FILE_MAX_AGE_DEFAULT = 1  # 개발환경에서 캐시 파일 1초마다 reload 할 수 있도록 한거다.
    TEMPLATES_AUTO_RELOAD = True  # DEBUG = True이면 자동으로 켜진다. 굳이 안써도 된다면서.....
    WTF_CSRF_ENABLED = True  # False로 하면 좋으나 체크하기위해 True

    MYSQL_ROOT_USER = 'root'
    MYSQL_ROOT_PASSWORD = os.environ.get("DEV_MYSQL_ROOT_PASSWORD")
    MYSQL_DATABASE = 'flapro_1.4'
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = '3306'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_ROOT_USER}:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8"


class ProductionConfig(Config):
    SECRET_KEY = "thisissecretkey"
    # SECRET_KEY = os.environ.get("SECRET_KEY")

    MYSQL_ROOT_USER = 'root'
    MYSQL_ROOT_PASSWORD = "moljin!981011"
    # MYSQL_ROOT_PASSWORD = os.environ.get("PROD_MYSQL_ROOT_PASSWORD")
    MYSQL_DATABASE = 'flapro_1.4'
    MYSQL_HOST = '112.186.157.226'
    MYSQL_PORT = '56033'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_ROOT_USER}:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8"


class TestingConfig(Config):
    __test__ = False
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "sqlite_test.db")}'
