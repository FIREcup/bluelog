from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

bootstrap = Bootstrap()
mail = Mail()
ckeditor = CKEditor()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManger()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    from .models import Admin
    user = Admin.query.get(int(user_id))
    return user

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
