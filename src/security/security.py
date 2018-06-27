from flask import Blueprint, current_app, jsonify, request, redirect, session, render_template, url_for, flash
from flask_cors import cross_origin
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from functools import wraps
import httplib2 as http
import uuid
import json
import redis
from pymongo import MongoClient
import ldap_service
import fnmatch
from oauth import SERVICES_ROLES_MATRIX, FUNCIONALITY_ROLES_MATRIX
import sso
from random import randint
from init import User, db
from oauth import OAuthSignIn


try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


security = Blueprint('security', "instance_manager")

ROLES_DESCRIPTIONS = {'ADMINISTRADOR': 'Usuario con permisos absolutos sobre la aplicacion', 'PUBLICADOR': 'Usuario autorizado a realizar publicacion de reglas', 'EDITOR': 'Usuario con capacidad de crear reglas pero no de publicarlas'}


def getTokenFromRequest():
    token = request.cookies.get("security_token")
    if token is None:
        token = request.headers.get("Authorization")

    return token


def token_required(func=None):
    def _decorate(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            token = getTokenFromRequest()
            if token is None:
                current_app.logger.error("Acceso denegado: No provee token. Conexion desde {0} ".format(request.remote_addr))
                return jsonify(success=False, msg="Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado"), 428

            return function(*args, **kwargs)

        return wrapped_function

    if func:
        return _decorate(func)

    return _decorate


def secure_service(func=None):
    def _decorate(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):

            if not current_user.is_authenticated:
                oauth_enabled = current_app.config.get('OAUTH_ENABLED')
                if oauth_enabled is True and current_app.config.get('OAUTH_CREDENTIALS') is not None:
                    return render_template("login.html")

                sso_enabled = current_app.config.get('SSO_ENABLED')
                if sso_enabled is True:
                    if not sso.verifySession():
                        return jsonify(success=False, msg="Lo sentimos pero su session SSO no es correcta"), 500

                    redirect(url_for('index'))

            token = getTokenFromRequest()

            if not valid_token(token):
                return jsonify(success=False, msg="Lo sentimos pero su token no es valido"), 428

            if not access_granted(token):
                return jsonify(success=False, msg="No se encuentra autorizado para acceder a este recurso"), 403

            return function(*args, **kwargs)

        return wrapped_function

    if func:
        return _decorate(func)

    return _decorate


def valid_token(token):
    if token is None:
        current_app.logger.error('Acceso denegado: No provee token. Conexion desde ' + request.remote_addr)
        return False

    current_app.logger.debug('Conexion desde: ' + str(request.remote_addr) + ' utilizando el token: ' + str(token))
    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)

    result = r.get(token)

    if result is None:
        current_app.logger.error("Acceso denegado. Intentando acceder a un recurso con un token no valido. Token provisto: " + token)
        return False

    return True


def access_granted(token):
    # check if SERVICE PROTECTION is diactivated, if it's not, grant access to the user
    protection = current_app.config.get('SERVICE_PROTECTION')
    if protection is False:
        current_app.logger.debug("SERVICE_PROTECTION no definido en el CFG, o en False. No se verificaran permisos de acceso a los servicios")
        return True

    # Get the USER_PROFILES_SERVICES_MATRIX in the CFG
    oauth_enabled = current_app.config.get('OAUTH_ENABLED')
    sso_enabled = current_app.config.get('SSO_ENABLED')

    if oauth_enabled is True or sso_enabled is True:
        matrix = SERVICES_ROLES_MATRIX
    else:
        matrix = current_app.config.get('USER_PROFILES_SERVICES_MATRIX')

    # Kick if the USER_PROFILES_SERVICES_MATRIX is not defined in the CFG
    if not matrix:
        current_app.logger.error("USER_PROFILES_SERVICES_MATRIX no definida")
        return False

    # Search for the requested resource in the matrix
    requested_resource = None
    # actual_path = request.path[1:]
    for resource in matrix:
        # if is_alike(resource['path'].split('/'), actual_path.split('/')):
        if fnmatch.fnmatch(request.path, resource['path']):
            requested_resource = resource
            break

    # Kick if the requested resource is not in the CFG Matrix
    if requested_resource is None:
        current_app.logger.error("El path al que se quiere acceder no coincide con ninguno de los paths de los resources definidos en USER_PROFILES_SERVICES_MATRIX")
        return False

    # GET Redis user data by token
    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)
    user = json.loads(r.get(token))

    # LOGGED USER'S ROLES
    rol_ids = [user_roles['rol_id'] for user_roles in user["roles"]]

    # REQUIRED ROLES
    requested_roles = requested_resource.get("user_roles")

    if requested_roles is not None and requested_roles > 0:
        if len(filter(lambda x: x in requested_roles, rol_ids)) > 0:
            return True
    else:
        return True

    return False


