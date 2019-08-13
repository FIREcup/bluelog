from flask import Blueprint, render_template, flash
from flask_login import login_user, login_required, current_user
from ..forms import LoginForm
from ..models import Admin
from ..utils import redirect_back


auth_bp = Blueprint('auth', __name__)


#@auth_bp.before_request
#@login_required
#def login_protect():
#    pass


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            print('password:{}, password_hash:{}'.format(password, admin.password_hash))
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('Welcome back', 'info')
                return redirect_back() # 返回上一个页面
            flash('Invalid username or password', 'warning')
        else:
            flash('No account', 'warning')
    return render_template('auth/login.html', form=form)



@auth_bp.route('/logout')
@login_required # 用于视图保护
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()
