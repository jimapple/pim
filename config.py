import os
import sys

PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 3:
    import urllib.parse
else:
    import urlparse

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


class Config:
    APP_NAME = 'PIM'
    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    REDIS_HOST = os.getenv('REDIS_HOST') or '122.237.100.158'
    REDIS_PORT = int(os.getenv('REDIS_PORT', 0)) or 6379
    REDIS_DB = os.getenv('REDIS_DB') or '0'
    CLIENT_ACCESS_TOKEN = []

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 10
    TOKEN_TTL = 3600
    TOKEN_PREFIX = "douwa:token"
    GENERATORID_IP = "122.237.100.158:5001"

    # 数据库连接池
    # 数据库连接超时时间
    # 显示sql语句
    # SQLALCHEMY_ECHO = true
    # 数据库对象

    base_fmt = ('%(name)s:%(levelname)s %(message)s:%(pathname)s:%(lineno)s')
    syslog_tag = "douwa"
    LOGCONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {},
        'formatters': {
            'tornado': {
                '()': 'tornado.log.LogFormatter',
                'color': True
            },
            'simple': {
                '()': 'tornado.log.LogFormatter',
                'color': False
            },
        },
        'handlers': {
            'console': {
                '()': 'logging.StreamHandler',
                'formatter': 'tornado'
            },
           #  'file' : {
           #      '()': 'logging.handlers.RotatingFileHandler',
           #      'formatter': 'simple',
           #      'filename':basedir,
           #      'mode': 'a',
           #      'maxBytes': 50000,  # 5 MB
           #      'backupCount': 1,
           # },
     },
        'loggers': {
            'app.api.user': {
                'handlers': ['console'],
                'level': 'INFO'
            },
        },
        'root':{
                'handlers': ['console'],
                'level': 'INFO'
        }
    }

    LOGCONFIG_QUEUE = ['myapp']


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    print('THIS APP IS IN DEBUG MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class TestingConfig(Config):
    TESTING = True
    user = os.environ.get('PG_USER') or "jim"
    pwd = os.environ.get('PG_PWD') or "123456"
    host = os.environ.get('PG_HOST') or "47.100.21.215"
    port = int(os.environ.get('PG_PORT', 0)) or 50310
    db = os.environ.get('PG_DB') or "pim"
    DEBUG = True
    # user = os.environ.get('PG_USER') or "iye"
    # pwd = os.environ.get('PG_PWD') or "123456"
    # host = os.environ.get('PG_HOST') or "122.237.100.158"
    # port = int(os.environ.get('PG_PORT', 0)) or 5432
    # db = os.environ.get('PG_DB') or "test_pim"

    data = dict(user=user, pwd=pwd, host=host, port=port, db=db)
    con_str = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}?client_encoding=utf8'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              con_str.format(**data)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SSL_DISABLE = (os.environ.get('SSL_DISABLE') or 'True') == 'True'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku': HerokuConfig,
    'unix': UnixConfig
}