def only_production(func=None):
    def _decorate(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            if current_app.config["DEV_MODE"] is not True:
                return jsonify(success=False, msg="Lo sentimos, pero no se pueden crear tokens en un modo de aplicacion que no sea development")

            return function(*args, **kwargs)

        return wrapped_function

    if func:
        return _decorate(func)

    return _decorate


@security.route("/security/test")
@cross_origin(headers=['Content-Type'])
def test():
    return jsonify(success=True, mgs="funciona"), 200


@security.route("/security/token/create/one_shoot", methods=['POST'])
@cross_origin(headers=['Content-Type'])
@only_production
def create_one_shoot_token():

    '''
    Create one shoot token
    '''
    payload = ''
    if request.data is not None:
        payload = json.loads(request.data)

    token = str(uuid.uuid4())

    organization_id = ''
    if 'organization_id' in payload:
        organization_id = payload['organization_id']

    msg = {'uid': 'DEV_USER', 'cn': 'Developer User', 'email': 'dev_user@moorea.io', 'token': token, 'one_shoot': True, 'user_profiles': ['Administrador', 'Operador'], 'roles': ['cn=Design', 'cn=Developer'], 'payload': payload, 'organization_id': organization_id}

    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)
    r.set(token, json.dumps(msg))

    return jsonify(success=True, result={"token": token, "payload": payload})


@security.route("/security/token/create_and_redirect", methods=["GET"])
@cross_origin(headers=['Content-Type'])
def create_token_and_redirect():

    goto = request.args.get('goto')
    organization_id = request.args.get('organization_id')

    code = request.args.get('code')
    if code is not None:
        goto = goto + "?code=" + code

    organization = {"organization_id": organization_id, "organization_description": organization_id}

    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)
    token = str(uuid.uuid4())
    msg = {
        "uid": "WEBUSER",
        "cn": "Anonymous User",
        "email": "anonymous@moorea.io",
        "token": token,
        "one_shoot": True,
        "user_profiles": [{"profile_id": "OPERADOR", "profile_description": "Operador"}],
        "roles": [{"rol_id": "WEB", "rol_description": "Web"}],
        "organization": organization,
        "payload": {"organization": organization}
    }

    r.set(token, json.dumps(msg))

    TTL_KEY_WEBUSER = 300

    if current_app.config.get("TTL_KEY_WEBUSER") is not None:
        TTL_KEY_WEBUSER = current_app.config.get("TTL_KEY_WEBUSER")

    r.expire(token, TTL_KEY_WEBUSER)

    redirect_to = redirect(goto)
    response = current_app.make_response(redirect_to)

    if current_app.config.get('DOMAIN'):
        domain = current_app.config.get('DOMAIN')
    else:
        domain = current_app.config.get('IMANAGER_DOMAIN')

    response.set_cookie("security_token", value=token, domain=domain)

    return response, 302


