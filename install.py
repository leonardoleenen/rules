# -*- coding: UTF-8 -*-
# from setuptools import setup, find_packages
import os
import sys
from urlparse import urlparse


def ensure_dir(folder):
    d = os.path.dirname(folder + os.sep)
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno == 13:
                print 'No se poseen permisos para crear los directorios en el sistema'
                raise e


if len(sys.argv) == 1:
    print "Debe indicar el modo de instalacion de las librerias python (develop o install)"
    sys.exit(-1)


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


welcome = '''
Bienvenidos al modulo de instalacion de ARG. Durante este proceso se solicitaran datos de configuracion.
Para continuar con la instalación debe poseer los siguientes datos:
    1-  Path absoluto donde se almacenarán los archivos de configuraciones y datos anexos de la aplicación (Por defecto "/opt/arg2_folder")
    2-  Puerto donde correra la aplicación en el sistema donde se está isntalando (Por defecto "5000")
    3-  fqdn del host donde se encuentra corriendo MongoDB (Por defecto "localhost")
    4-  Puerto donde corre MongoDB (Por defecto "27017")
    5-  Usuario con acceso a MongoDB (Opcional)
    6-  Contraseña encriptada del Usuario (Opcional)
    7-  Path al archivo de clave privada (Opcional)
    8-  URL de servicio de roles de usuario (Por defecto http://localhost:5000/security/user/get_roles)
    9-  URL de servicio de sub-organizaciones de usuario (Por defecto http://localhost:5000/security/get_organizations)
    10-  fqdn del servidor de reglas (Run - Time) y de ser necesario el puerto asociado al mismo (Por defecto http://127.0.0.1:8080)
'''

os.system('clear')
print bcolors.OKGREEN
print welcome

app_path = os.path.dirname(os.path.realpath(__file__))

print "\n" * 5
print bcolors.WHITE


data = raw_input("Por favor ingrese el path absoluto donde quiere realizar la instalacion [default: /opt/Rulz]: ")
if data == "":
    data = "/opt/Rulz"

luzia_port = raw_input("Por favor ingrese el puerto del host donde correra ARG [default: 5000]: ")
if luzia_port == "":
    luzia_port = "5000"


mongo_host = raw_input("Por favor ingrese el nombre del host donde esta ejecutando mongo [default: localhost]: ")
if mongo_host == "":
    mongo_host = "localhost"


mongo_port = raw_input("Por favor ingrese el numero de puerto del host donde se ejecuta MongoDB [default: 27017]: ")
if mongo_port == "":
    mongo_port = "27017"

mongo_sec_active = raw_input("Se encuentra activa la seguridad de MongoDB? si - no [default no]: ")
if mongo_sec_active == "":
    mongo_sec_active = False
elif mongo_sec_active == "si" or mongo_sec_active == "yes":
    mongo_sec_active = True
elif mongo_sec_active != "no":
    mongo_sec_active = False
else:
    mongo_sec_active = False

if mongo_sec_active is True:
    mongo_user = raw_input("Nombre de Usuario de MongoDB [default \"arg2\"]: ")
    if mongo_user == "":
        mongo_user = "arg2"

    mongo_pass = raw_input("Password encriptada del usuario de MongoDB: ")

    mongo_sec_path = raw_input("Path de la private key: ")

else:
    mongo_user = ""
    mongo_pass = ""
    mongo_sec_path = ""


ready = False
while not ready:
    roles_url = raw_input("Por favor ingrese la url del servicio de obtencion de roles de usuario [default: http://localhost:5000/security/user/get_roles]: ")
    ready = True
    if roles_url == '':
        roles_url = "http://localhost:5000/security/user/get_roles"
    else:
        u = urlparse(roles_url)
        if u.scheme is None or u.scheme == '' or u.netloc is None or u.netloc == '':
            ready = False

ready = False
while not ready:
    sub_organization_url = raw_input("Por favor ingrese el servicio de obtencion de sub-organizaciones [default: http://localhost:5000/security/get_organizations]: ")
    ready = True
    if sub_organization_url == '':
        sub_organization_url = "http://localhost:5000/security/get_organizations"
    else:
        u = urlparse(sub_organization_url)
        if u.scheme is None or u.scheme == '' or u.netloc is None or u.netloc == '':
            ready = False

