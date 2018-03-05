import os

# configuration
APP_DIR  = os.path.dirname(os.path.realpath(__file__))
APP_NAME = 'Blog Space' 

SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlalchemy_example.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False


SECURITY_PASSWORD_SALT = 'rF8zsNAP9BQVx7N82PQA6aCa7ru5gzQQcpga3DsflPngCDMM7UW8u8AifvXS'
SECRET_KEY = 'InRNnbv0zZlmaF138f7AWSGE9pstd7kfkrp3B0VgVsFBYlDFW5TsjolWEqMq'
BCRYPT_LOG_ROUNDS = 12


DEBUG = True

# mail settings
MAIL_SERVER  = 'smtp.googlemail.com'
MAIL_PORT    = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# mail accounts
MAIL_DEFAULT_SENDER = 'bloggingapp12@gmail.com'

# gmail authentication 
MAIL_USERNAME = 'bloggingapp12'
MAIL_PASSWORD = 'commonwords'


DEFAULT_POST_IMG  = 'http://placehold.it/850x400?text=Blog+Space'
DEFAULT_USER_LOGO = 'http://www.free-icons-download.net/images/user-icon-27998.png'

# misc constants
CACHE_TIMEOUT = 300
PER_PAGE      = 10
MAX_LINK_LEN  = 50
CONFIRM_EMAIL_TOKEN_EXPIRATION = 3600