@security.route("/security/token/create", methods=["POST"])
@cross_origin(headers=['Content-Type'])
def create_token():

    payload = json.loads(request.data)
    token = str(uuid.uuid4())

    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)

    oauth_enabled = current_app.config.get('OAUTH_ENABLED')
    sso_enabled = current_app.config.get('SSO_ENABLED')

    if oauth_enabled is True or sso_enabled is True:
        if not current_user.is_authenticated:
            if oauth_enabled is True:
                return redirect(url_for('index'))

            print 'User autenticaded', current_user.is_authenticated

            if sso_enabled is True and not current_user.is_authenticated:
                if not loginSSO():
                    print "no se logea"

        msg = {
            'uid': 'OAUTH_USER',
            'cn': current_user.nickname,
            'email': current_user.email,
            'token': token,
            'one_shoot': False,
            'roles': [dict([('rol_id', this_id), ('rol_description', ROLES_DESCRIPTIONS[this_id])]) for this_id in current_user.roles],
            'organization': {'organization_id': ('testing_', current_user.organization_id)[current_user.organization_id is not None]}
            # 'organization': {'organization_id': ('testing', current_user.organization_id)[current_user.organization_id is None]}
        }

    else:
        # Get the USER_DEV_MODE in the CFG
        msg = current_app.config.get('USER_DEV_MODE')

    if msg is None:
        msg = {
            "uid": "DEV_USER",
            "cn": "Developer User",
            "email": "dev_user@moorea.io",
            "token": token,
            "one_shoot": False,
            "user_profiles": [{"profile_id": "ADMINISTRADOR", "profile_description": "Administrador"}, {"profile_id": "OPERADOR", "profile_description": "Operador"}],
            "roles": [{"rol_id": "DESIGN", "rol_description": "Design"}, {"rol_id": "DEVELOPER", "rol_description": "Developer"}],
            "organization": {"organization_id": "0079_000", "organization_description": "Dev Org"},
            "filter": {"filter_id": "DEFAULT", "filter_description": "Default"},
            "payload": payload
        }

    if request.cookies.get('moorea_auth') is not None:
        headers_virgilio = {'Authorization': current_app.config['KEY_SSO']}

        target = urlparse(current_app.config['URL_SSO'] + "/get_user_info/" + request.cookies.get('moorea_auth'))
        method = 'GET'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), method, '')

        sso_token_info = json.loads(content)
        user_info = ldap_service.get_user_data(sso_token_info['result']['userid'])

        msg['uid'] = sso_token_info['result']['userid']
        msg['email'] = user_info['mail']
        msg['cn'] = user_info['cn']

        query = {
            "only_fields": [],
            "query": "id:{2} AND application:{0} AND userid:{1}".format(current_app.config['APPLICATION_ID'], sso_token_info['result']['userid'], payload['enrollment_id'])
        }

        target = urlparse(current_app.config["VIRGILIO_URL"] + "/enrollments/search")
        method = 'POST'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), method, json.dumps(query), headers_virgilio)
        result = json.loads(content)

        new_roles = []
        new_user_profiles = []

        for enroll in result['result']['hits']:
            new_roles = [x for x in enroll['_source']['data']['rol']]

        for enroll in result['result']['hits']:
            new_user_profiles = [x for x in enroll['_source']['data']['user_profiles']]

        msg['roles'] = new_roles
        msg['user_profiles'] = new_user_profiles

        if enroll['_source']['data'].get('organization'):
            msg['organization'] = enroll['_source']['data']['organization']
        else:
            msg['organization'] = {'organization_id': enroll['_source']['data']['organization_id'], 'organization_description': enroll['_source']['data']['organization_description']}

        if enroll['_source']['data'].get('filter'):
            msg['filter'] = enroll['_source']['data']['filter']

        if enroll['_source']['data'].get('office'):
            msg['office_id'] = enroll['_source']['data']['office']['office_id']
            msg['office_description'] = enroll['_source']['data']['office']['office_description']

    else:
        if oauth_enabled is not True and sso_enabled is not True and current_app.config.get('DEV_MODE') is not True:
            msg = payload

    r.set(token, json.dumps(msg))

    # Verify is TTL KEYS is set. Else set default value

    TTL_KEY_WEBUSER = randint(300, 1800)

    if current_app.config.get("TTL_KEY_WEBUSER") is not None:
        TTL_KEY_WEBUSER = current_app.config.get("TTL_KEY_WEBUSER")

    elif current_app.config.get("TTL_KEY_BACKOFFICEUSER") is not None:
        TTL_KEY_WEBUSER = current_app.config.get("TTL_KEY_BACKOFFICEUSER")

    r.expire(token, TTL_KEY_WEBUSER)

    return jsonify(success=True, result={"token": token, "payload": payload})