ready = False
while not ready:
    rule_server = raw_input("Por favor ingrese la URL del servidor de reglas (Run Time) [default: http://127.0.0.1:8080]: ")
    ready = True
    if rule_server == '':
        rule_server = 'http://127.0.0.1:8080'
    else:
        u = urlparse(rule_server)
        if u.scheme is None or u.scheme == '' or u.netloc is None or u.netloc == '' or len(u.netloc.rsplit('.', 1)) < 2:
            print "\nDebe ingresar una url valida!\n"
            ready = False

rule_server_dialect = 'mvel'

arg_config = '''

#Rule Server
RULE_DIALECT="{8}"
RULE_SERVER="{7}"
RULE_SERVER_VALIDATE="/selectividad/rest/rule_engine/drl/validate"
RULE_SERVER_DRL="/selectividad/rest/rule_engine/drl"
RULE_SERVER_BASE="/selectividad/rest/rule_engine/execute"
RULE_SERVER_TEST="/selectividad/rest/rule_engine/execute/approval"
RULE_SERVER_INSTALL="/selectividad/rest/rule_engine/execute/install"
RULE_SERVER_UNISTALL="/selectividad/rest/rule_engine/execute/uninstall"
RULE_SERVER_LIST="/selectividad/rest/rule_engine/execute/list"
RULE_SERVER_IS_ALIVE="/selectividad/rest/rule_engine/test"

#Tech Configuration
ARG_RULZ_PORT={1}
DEBUG_MODE=True

MONGO_HOST="{3}"
MONGO_PORT={4}
MONGO_SECURITY_ENABLED={9}
MONGO_USER="{10}"
MONGO_PASS="{11}"
PRIVATE_KEY_PATH="{12}"

HANDLED_BY_DIRECTOR=True

NEED_INSTRUMENTS=True

SERVICE_PROTECTION=False

AUTO_VERSION=True

APP_PATH='{0}'

PLUGINS_PATH="{2}/plugins"

TMP_FOLDER='{2}/tmp'

LOGGER_CONFIG='{2}/conf/arg-logger-conf.yaml'

FILE_STORAGE_BUCKET_PATH="{2}/storage/bucket"
FILE_STORAGE_SNAPSHOTS="{2}/storage/snapshots"
FILE_STORAGE_FACTS="{2}/storage/facts"
FILE_STORAGE_SIGNED_FILES_PATH="{2}/storage/signed"

RULE_STORAGE="{2}/rule_storage"
FIXED_EVENTS_URL=""

#[ROLES]
MODULE_TEMPLATE_PUBLICATION="ONC, Administrador"
MODULE_TEMPLATE_CONSUMPTION="Operador,Publicador,Administrador"
MODULE_CALENDAR="Operador,Publicador,Administrador,ONC"
MODULE_RULES="Administrador"
MODULE_ADMINISTRATION="Administrador"

#[INTERNATIONALIZATION]
i18n="es"

#[DEV MODE]
DEV_ORGANIZATION="Luzia"
DEV_MODE=False
FILTER_BY_ROLES=True

LOAD_USER_DATA_URL="{5}"
FETCH_SUBORGS_URL="{6}"
LOGOUT_URL=""
FIXED_EVENTS_URL=""
LOGO_SRC="src/img/aduana_logo.png"

USER_PROFILES_MODULES_MATRIX=[("AUDIT_MENU",["ADMINISTRADOR"]),("BTN_PUBLICAR_ESCENARIO",["ADMINISTRADOR","EDITOR","PUBLICADOR"]),("TEMPLATE_PUBLICATION",["ADMINISTRADOR", "ONC"]), ("TEMPLATE_CONSUMPTION",["ADMINISTRADOR","EDITOR","PUBLICADOR"]), ("CALENDAR",["ONC","Publicador","Operador","ADMINISTRADOR"]), ("RULES",["ADMINISTRADOR"]), ("ADMINISTRATION",["ADMINISTRADOR"])]

USER_PROFILES_SERVICES_MATRIX=[{{"path":"/security/token/create","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/security/rxf/matrix","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/security/user/get_roles","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/anses/get_employee_office","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/anses/get_office_children","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/config/as_dict","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/config/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/rulz/rule","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteRule"]}},{{"path":"/rulz/entity","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteEntity"]}},{{"path":"/rulz/check/entity/attribute","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteEntity"]}},{{"path":"/rulz/change/entity/attribute","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteEntity"]}},{{"path":"/rulz/catalog","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteCatalog"]}},{{"path":"/rulz/table","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteTable"]}},{{"path":"/rulz/simulation","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteSimulation"]}},{{"path":"/rulz/simulation/model/get","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteSimulation"]}},{{"path":"/rulz/simulation/jsons","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteSimulation"]}},{{"path":"/rulz/list","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteList"]}},{{"path":"/rulz/function","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteFunction"]}},{{"path":"/rulz/function/test","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteFunction"]}},{{"path":"/rulz/formula","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteFormula"]}},{{"path":"/rulz/instrument","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteInstrument"]}},{{"path":"/rulz/instrument/file/delete","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteInstrument"]}},{{"path":"/rulz/simulate/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","RuleSimulate"]}},{{"path":"/rulz/install/publication/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","RuleInstall"]}},{{"path":"/rulz/uninstall/publication/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","RuleInstall"]}},{{"path":"/snapshot/get/all","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/export","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/export/*","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/import","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/create/*","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/use","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/delete/*","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/snapshot/edit/*","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/rulz/drls_new","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/rulz/drls","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/rulz/drls/*/*","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}},{{"path":"/rulz/test","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","RuleSimulate"]}},{{"path":"/rulz/test/data","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","RuleSimulate"]}},{{"path":"/rulz/test/install","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","RuleInstall"]}},{{"path":"/rulz/test/uninstall","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","RuleInstall"]}},{{"path":"/rulz/test/list","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadPublication"]}},{{"path":"/rulz/install/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","RuleInstall"]}},{{"path":"/rulz/uninstall/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","RuleInstall"]}},{{"path":"/rulz/drl/rule","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadRule"]}},{{"path":"/rulz/drl/table","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadTable"]}},{{"path":"/rulz/drl/simulation","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadSimulation"]}},{{"path":"/rulz/files/*/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteInstrument"]}},{{"path":"/rulz/rule/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadRule"]}},{{"path":"/rulz/table/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadTable"]}},{{"path":"/rulz/catalog/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadCatalog"]}},{{"path":"/rulz/simulation/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadSimulation"]}},{{"path":"/rulz/entity/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadEntity"]}},{{"path":"/rulz/list/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadList"]}},{{"path":"/rulz/instrument/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadInstrument"]}},{{"path":"/rulz/function/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadFunction"]}},{{"path":"/rulz/formula/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadFormula"]}},{{"path":"/rulz/publication/all","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadPublication"]}},{{"path":"/rulz/rule/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteRule"]}},{{"path":"/rulz/table/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteTable"]}},{{"path":"/rulz/catalog/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteCatalog"]}},{{"path":"/rulz/simulation/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteSimulation"]}},{{"path":"/rulz/entity/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteEntity"]}},{{"path":"/rulz/list/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteList"]}},{{"path":"/rulz/instrument/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteInstrument"]}},{{"path":"/rulz/function/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteFunction"]}},{{"path":"/rulz/formula/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WriteFormula"]}},{{"path":"/rulz/publication/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WritePublication"]}},{{"path":"/rulz/drls/remove","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","WritePublication"]}},{{"path":"/rulz/*/notincatalog","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadRule","ReadTable","ReadCatalog"]}},{{"path":"/rulz/rule/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadRule"]}},{{"path":"/rulz/table/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadTable"]}},{{"path":"/rulz/catalog/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadCatalog"]}},{{"path":"/rulz/simulation/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadSimulation"]}},{{"path":"/rulz/entity/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadEntity"]}},{{"path":"/rulz/list/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadList"]}},{{"path":"/rulz/instrument/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadInstrument"]}},{{"path":"/rulz/function/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadFunction"]}},{{"path":"/rulz/formula/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadFormula"]}},{{"path":"/rulz/publication/*","user_profiles":["Aplicacion","ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR","ReadPublication"]}},{{"path":"/auditory/registered_users","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/auditory/search","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/auditory/getdata/*","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/auditory/getregistry/*","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/api/register_key","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/api/all_keys","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/api/delete_key/*","user_profiles":["ADMINISTRADOR","Usuario"],"user_roles":["ADMINISTRADOR"]}},{{"path":"/rulz/count/*","user_profiles":["ADMINISTRADOR","EDITOR","PUBLICADOR","Usuario"],"user_roles":["PUBLICADOR","ADMINISTRADOR","EDITOR"]}}]

MODULES_MATRIX_SERVICE="/security/matrix"

TTL_KEY_WEBUSER=1000000000
TTL_KEY_BACKOFFICEUSER=1000000000

SSO_DATA={{"token_name":"Auth-Token","user_name":"User","urls":{{"verify": "http://suma-test.aduana.gob.bo/b-sso/rest/autenticar/verify","user_data": "http://suma-test.aduana.gob.bo/b-sso/rest/usuarios/oce","user_roles": "http://suma-test.aduana.gob.bo/b-sso/rest/autenticar/verificar"}},"roles_path": "usuario.roles","roles_name": "nombreRole","roles_reference": {{"EDITOR": ["USER"],"ADMINISTRADOR": ["EXP_TECAFORADOR"],"PUBLICADOR": ["OCE_REPRESENTANTE_PRINCIPAL"]}},"user_data_ref": {{"id": "perfilUsuario.nroDocumento","username": "nombre","email": "email","organization_id": "nombreUsuario"}}}}

SSO_ENABLED=False

OAUTH_CREDENTIALS={{'facebook':{{'id': '928145690594469','secret':'6303b300c95724d81aefc0477484dc06'}},'google':{{'id': '663758850100-crm91b0n542s7f1ed0qdp1a88uu33ltl.apps.googleusercontent.com','secret':'7t01cbWNfbEQf1TElaZYiV1v'}},'twitter':{{'id':'XkdHrubmsgCfWOr14JVe0bslO','secret':'zkzPn3gbH0GaYgvNAkAgmdoRyTG2bfoKXWwKFXHWVmCuOvGvFa'}}}}

OAUTH_ENABLED=True

'''.format(app_path, luzia_port, data, mongo_host, mongo_port, roles_url, sub_organization_url, rule_server, rule_server_dialect, mongo_sec_active, mongo_user, mongo_pass, mongo_sec_path)

