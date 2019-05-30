from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

login_manager.login_view = "users.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "danger"