@security.route("/security/user/get_roles", methods=["GET"])
@cross_origin(headers=['Content-Type'])
def user_get_roles():
    try:
        token = getTokenFromRequest()
        if token is None:
                current_app.logger.error("Acceso denegado: No provee token. Conexion desde " + request.remote_addr)
                return jsonify(success=False, msg="Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado"), 428

        result = get_token()
        return jsonify(success=True, data=result)
    except Exception:
        return jsonify(success=False, msg="Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado"), 428


def get_token():
    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)

    token = None

    if getTokenFromRequest() is not None:
        token = getTokenFromRequest()
    elif session.get('token_id') is not None:
        token = session['token_id']
    if token is None:
        raise Exception('Token required')

    red_token = r.get(token)

    if red_token is None:
        raise Exception('Token required')

    return json.loads(red_token)


@security.route("/security/matrix", methods=["GET"])
@cross_origin(headers=['Content-Type'])
@token_required
def get_available_modules():

    try:
        user = get_token()
    except Exception:
        return jsonify(success=False, msg="Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado"), 428

    oauth_enabled = current_app.config.get('OAUTH_ENABLED')
    sso_enabled = current_app.config.get('SSO_ENABLED')

    if oauth_enabled is True or sso_enabled is True:
        matrix = FUNCIONALITY_ROLES_MATRIX
    else:
        matrix = current_app.config.get("USER_PROFILES_MODULES_MATRIX")

    rols_ids = [user_profile['rol_id'] for user_profile in user["roles"]]

    available_modules = list(set([module for module, module_profiles in matrix for profile in rols_ids if profile in module_profiles]))

    current_app.logger.debug(available_modules)

    return jsonify(success=True, result=available_modules, msg="La operacion se ha realizado con exito")


@security.route("/security/get_organizations", methods=["GET"])
@cross_origin(headers=['Content-Type'])
def user_get_organizations():

    if request.cookies.get('moorea_auth') is not None:
        # WE GET THIS ORGANIZATIONS FROM LDAP.

        headers = {'Authorization': "5b341f83-5359-412f-8a20-84e39a3a281c"}

        target = urlparse(current_app.config['URL_SSO'] + "/get_user_info/" + request.cookies.get('moorea_auth'))
        method = 'GET'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), method, '', headers)

        user_info = json.loads(content)
        # current_app.logger.debug("Informacion de Usuario: " + content)
        query = {
            "only_fields": [],
            "query": "application:{0} AND userid:{1}".format(current_app.config['APPLICATION_ID'], user_info['result']['userid'])
        }

        target = urlparse(current_app.config["VIRGILIO_URL"] + "/enrollments/search")
        method = 'POST'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), method, json.dumps(query), headers)
        result = json.loads(content)

        if result['success'] is False:
            return jsonify(success=True, msg="Lo sentimos pero no posee permisos para poder acceder a la aplicacion"), 403

        if result['success'] is True and result['result']['total'] == 0:
            return jsonify(success=True, msg="Lo sentimos pero no posee permisos para poder acceder a la aplicacion"), 403

        organizations = []

        for enroll in result['result']['hits']:
            if enroll['_source']['data'].get("organization") != None:
                organizations.append({"organization_id": enroll['_source']['data']['organization']['organization_id'], "organization_description": enroll['_source']['data']['organization']['organization_description']})
            else:
                # PATCH to REMOVE  @deprecated. remove when arDifusion is deploy in Server Test
                organizations.append({"organization_id": enroll['_source']['data']['organization_id'], "organization_description": enroll['_source']['data']['organization_description']})

        return jsonify(success=True, result=organizations, msg="La operacion se ha realizado con exito")

    else:
        if current_app.config['DEV_MODE']:
            organizations = [
                {"organization_id": "0079_000", "organization_description": "Organizacion 1"},
                {"organization_id": "0079_000", "organization_description": "Organizacion 2"}
            ]
            return jsonify(success=True, result=organizations, msg="La operacion se ha realizado con exito")
        else:
            msg = {
                "url_return": current_app.config['URL_SSO'] + "/#/login?goto=" + current_app.config['URL_IMANAGER']
            }

            return jsonify(success=False, msg='Lo sentimos pero no posee credenciales validas para utilizar el servicio. Por favor genere y presente credenciales validas para poder acceder al servicio', result=msg), 302


