from datetime import datetime
import os
from flask import Flask,render_template,request
from .extensions import db,mail,migrate,login_manager,babel
from .models import User,Article,Category,Comment,Tag,Notification
from .settings import Config
from flask_login import current_user
from flask_wtf.csrf import CSRFError
import click
from elasticsearch import Elasticsearch

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)
    register_extensions(app)
    register_filters(app)
    register_shell_context(app)
    register_templates_context(app)
    create_database(app)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        
    return app



def create_database(app):
    if not os.path.exists('/database.db'):
        db.create_all(app=app)

def register_blueprints(app):
    from .blueprints.admin import admin
    from .blueprints.auth import auth
    from .blueprints.routes import routes
    app.register_blueprint(auth,prefix_url='/')
    app.register_blueprint(routes, prefix_url='/')
    app.register_blueprint(admin, prefix_url='/')

def register_extensions(app):
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401
        
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 500


def register_templates_context(app):
    """
    this will help us to reference the variable without the need to pass it to the render template function you can just call the variable
    on your HTML template
    """
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            notification_count=Notification.query.with_parent(current_user).filter_by(is_read=False).count()
        else:
            notification_count = None
        return dict(notification_count=notification_count,current_date=datetime.utcnow())


def register_filters(app):
    @app.template_filter('')
    def dateformater(value, format='%b/%m/%Y'):
        return value.strftime(format)

def register_shell_context(app):
    """
    shell_context_processor decorator register the function as shell context function when the flask shell commands run
    it will invoke this function and register the items returned by it in the shell session.
    shell context helps us to test our app from python shell with out importing everything
    """
    @app.shell_context_processor
    def make_shell_context():
        # the reason that the function returns a dict is that for each item you have also provide a name under which it will be referenced
        return dict(db=db,User=User,Article=Article,Notification=Notification,Comment=Comment,Category=Category,Tag=Tag)


def register_commands(app):
    """
    we can use this command from cmd you can add more commands
    we add them using click this module that add the command
    app.cli.command decorator makes sure that the command will executed with
    an application context pushed so our command and extensions have access
    to the app and its configuration,you can create command this way or you can create it
    this way
    @click.command
    @with_appcontext --> you can import with_appcontext form flask.cli
    """
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        #Initialize the database
        if drop:
            click.confirm(
                'This operation will delete the database do you want to continue', abort=True)
            db.drop_all()
            click.echo('Drop tables')
        db.create_all()
        click.echo('Initialized database')

    @app.cli.command()
    def init():
        click.echo('Initializing the database...')
        db.create_all()
        click.echo('Done')
