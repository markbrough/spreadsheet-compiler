from flask import Flask

from spreadsheetcompiler.views import users, uploader, compiler, manager, data
from . import extensions

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


def create_app(config_object='config'):
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_blueprints(app)
    register_extensions(app)
    return app


def register_extensions(app):
    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    extensions.login_manager.init_app(app)


def register_blueprints(app):
    app.register_blueprint(users.blueprint)
    app.register_blueprint(uploader.blueprint)
    app.register_blueprint(compiler.blueprint)
    app.register_blueprint(manager.blueprint)
    app.register_blueprint(data.blueprint)
