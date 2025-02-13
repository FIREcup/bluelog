import os
import click
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from .extensions import bootstrap, mail, moment, db, ckeditor, bootstrap, login_manager, csrf
from .settings import config
from .models import Admin, Category, Post, Link, Comment
from flask_login import current_user


from .blueprints.admin import admin_bp
from .blueprints.auth import auth_bp
from .blueprints.blog import blog_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)
    return app


def register_logging(app):
    pass

def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()

        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        if drop:
            click.confirm('This operation will drop all the data and create a new one, continue?', abort=True)
            db.drop_all()
            click.echo('Drop all data...')
        db.create_all()
        click.echo('Creating data...')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generate fake data"""
        from .fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator....')
        fake_admin()

        click.echo('Generating the categories...')
        fake_categories()

        click.echo('Generating the posts...')
        fake_posts()

        click.echo('Generating the comments...')
        fake_comments()

        click.echo('Generating the links....')
        fake_links()

        click.echo('Done')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    #@click.option('--password', prompt=True, hide_input=True,
    #        confirmation_prompt=True, help='The password used to login.')
    @click.password_option()
    def init(username, password):
        """Building Bluelog, just for you"""
        click.echo('Initializing the database...')
        db.create_all()
        print('password:{}'.format(password))
        admin = Admin.query.first()
        if admin: # 如果已经存在admin用户，则更新用户名和密码
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else: # 否则创建admin用户
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                    username = username,
                    blog_title = 'Bluelog',
                    blog_sub_title = 'No, I\'m the real thing.',
                    name = 'Admin',
                    about = 'Anything about you.'
                    )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