@security.route("/security/get_enrollments", methods=["GET"])
@cross_origin(headers=['Content-Type'])
def user_get_enrollments():

    if request.cookies.get('moorea_auth') != None:
        # WE GET THIS ORGANIZATIONS FROM LDAP.

        headers = {'Authorization': "5b341f83-5359-412f-8a20-84e39a3a281c"}

        target = urlparse(current_app.config['URL_SSO'] + "/get_user_info/" + request.cookies.get('moorea_auth'))
        method = 'GET'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), method, '', headers)

        user_info = json.loads(content)
        # current_app.logger.debug("Informacion de Usuario: " + content)
        query = {
            "only_fields": [],
            "query": "application:{0} AND userid:{1}".format(current_app.config['APPLICATION_ID'], user_info['result']['userid'])
        }

        target = urlparse(current_app.config["VIRGILIO_URL"] + "/enrollments/search")
        method = 'POST'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), method, json.dumps(query), headers)
        result = json.loads(content)

        if result['success'] is False:
            return jsonify(success=True, msg="Lo sentimos pero no posee permisos para poder acceder a la aplicacion"), 403

        if result['success'] is True and result['result']['total'] == 0:
            return jsonify(success=True, msg="Lo sentimos pero no posee permisos para poder acceder a la aplicacion"), 403

        # organizations = []

        enrollments = [x['_source']['data'] for x in result['result']['hits']]

        for enroll in enrollments:
            # if enroll['_source']['data'].get("organization") !=None:
            #    organizations.append({"organization_id":enroll['_source']['data']['organization']['organization_id'],"organization_description":enroll['_source']['data']['organization']['organization_description']})
            if enroll.get("organization_id") is not None:
                # PATCH to REMOVE  @deprecated. remove when arDifusion is deploy in Server Test
                organization = {"organization_id": enroll['organization_id'], "organization_description": enroll['organization_description']}
                enroll["organization"] = organization
                # organizations.append({"organization_id":enroll['_source']['data']['organization_id'],"organization_description":enroll['_source']['data']['organization_description']})

        return jsonify(success=True, result=enrollments, msg="La operacion se ha realizado con exito")

    else:
        if current_app.config['DEV_MODE']:
            enrollments = [
                {
                    "id": "user1",
                    "userid": "DEV_USER",
                    "status": "ACTIVE",
                    "application": "appdemo",
                    "organization": {"organization_id": "0079_000", "organization_description": "Organizacion1"},
                    "filter": {"filter_id": "DEFAULT", "filter_description": "Default"},
                    "user_profiles": [{"profile_id": "ADMINISTRADOR", "profile_description": "Administrador"}, {"profile_id": "OPERADOR", "profile_description": "Operador"}],
                    "rol": [{"rol_id": "ADMINISTRADOR", "rol_description": "Administrador"}, {"rol_id": "OPERADOR", "rol_description": "Operador"}],
                    "enrollment_form": {}
                },
                {
                    "id": "user2",
                    "userid": "DEV_USER",
                    "status": "ACTIVE",
                    "application": "appdemo",
                    "organization": {"organization_id": "0079_001", "organization_description": "Organizacion2`"},
                    "filter": {"filter_id": "DEFAULT", "filter_description": "Default"},
                    "user_profiles": [{"profile_id": "ADMINISTRADOR", "profile_description": "Administrador"}, {"profile_id": "OPERADOR", "profile_description": "Operador"}],
                    "rol": [{"rol_id": "ADMINISTRADOR", "rol_description": "Administrador"}, {"rol_id": "OPERADOR", "rol_description": "Operador"}],
                    "enrollment_form": {}
                }
            ]

            return jsonify(success=True, result=enrollments, msg="La operacion se ha realizado con exito")
        else:
            msg = {
                "url_return": current_app.config['URL_SSO'] + "/#/login?goto=" + current_app.config['URL_IMANAGER']
            }

            return jsonify(success=False, msg='Lo sentimos pero no posee credenciales validas para utilizar el servicio. Por favor genere y presente credenciales validas para poder acceder al servicio', result=msg), 302


