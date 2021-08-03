from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate
from flask_mail import Mail
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)


db = SQLAlchemy(session_options={"autoflush": False}, metadata=metadata)
login_manager =LoginManager()
babel = Babel()
migrate = Migrate()
mail = Mail()


login_manager.login_view='auth.login'
login_manager.login_message_category='warning'


@login_manager.user_loader
def user_load(id):
    from .models import User
    return User.query.get(int(id))
