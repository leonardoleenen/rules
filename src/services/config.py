# -*- coding: UTF-8 -*-
from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin
import json
import os
import base64
from security.security import secure_service

config = Blueprint('config', "luzia-rulz")

ALLOWED_KEYS = ['DEBUG_MODE', 'RULE_SERVER', 'RULE_SERVER_VALIDATE', 'RULE_SERVER_BASE', 'RULE_SERVER_TEST', 'RULE_SERVER_INSTALL', 'RULE_SERVER_UNISTALL', 'RULE_SERVER_LIST', 'MONGO_HOST', 'MONGO_PORT', 'APP_PATH', 'TMP_FOLDER', 'LOGGER_CONFIG', 'FILE_STORAGE_BUCKET_PATH', 'FILE_STORAGE_SNAPSHOTS', 'DEV_MODE', 'FILTER_BY_ROLES', 'LOAD_USER_DATA_URL', 'FETCH_SUBORGS_URL', 'MODULES_MATRIX_SERVICE', 'HANDLED_BY_DIRECTOR', 'TTL_KEY_WEBUSER', 'OAUTH_CREDENTIALS', 'OAUTH_ENABLED', 'SERVICE_PROTECTION', 'AUTO_VERSION', 'NEED_INSTRUMENTS']


@config.route('/config/alive')
@cross_origin(headers=['Content-Type'])
@secure_service
def alive():
	return 'its alive'