@security.route("/security/get_organizations_and_filters", methods=["GET"])
@cross_origin(headers=['Content-Type'])
def user_get_organizations_and_filters():

    current_app.logger.debug("MOOREA AUTH:")
    current_app.logger.debug(request.cookies.get('moorea_auth'))

    if request.cookies.get('moorea_auth') != None:

        # WE GET THIS ORGANIZATIONS FROM VIRGILIO.

        headers = {'Authorization': current_app.config['KEY_SSO']}

        target = urlparse(current_app.config['URL_SSO'] + "/get_user_info/" + request.cookies.get('moorea_auth'))
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), 'GET', '', headers)

        user_info = json.loads(content)

        current_app.logger.debug("USER INFO:")
        current_app.logger.debug(user_info)

        query = {
            "only_fields": [],
            "size": 100,
            "from": 0,
            "query": "application:{0} AND userid:{1}".format(current_app.config['APPLICATION_ID'], user_info['result']['userid'])
        }

        target = urlparse(current_app.config["VIRGILIO_URL"] + "/enrollments/search")
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(target.geturl(), 'POST', json.dumps(query), headers)

        # TODO: Devolver el user info de ldap en el token

        try:

            result = json.loads(content)
        except Exception, ex:
            current_app.logger.exception(ex)
            current_app.logger.debug("VIRGILIO_URL: " + current_app.config["VIRGILIO_URL"])
            current_app.logger.debug(content)
            return jsonify(success=False, msg="Lo sentimos pero no se pudieron obtener los datos de virgilio. Para mas informacion consulte el log de sistema"), 500

        if result['success'] is False:
            current_app.logger.debug(result['msg'])
            return jsonify(success=True, msg="Lo sentimos pero no posee permisos para poder acceder a la aplicacion. Error: " + result['msg']), 403

        if result['success'] is True and result['result']['total'] == 0:
            return jsonify(success=True, msg="Lo sentimos pero no posee permisos para poder acceder a la aplicacion"), 403

        enrollments = [x['_source']['data'] for x in result['result']['hits']]

        organizations = []
        for enroll in enrollments:
            # PATCH to REMOVE  @deprecated. remove when arDifusion is deploy in Server Test
            # -----------------------------------------------------------------------------
            if enroll.get("organization_id") is not None:
                organization = {"organization_id": enroll['organization_id'], "organization_description": enroll['organization_description']}
                enroll["organization"] = organization
            # -----------------------------------------------------------------------------
            organizations.append(enroll["organization"])

        uniq_organizations = {v['organization_id']: v for v in organizations}.values()

        for org in uniq_organizations:
            org['filters'] = []
            for enroll in enrollments:
                if org['organization_id'] == enroll['organization']['organization_id']:
                    if not enroll.get('filter'):
                        enroll['filter'] = {"filter_id": "DEFAULT", "filter_description": "Default"}
                    enroll['filter']['enrollment_id'] = enroll['id']
                    org['filters'].append(enroll['filter'])
        current_app.logger.debug(uniq_organizations)

        return jsonify(success=True, result=uniq_organizations, msg="La operacion se ha realizado con exito")

    else:
        if current_app.config['DEV_MODE']:

            organizations = [
                {
                    'organization_id': 'sipro',
                    'filters': [
                        {
                            'filter_description': 'Filtro1',
                            'filter_id': 'FILTRO1',
                            'enrollment_id': "abcdefghijklmnopqrstuvwxyz"
                        },
                        {
                            'filter_description': 'Filtro2',
                            'filter_id': 'FILTRO2',
                            'enrollment_id': "abcdefghijklmnopqrstuvwxyz"
                        }
                    ],
                    'organization_description': 'Organizacion2'
                }
            ]

            return jsonify(success=True, result=organizations, msg="La operacion se ha realizado con exito")
        else:
            msg = {
                "url_return": current_app.config['URL_SSO'] + "/#/login?goto=" + current_app.config['URL_IMANAGER']
            }

            return jsonify(success=False, msg='Lo sentimos pero no posee credenciales validas para utilizar el servicio. Por favor genere y presente credenciales validas para poder acceder al servicio', result=msg), 302


