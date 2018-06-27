#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# -*- coding: utf-8 -*-
# !/usr/bin/python
# -*- coding: ascii -*-
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# !/usr/bin/python
# -*- coding: latin-1 -*-
# !/usr/bin/python
# -*- coding: iso-8859-15 -*-

from setuptools import setup, find_packages
import os
import sys

# Encoding
reload(sys)
sys.setdefaultencoding("utf-8")


# Setting color constants
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WHITE = '\033[0;17m'
    UNDERLINE = '\033[4m'

# Checking if the user has root privileges
try:
    os.mkdir('/etc/luzia_test_folder_121234234342123134134')
    os.rm('/etc/luzia_test_folder_121234234342123134134')
except Exception, ex:
    if (ex[0] == 13):
        print bcolors.FAIL
        print >> sys.stderr, "ERROR: Se requieren privilegios de administrador para ejecutar este script!"
        print bcolors.WHITE
        sys.exit(1)


# Warning the requeriments of the script
warning = '''
Bienvenido al módulo de creación y configuración WSGI.

1) Usuario con el que corre el apache. (Para averiguarlo haga un: ps -aux | grep apache) [default: www-data]
2) Grupo del usuario con el que corre el apache. (Para averiguarlo haga un: ps -aux | grep apache) [default: www-data]
3) Ruta en donde se alojan los .conf de los sites de apache. [default: /etc/apache2/sites-enabled]
4) Ruta en donde se alojan las librerías de Python 2.7. [default: /var/www/.local/lib/python2.7/site-packages]
5) FQDN. (Ej: rulz.cuyum.com)
6) Acceso SSL
  6.1) Ruta al certificado SSL.
  6.2) Ruta a la key del certificado SSL.
  6.3) Redirección de HTTP a HTTPS?
7) Directorio de datos anexos.
8) Ruta completa al archivo de configuración (arg-properties.cfg).
9) Nombre del proceso WSGI.
'''


# Clear screen and print the warning message
def clear():
    os.system('clear')

print bcolors.WHITE
print warning

##############################################################################################################################
# 0
rulz_path = os.path.dirname(os.path.realpath(__file__))
rulz_src_path = os.path.dirname(os.path.realpath(__file__)) + os.sep + "src"


##############################################################################################################################
# 0.9
app_cod = raw_input("A que herramienta desea crear el modulo wsgi?\n1:ARG2\n2:Gateway\n3:Soap Server\n[default: 1]: ")
if app_cod == '' or (app_cod != '2' and app_cod != '3'):
    app_cod = 'ARG_SETTINGS'
elif app_cod == '2':
    app_cod = 'GATEWAY_SETTINGS'
elif app_cod == '3':
    app_cod = 'SOAPSERVER_SETTINGS'


##############################################################################################################################
# 1
apache_user = raw_input("Ingrese el usuario con el que está corriendo el apache [default: www-data]: ")
if apache_user == '':
    apache_user = 'www-data'


##############################################################################################################################
# 2
apache_group = raw_input("Ingrese el grupo del usuario con el que está corriendo el apache [default: www-data]: ")
if apache_group == '':
    apache_group = 'www-data'


##############################################################################################################################
# 3
apache_sites_path = raw_input("Ingrese la ruta de los sites de apache. [default: /etc/apache2/sites-enabled]: ")
if apache_sites_path == '':
    apache_sites_path = '/etc/apache2/sites-enabled'

##############################################################################################################################
# 4
python_lib_path = raw_input("Ingrese la ruta de las bibliotecas de python. [default: /var/www/.local/lib/python2.7/site-packages]: ")
if python_lib_path == '':
    python_lib_path = '/var/www/.local/lib/python2.7/site-packages'

##############################################################################################################################
# 5
fqdn = raw_input("Ingrese el FQDN para el virtualhost de apache. (ej: rulz.cuyum.com): ")

##############################################################################################################################
# 6
using_ssl = raw_input("Se utilizará SSL para el acceso? (s/n): ")
if using_ssl.lower() in {"y", "yes", "si", "s"}:
    using_ssl = True
else:
    using_ssl = False

##############################################################################################################################
# 6.1
ssl_cert_path = raw_input("Ingrese la ruta al certificado SSL (Ej: /var/www/certificados/certSSL.crt): ")

##############################################################################################################################
# 6.2
ssl_cert_key_path = raw_input("Ingrese la ruta a la key del certificado SSL (Ej: /var/www/certificados/certSSL.key): ")

##############################################################################################################################
# 6.3
ssl_redirect = raw_input("Desea redireccionar los llamados HTTP a HTTPS? (s/n): ")
if ssl_redirect.lower() in {"y", "yes", "si", "s"}:
    ssl_redirect = True
else:
    ssl_redirect = False


##############################################################################################################################
# 7
rulz_config_path = raw_input("Ingrese la ruta del directiorio de datos anexos de ARG. [default: /opt/arg_configs/arg]: ")
if rulz_config_path == '':
    rulz_config_path = '/opt/arg_configs/arg'


##############################################################################################################################
# 8
rulz_config_cfg_path = raw_input("Ingrese la ruta completa del archivo de configuración de ARG. [default: /opt/arg_configs/arg/conf/arg-properties.cfg]: ")
if rulz_config_cfg_path == '':
    rulz_config_cfg_path = '/opt/arg_configs/arg/conf/arg-properties.cfg'


