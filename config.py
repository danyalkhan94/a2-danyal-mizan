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
MAIL_PORT   