@security.route("/security/organizations", methods=["POST"])
@cross_origin(headers=['Content-Type'])
@only_production
def organization_create():
    client = MongoClient('localhost', 27017)

    if client.security.organizations.find(json.loads(request.data)).count(True) > 0:
        return jsonify(success=False, msg='Lo sentimos pero la organizacion que quiere crear ya existe'), 422

    message = json.loads(request.data)
    message['owner'] = 'DEV_USER'
    client.security.organizations.insert(message)
    return jsonify(success=True, msg='La operacion se ha realizado con exito')


@security.route("/security/organizations", methods=["GET"])
@cross_origin(headers=['Content-Type'])
@only_production
def organization_get_all():
    client = MongoClient('localhost', 27017)
    result = []
    for element in client.security.organizations.find({}, {"_id": False}):
        result.append(element)

    return jsonify(success=True, result=result)


@security.route("/security/organizations/<id>", methods=["GET"])
@cross_origin(headers=['Content-Type'])
@only_production
def organization_get_by_id(id):
    client = MongoClient('localhost', 27017)
    result = []

    for element in client.security.organizations.find({'organizacion_id': id, 'owner': 'DEV_USER'}, {"_id": False}):
        result.append(element)

    return jsonify(success=True, result=result)


@security.route("/security/error/mirror/<code>", methods=['GET'])
@cross_origin(headers=['Content-Type'])
def error_mirror(code):
    return jsonify(success=True, msg='Se retorna con el codigo de error: ' + code), code


def loginSSO(headersParams=None):

    if not sso.verifySession(headersParams):
        return False

    userData = sso.userData(headersParams)

    if userData is None:
        return False

    social_id = userData.get('id')
    username = userData.get('username')
    email = userData.get('email')
    organization_id = userData.get('organization_id')

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = User.query.filter(User.social_id == social_id).first()

    if not user:
        roles = sso.userRoles(headersParams)
        user = User(social_id=social_id, nickname=username, email=email, organization_id=organization_id, roles=roles)
        db.session.add(user)
        db.session.flush()

    if login_user(user):
        session.permanent = True

    return True


@security.route('/authorize/<provider>')
def oauth_authorize(provider):

    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@security.route('/callback/<provider>')
def oauth_callback(provider):

    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, organization_id = oauth.callback()

    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = User.query.filter(User.social_id == social_id).first()

    if not user:
        user = User(social_id=social_id, nickname=username, email=email, organization_id=organization_id, roles=[('EDITOR', 'ADMINISTRADOR')[current_app.config.get('DEV_MODE') is True]])
        db.session.add(user)
        db.session.flush()
    if login_user(user):
        session.permanent = True

    return redirect(url_for('index'))
