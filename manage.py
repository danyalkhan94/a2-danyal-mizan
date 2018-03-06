from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from blogspace import app, db


app.config.from_object('config')

