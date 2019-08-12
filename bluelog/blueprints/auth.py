from flask import Blueprint
from flask_login import login_user


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validdate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('Welcome back', 'info')
                return redirect_back() # 返回上一个页面
            flash('Invalid username or password', 'warning')
        else:
            flash('No account', 'warning')
    return render_template('auth/login.html', form=form)



@auth_bp.route('/logout')
def logout():
    if current_user.
