from flask import Flask, render_template, url_for, redirect, flash, session, request
from flask_mongoalchemy import MongoAlchemy
from mongoalchemy.document import Document
from mongoalchemy.fields import *
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from init import app, User, lm, oauth_enabled, sso_enabled

from services.config import config
from services.rulz import rulz
from services.auditory import auditory
from services.snapshots import snapshots
from security.security import security, loginSSO
from utils.toolbox import configLogger, rsa_decrypt

from services.api_service import api_service, register_all

import sys

app.register_blueprint(config)
app.register_blueprint(rulz)
app.register_blueprint(snapshots)
app.register_blueprint(auditory)
app.register_blueprint(security)
app.register_blueprint(api_service)

reload(sys)
sys.setdefaultencoding("utf-8")


def run_init_config():
    with app.app_context():
        configLogger()
        register_all()

setup_ok = True


@lm.user_loader
def load_user(id):
    return User.query.filter(User.social_id == id).first()


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html")

    if sso_enabled is True:
        print app.template_folder
        return render_template("index.html")
        # if loginSSO():
        #     return redirect(url_for('index'))

        return app.make_response(render_template('505.html')), 505

    return render_template("login.html")


@app.route('/auth')
def indexAuth():
    if sso_enabled is True:
        headersParams = request.args.to_dict()
        loginSSO(headersParams)

    return render_template("index.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def autorizedStatic(path):
    parts = path.split('/')

    if len(parts) < 2:
        return False

    if parts[0] in ['libs', 'styles', 'scripts', 'fonts'] and parts[len(parts) - 1].endswith(('.js', '.css', '.jpg', '.html', '.otf', '.eot', '.svg', '.svg', '.woff', '.woff2')):
        return True

    if parts[len(parts) - 1].endswith(('.js', '.css', '.jpg', '.html', '.otf', '.eot', '.svg', '.svg', '.woff', '.woff2')) and parts[0] == 'login':
        return True

    return False


@app.route('/<path:path>')
def catch_all(path):
    if current_user.is_authenticated or autorizedStatic(path):
        return app.send_static_file(path)

    if sso_enabled is True:
        # if loginSSO():
        return app.send_static_file(path)

        # return app.make_response(render_template('505.html')), 505

    if oauth_enabled is True:
        return render_template("login.html")


@app.before_first_request
def before_first():
    run_init_config()

if __name__ == '__main__':

    with app.app_context():
        '''App Conext Here'''

    if (setup_ok):
        app.debug = app.config["DEBUG_MODE"]
        # run_init_config()
        app.app_context().push()
        app.run("0.0.0.0", app.config["ARG_RULZ_PORT"])