##############################################################################################################################
# 9
wsgi_process_name = raw_input("Ingrese el nombre del proceso WSGI. (Ej: arg_wsgi_process): ")


app_wsgi = '''
import sys
import os
import site
from os import environ, getcwd
import logging, sys

sys.path.append('{0}')
os.environ['PYTHON_EGG_CACHE']="{1}"
os.environ['{3}']="{2}"
site.addsitedir('{1}')

from initserver import app as application
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

LOG = logging.getLogger(__name__)
LOG.debug('Current path: {{0}}'.format(getcwd()))

# Application config
application.debug = True

with application.app_context():
        pass
'''.format(rulz_src_path, python_lib_path, rulz_config_cfg_path, app_cod)


os.mkdir(rulz_config_path + os.sep + "wsgi")
app_wsgi_path = rulz_config_path + os.sep + "wsgi" + os.sep + "app.wsgi"
file_conf = open(app_wsgi_path, "w")
file_conf.write(app_wsgi)
file_conf.close()

clear()
print "------------------------------------------------------------------------------------------------------------------"
print "----------------------------------------------- app.wsgi ---------------------------------------------------------"
print "------------------------------------------------------------------------------------------------------------------"
print app_wsgi


if using_ssl:
    if ssl_redirect:
        virtualhost = '''
        <VirtualHost *:80>
            ServerName {0}
            Redirect permanent / https://{0}
        </VirtualHost>
        <VirtualHost *:443>
            ServerName {0}

            <Directory {1}>
                Require all granted
                Options +FollowSymLinks -Indexes
            </Directory>

            <Directory "{2}">
                Options -Indexes +FollowSymLinks
                AllowOverride All
                Require all granted
            </Directory>

            # Possible values include: debug, info, notice, warn, error, crit,
            # alert, emerg.
            LogLevel debug

            WSGIDaemonProcess {3} user={4} group={5} threads=5
            WSGIScriptAlias / {6}
            WSGIPassAuthorization On
            WSGIScriptReloading On

            ErrorLog ${{APACHE_LOG_DIR}}/error-{0}.log
            CustomLog ${{APACHE_LOG_DIR}}/access-{0}.log combined

            Include "/etc/apache2/include/ssl.conf"

            SSLCertificateFile {7}
            SSLCertificateKeyFile {8}
        </VirtualHost>
        '''.format(fqdn, rulz_path, rulz_config_path, wsgi_process_name, apache_user, apache_group, app_wsgi_path, ssl_cert_path, ssl_cert_key_path)
    else:
        virtualhost = '''
    <VirtualHost *:443>
        ServerName {0}

        <Directory {1}>
            Require all granted
            Options +FollowSymLinks -Indexes
        </Directory>

        <Directory "{2}">
            Options -Indexes +FollowSymLinks
            AllowOverride All
            Require all granted
        </Directory>

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel debug

        WSGIDaemonProcess {3} user={4} group={5} threads=5
        WSGIScriptAlias / {6}
        WSGIPassAuthorization On
        WSGIScriptReloading On

        ErrorLog ${{APACHE_LOG_DIR}}/error-{0}.log
        CustomLog ${{APACHE_LOG_DIR}}/access-{0}.log combined

        Include "/etc/apache2/include/ssl.conf"

        SSLCertificateFile {7}
        SSLCertificateKeyFile {8}
    </VirtualHost>
    '''.format(fqdn, rulz_path, rulz_config_path, wsgi_process_name, apache_user, apache_group, app_wsgi_path, ssl_cert_path, ssl_cert_key_path)
else:
    virtualhost = '''
    <VirtualHost *:80>
        ServerName {0}

        <Directory {1}>
            Require all granted
            Options +FollowSymLinks -Indexes
        </Directory>


        <Directory "{2}">
            Options -Indexes +FollowSymLinks
            AllowOverride All
            Require all granted
        </Directory>

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel debug

        WSGIDaemonProcess {3} user={4} group={5} threads=5
        WSGIScriptAlias / {6}
        WSGIProcessGroup {3}
        WSGIApplicationGroup %{GLOBAL}
        WSGIPassAuthorization On
        WSGIScriptReloading On

        ErrorLog ${{APACHE_LOG_DIR}}/error-{0}.log
        CustomLog ${{APACHE_LOG_DIR}}/access-{0}.log combined
    </VirtualHost>
    '''.format(fqdn, rulz_path, rulz_config_path, wsgi_process_name, apache_user, apache_group, app_wsgi_path)

file_conf = open(apache_sites_path + os.sep + fqdn + ".conf", 'w')
file_conf.write(virtualhost)
file_conf.close()

print "------------------------------------------------------------------------------------------------------------------"
print "-----------------------------------------------" + fqdn + ".conf -----------------------------------------------"
print "------------------------------------------------------------------------------------------------------------------"
print virtualhost


print bcolors.OKBLUE
print '''
El app.wsgi y el virtualhost ({0}.conf) se han generado exitosamente:

Enjoy it!
'''.format(fqdn)

print bcolors.WHITE