ensure_dir(data)
ensure_dir(data + os.sep + "conf")
ensure_dir(data + os.sep + "wsgis")
ensure_dir(data + os.sep + "bin")
ensure_dir(data + os.sep + "log")
ensure_dir(data + os.sep + "etc")
ensure_dir(data + os.sep + "tmp")
ensure_dir(data + os.sep + "plugins")
ensure_dir(data + os.sep + "plugins" + os.sep + "validators")
ensure_dir(data + os.sep + "storage")
ensure_dir(data + os.sep + "storage" + os.sep + "bucket")
ensure_dir(data + os.sep + "storage" + os.sep + "snapshots")
ensure_dir(data + os.sep + "storage" + os.sep + "signed")


file_conf = open(data + os.sep + "conf" + os.sep + "arg-properties.cfg", "w")
file_conf.write(arg_config)
file_conf.close()

logger_conf = '''---
formatters:
  extend:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  simple:
    format: "%(levelname)s  - %(asctime)s - %(message)s"
handlers:
  audit:
    class: logging.handlers.RotatingFileHandler
    filename: {0}/log/arg2-audit.log
    formatter: extend
    level: DEBUG
  console:
    class: logging.StreamHandler
    formatter: simple
    level: DEBUG
    stream: "ext://sys.stdout"
  error:
    class: logging.handlers.RotatingFileHandler
    filename: {0}/log/arg2-error.log
    formatter: simple
    level: DEBUG
loggers:
  arg_audit:
    handlers:
      - audit
    level: INFO
    propagate: false
  arg_log:
    handlers:
      - error
    level: INFO
    propagate: false
version: 1
'''.format(data)

file_conf = open(data + os.sep + "conf" + os.sep + "arg-logger-conf.yaml", "w")
file_conf.write(logger_conf)
file_conf.close()

with open(data + os.sep + "bin" + os.sep + "start-arg.sh", "w") as file_bin:
    raw_binary = '''
#/bin/sh
export ARG_SETTINGS="{0}"
cd {1}/src
python initserver.py
'''.format(data + os.sep + "conf/arg-properties.cfg", os.getcwd())
    file_bin.write(raw_binary)

os.system('clear')
print bcolors.OKBLUE
print '''
 La instalacion se ha realizado en forma exitosa. Para iniciar la aplicacion debe realizar los siguientes pasos:

 1) Cambiar el propietario del directrio {0} al usuario que ejecutara la aplicacion ya que este directorio debe tener los permisos de lectura/escritura correspondientes
 2) export ARG_SETTINGS={0}/conf/arg-properties.cfg
 3) cd {1}/src
 4) python initserver.py

 Enjoy!
 '''.format(data, os.getcwd())

print bcolors.WHITE
