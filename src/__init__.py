# from flask import Flask, render_template, url_for, redirect, flash, session
# from flask_mongoalchemy import MongoAlchemy
# from flask_login import LoginManager, UserMixin
# from utils.toolbox import rsa_decrypt

# import os
# import sys

# os.chdir(os.path.dirname(os.path.realpath(__file__)))

# tmpl_dir = os.path.realpath("..") + os.sep + "html"
# static_fold = os.path.realpath("..") + os.sep + "html"

# app = Flask('luzia-rulz', template_folder=tmpl_dir, static_folder=static_fold)

# app.secret_key = '16e91cb7a939c640b37d77e14bbd79d3'


# try:
#     app.config.from_envvar('ARG_SETTINGS')
#     app.config['MONGOALCHEMY_DATABASE'] = 'mongo_alchemy_rulz'

#     if app.config.get('MONGO_SECURITY_ENABLED') is True:
#         app.config['MONGOALCHEMY_USER'] = app.config.get('MONGO_USER')

#         app.config['MONGOALCHEMY_PASSWORD'] = rsa_decrypt(app.config.get('PRIVATE_KEY_PATH'), app.config.get('MONGO_PASS'))

#     db = MongoAlchemy(app)
#     lm = LoginManager(app)
#     lm.login_view = 'index'
#     app.config['PERMANENT_SESSION_LIFETIME'] = 3600

#     oauth_enabled = app.config.get('OAUTH_ENABLED')
#     sso_enabled = app.config.get('SSO_ENABLED')

#     setup_ok = True
# except Exception, e:
#     print "Lo sentimos, pero no se encuentra la referencia a la variable de ambiente ARG_SETTINGS la cual debe estar definida y referenciar el archivo de configuracion correspondiente"
#     print e
#     raise e


# class User(UserMixin, db.Document):
#     social_id = db.StringField(max_length=64)
#     nickname = db.StringField(max_length=64)
#     email = db.StringField(max_length=64)
#     organization_id = db.StringField(max_length=30)
#     roles = db.ListField(db.StringField(max_length=64))

#     def get_id(self):
#         return self.social_id
