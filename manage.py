#assignment 2
#PROG38263
#Danyal Khan 991 389 587
#Mizanur Rahman 981388924

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from blogspace import app, db


app.config.from_object('config')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