# Obtiene el archivo de configuracion de la aplicacion
@config.route('/config', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get_config():
	try:
		f = open(os.environ["ARG_SETTINGS"])
		content = base64.b64encode(f.read())
		print content
		f.close()
		return jsonify(success=True, message='Exito al leer el archivo de configuracion', response=content)
	except Exception, e:
		current_app.logger.error('Se produjo un error : ' + str(e))
		return jsonify(success=False, message='Se produjo un error al leer el archivo de configuracion', response=str(e)), 500


# Obtiene el archivo de configuracion de la aplicacion como un arreglo
@config.route('/config/as_array', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get_config_as_array():
	try:
		f = open(os.environ["ARG_SETTINGS"])
		content = f.readlines()
		f.close()
		return jsonify(success=True, message='Exito al leer el archivo de configuracion', response=content)
	except Exception, e:
		current_app.logger.error('Se produjo un error : ' + str(e))
		return jsonify(success=False, message='Se produjo un error al leer el archivo de configuracion', response=str(e)), 500


# Obtiene el archivo de configuracion de la aplicacion como un diccionario
@config.route('/config/as_dict', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get_config_as_dict():
	try:
		conf = confAsDict()

		for key in conf:
			conf[key] = parseConfigValue(conf[key])

		return jsonify(success=True, message='Exito al leer el archivo de configuracion', response=conf)
	except Exception, e:
		current_app.logger.error('Se produjo un error : ' + str(e))
		return jsonify(success=False, message='Se produjo un error al leer el archivo de configuracion', response=str(e)), 500


@config.route('/config/save/dict', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def save_config_as_dict():
	try:
		info = json.loads(request.data)
		data = []

		conf = confAsDict(False)

		for key in info:

			if key not in ALLOWED_KEYS:
				continue

			if info[key]['type'] == 'string':
				conf[key] = '"' + info[key]['value'] + '"'
			else:
				conf[key] = info[key]['value']

		for key in conf:

			data.append(str(key) + '=' + str(conf[key]))

		with open(os.environ["ARG_SETTINGS"], "w") as f:
			f.write('\n\n'.join(data))

		current_app.config.from_envvar('ARG_SETTINGS')
		return jsonify(success=True, message='Exito al actualizar las configuraciones del sistema', response=None)
	except Exception, e:
		current_app.logger.error('Se produjo un error : ' + str(e))
		return jsonify(success=False, message='Se produjo un error al guardar el archivo de configuracion ' + str(e.message), response=str(e)), 500


# Guarda el archivo de configuracion de la aplicacion
@config.route('/config', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def set_config():
	try:
		f = open(os.environ["ARG_SETTINGS"], "w")
		f.write(base64.b64decode(request.data))
		f.close()
		current_app.config.from_envvar('ARG_SETTINGS')
		return jsonify(success=True, message='Exito al guardar el archivo de configuracion', response='')
	except Exception, e:
		current_app.logger.error('Se produjo un error : ' + str(e))
		return jsonify(success=False, message='Se produjo un error al guardar el archivo de configuracion', response=str(e)), 500


# Gets the initial configuration
@config.route('/config/initial', methods=['GET'])
@cross_origin(headers=['Content-Type'])
def getInitialConfig():
    try:

        ini = {}

        ini['matrixurl'] = current_app.config.get('MODULES_MATRIX_SERVICE')
        if ini['matrixurl'] is None:
            ini['matrixurl'] = '/security/matrix'

        ini['director'] = current_app.config.get('HANDLED_BY_DIRECTOR')
        if ini['director'] is None:
            ini['director'] = False

        ini['instruments'] = current_app.config.get('NEED_INSTRUMENTS')
        if ini['instruments'] is None:
            ini['instruments'] = True

        ini['auto_version'] = current_app.config.get('AUTO_VERSION')
        if ini['auto_version'] is None:
            ini['auto_version'] = True

        ini['wizard'] = current_app.config.get('WIZARD')
        if ini['wizard'] is None:
            ini['wizard'] = False

        ini['sso'] = current_app.config.get('SSO_ENABLED')
        if ini['sso'] is None:
            ini['sso'] = False

        return jsonify(success=True, message='Exito al recuperar la configuración de inicio', response=ini)

    except KeyError as ke:
        return jsonify(success=False, message='La clave ' + str(ke) + 'no se encuentra definida', response={}), 200
    except Exception, e:
        current_app.logger.exception('Se produjo un error al leer el archivo de configuracion: ' + str(e))
        return jsonify(success=False, message='Error al recuperar el valor', response={}), 500


# Gets the value of the given key from the configuration file
@config.route('/config/<key>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get_config_value(key):
	try:
		try:
			message = json.loads(current_app.config[key])
		except ValueError as e:
			message = current_app.config[key]
		except TypeError as e:
			message = current_app.config[key]
		return jsonify(success=True, message='Exito al recuperar el valor', response=message)
	except KeyError:
		return jsonify(success=False, message=key + ' no es una clave de configuracion valida', response=None), 200
	except Exception, e:
		current_app.logger.exception('Se produjo un error al leer el archivo de configuracion: ' + str(e))
		return jsonify(success=False, message='Error al recuperar el valor', response=str(e)), 500


def confAsDict(onlie_alowed=True):

	with open(os.environ["ARG_SETTINGS"], 'r') as f:
		conf = {}
		for line in f:
			if line is None or line == ' ' or line == '\n' or line.strip() == '' or indexOf(line, '#') == 0:
				continue
			txt = line.split('=')

			if onlie_alowed and txt[0] not in ALLOWED_KEYS:
				continue

			conf[txt[0]] = txt[1].replace('\n', '')

	return conf


def indexOf(string, value):

	try:
		i = string.index(value)
	except ValueError:
		i = -1

	return i


def parseConfigValue(value):
	if value == 'True':
		return {'value': True, 'type': 'boolean'}

	elif value == 'False':
		return {'value': False, 'type': 'boolean'}

	elif indexOf(value, '"') == 0:
		return {'value': value.replace('"', ''), 'type': 'string'}

	elif indexOf(value, "'") == 0:
		return {'value': value.replace("'", ''), 'type': 'string'}

	else:
		try:
			int(value)
			return {'value': int(value), 'type': 'integer'}
		except ValueError:
			return {'value': value, 'type': 'json'}
