class Config(object):
    APP_NAME = "mankkoo-accounting"
    DB_NAME = ""


class DevConfig(Config):
    PORT = 5000
    DEBUG = True
    TESTING = False
    ENV = "dev"
    DB_NAME = "dev"


class ProdConfig(Config):
    PORT = 8080
    DEBUG = False
    TESTING = False
    ENV = "prod"
    DB_NAME = "mankkoo"


class TestConfig(Config):
    PORT = 5555
    DEBUG = True
    TESTING = True
    ENV = "test"
    DB_NAME = "test"
