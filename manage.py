from app import create_app
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import db
from flask_cors import *
from app.models import *

app = create_app('testing')

manager = Manager(app)
migrate = Migrate(app, db)


manager.add_command("shell", Shell())
manager.add_command("db", MigrateCommand)

CORS(app, supports_credentials=True)


@manager.command
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
