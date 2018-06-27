# -*- coding: UTF-8 -*-
'''
:Authors
	- Enzo D. Grosso
'''

from flask import Blueprint, current_app, request
from flask_cors import cross_origin
from security.security import secure_service
from utils import repo
from time import time as timestamp
from werkzeug import secure_filename
from datetime import datetime
from utils.toolbox import ensure_dir
from logging import getLogger
import redis
import os
import uuid
import json
import base64

snapshots = Blueprint('snapshots', "luzia-rulz")

INSTANCE = 'snapshot'
RLZ_INSTANCE = 'rulz'
COLECTION_RULES = 'rules'
COLECTION_ENTITYS = 'entitys'
COLECTION_CATALOGS = 'catalogs'
COLECTION_TABLES = 'tables'
COLECTION_SIMULATIONS = 'simulations'
COLECTION_LISTS = 'lists'
COLECTION_FUNCTIONS = 'functions'
COLECTION_FORMULAS = 'formulas'
COLECTION_INSTRUMENTS = 'instruments'
COLECTION_DRLS = 'drls'
COLECTION_SNAPSHOTS = 'snapshots'


@snapshots.route('/snapshot/create/<name>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def createSnapshot(name):
	try:
		name = make(name=name, register=True, description=request.data)
		return json.dumps({'success': True, 'response': name, 'message': 'Exito'}), 200
	except Exception as e:
		getLogger('arg_log').exception(e)
		return json.dumps({'success': False, 'response': None, 'message': e.message}), 200


@snapshots.route('/snapshot/get/all', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getAllSnapshots():
	try:
		client = repo.get_instance(INSTANCE)

		array = client.get_by_query(COLECTION_SNAPSHOTS, {})

		response = {'message': 'Exito', 'success': True, 'response': array}

	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'message': 'Ocurrio un error ' + e.message, 'success': False, 'response': []}
	return json.dumps(response), 200


@snapshots.route('/snapshot/export', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getExport():
	try:
		name = make()

		return downloadSnapshot(name, True)

	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'message': 'Ocurrio un error ' + e.message, 'success': False, 'response': []}
	return json.dumps(response), 200


@snapshots.route('/snapshot/export/<name>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def downloadSnapshot(name, dl=False):
	try:
		data = {}

		filename = secure_filename(name + '.json')

		folder = current_app.config['FILE_STORAGE_SNAPSHOTS'] + '/'

		fi = open(os.path.join(folder, filename), 'r')

		data['name'] = filename

		data['filetype'] = 'application/json'

		data['b64'] = base64.b64encode(fi.read())

		fi.close()

		if dl:
			os.remove(os.path.join(folder, filename))

		response = {'message': 'Exito', 'success': True, 'response': data}
	except IOError as ie:
		getLogger('arg_log').exception(ie)
		if ie.errno == 2:
			message = 'No se ha podido obtener acceso al archivo de snapshot, por favor contacte a su administrador de sistema'
		else:
			message = 'I/O problem ' + str(ie.strerror)
		response = {'message': message, 'success': False, 'response': None}
	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'message': 'Ocurrio un error ' + e.message, 'success': False, 'response': None}
	return json.dumps(response), 200


@snapshots.route('/snapshot/import', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def importSnapshot():
	try:
		data = json.loads(request.data)

		snap = json.loads(base64.b64decode(data['base64']))

		created = create('Anterior_al_import_de_' + data['filename'].rsplit('.', 1)[0], None, 'Snapshot creado al realizar el import del archivo ' + data['filename'])

		dumpColections()

		restore(snap)

		response = {'response': None, 'message': 'Se ha restaurado el estado de ' + data['filename'].rsplit('.', 1)[0] + ' y se ha genereado un snapshot con el estado anterior (' + created + ')', 'success': True}
	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'response': None, 'success': False, 'message': e.message}
	finally:
		return json.dumps(response), 200


@snapshots.route('/snapshot/use', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def useSnapshot():
	try:
		data = json.loads(request.data)

		filename = secure_filename(data['name'] + '.json')

		folder = current_app.config['FILE_STORAGE_SNAPSHOTS'] + '/'

		fi = open(os.path.join(folder, filename), 'r')

		created = create('Anterior_al_import_de_' + data['name'], None, 'Snapshot creado al realizar la restauracion del Snapshot ' + data['name'])

		snap = json.loads(fi.read())

		dumpColections()

		restore(snap)

		response = {'response': None, 'message': 'Se ha restaurado el estado de ' + filename.rsplit('.', 1)[0] + ' y se ha genereado un snapshot con el estado anterior (' + created + ')', 'success': True}
	except IOError as ie:
		getLogger('arg_log').exception(ie)
		if ie.errno == 2:
			message = 'No se ha podido obtener acceso al archivo de snapshot, por favor contacte a su administrador de sistema'
		else:
			message = 'I/O problem ' + str(ie.strerror)
		response = {'message': message, 'success': False, 'response': None}
	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'response': None, 'success': False, 'message': e.message}
	finally:
		return json.dumps(response), 200


@snapshots.route('/snapshot/delete/<id>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def deleteSnapshot(id):
	try:
		client = repo.get_instance(INSTANCE)

		obj = client.get_by_id(COLECTION_SNAPSHOTS, id)

		if obj is None:
			return json.dumps({'message': 'No se ha encontrado el Snapshot solicitado'}), 404

		roles = getRoles()

		if ('user' not in obj or obj['user'] != getUserName()) and 'ADMINISTRADOR' not in roles:
			response = {'response': None, 'success': False, 'message': 'No puede realizar la eliminación de un snapshot que no le pertenece'}
		else:

			filename = secure_filename(obj['name'] + '.json')

			folder = current_app.config['FILE_STORAGE_SNAPSHOTS'] + '/'

			os.remove(os.path.join(folder, filename))

			client.remove(COLECTION_SNAPSHOTS, id)

			response = {'response': None, 'message': 'El Snapshot ' + obj['name'] + ' ha sido borrado', 'success': True}
	except IOError as ie:
		getLogger('arg_log').exception(ie)
		if ie.errno == 2:
			message = 'No se ha podido obtener acceso al archivo de snapshot, por favor contacte a su administrador de sistema'
		else:
			message = 'I/O problem ' + str(ie.strerror)
		response = {'message': message, 'success': False, 'response': None}
	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'response': None, 'success': False, 'message': e.message}
	finally:
		return json.dumps(response), 200


@snapshots.route('/snapshot/edit/<id>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def editSnapshot(id):
	try:
		client = repo.get_instance(INSTANCE)

		obj = client.get_by_id(COLECTION_SNAPSHOTS, id)

		if obj is None:
			return json.dumps({'message': 'No se ha encontrado el Snapshot solicitado'}), 404

		data = json.loads(request.data)

		roles = getRoles()

		if ('user' not in obj or obj['user'] != getUserName()) and 'ADMINISTRADOR' not in roles:
			response = {'response': None, 'success': False, 'message': 'No puede realizar la edición de un snapshot que no le pertenece'}
		else:

			obj['description'] = data['description']

			client.updateRlz(COLECTION_SNAPSHOTS, id, obj)

			response = {'response': None, 'message': 'Operacion exitosa', 'success': True}
	except IOError as ie:
		getLogger('arg_log').exception(ie)
		if ie.errno == 2:
			message = 'No se ha podido obtener acceso al archivo de snapshot, por favor contacte a su administrador de sistema'
		else:
			message = 'I/O problem ' + str(ie.strerror)
		response = {'message': message, 'success': False, 'response': None}
	except Exception as e:
		getLogger('arg_log').exception(e)
		response = {'response': None, 'success': False, 'message': e.message}
	finally:
		return json.dumps(response), 200


def create(name=None, version=None, description=''):
	return make(name, version, True, description)


def make(name=None, version=None, register=False, description=''):
	try:
		client = repo.get_instance(RLZ_INSTANCE)
		snapshot = {}

		tstamp = timestamp()

		if name is None:
			name = 'snapshot_'
		else:
			name = name + '_' + ('', str(version) + '_')[version is not None]

		name = name.replace(' ', '_') + str(datetime.fromtimestamp(tstamp).strftime('%Y-%m-%dT%H-%M-%S'))

		snapshot['id'] = str(uuid.uuid1())

		snapshot['name'] = name

		snapshot['description'] = description

		snapshot['user'] = getUserName()

		snapshot['rules'] = client.get_by_query(COLECTION_RULES, {})

		snapshot['entitys'] = client.get_by_query(COLECTION_ENTITYS, {})

		snapshot['catalogs'] = client.get_by_query(COLECTION_CATALOGS, {})

		snapshot['tables'] = client.get_by_query(COLECTION_TABLES, {})

		snapshot['simulations'] = client.get_by_query(COLECTION_SIMULATIONS, {})

		snapshot['lists'] = client.get_by_query(COLECTION_LISTS, {})

		snapshot['functions'] = client.get_by_query(COLECTION_FUNCTIONS, {})

		snapshot['formulas'] = client.get_by_query(COLECTION_FORMULAS, {})

		snapshot['instruments'] = client.get_by_query(COLECTION_INSTRUMENTS, {})

		snapshot['drls'] = client.get_by_query(COLECTION_DRLS, {})

		folder = current_app.config['FILE_STORAGE_SNAPSHOTS'] + '/'

		ensure_dir(folder)

		filename = secure_filename(name + '.json')

		fil = open(os.path.join(folder, filename), 'w')

		fil.write(json.dumps(snapshot))

		fil.close()

		if register:

			size = os.path.getsize(os.path.join(folder, filename))

			source = {'id': snapshot['id'], 'name': name, 'date': str(datetime.fromtimestamp(tstamp).strftime('%Y-%m-%d %H:%M:%S')), 'size': size, 'user': snapshot['user'], 'description': description}

			client = repo.get_instance(INSTANCE)

			client.saveRlz(COLECTION_SNAPSHOTS, source)

		return name

	except Exception as e:
		getLogger('arg_log').exception(e)
		raise e


def dumpColections():
	try:
		client = repo.get_instance(RLZ_INSTANCE)

		client.clean_collection(COLECTION_RULES)

		client.clean_collection(COLECTION_ENTITYS)

		client.clean_collection(COLECTION_CATALOGS)

		client.clean_collection(COLECTION_TABLES)

		client.clean_collection(COLECTION_SIMULATIONS)

		client.clean_collection(COLECTION_LISTS)

		client.clean_collection(COLECTION_FUNCTIONS)

		client.clean_collection(COLECTION_FORMULAS)

		client.clean_collection(COLECTION_INSTRUMENTS)

		client.clean_collection(COLECTION_DRLS)
	except Exception as e:
		getLogger('arg_log').exception(e)
		raise e


def restore(snap):
	try:
		client = repo.get_instance(RLZ_INSTANCE)

		if 'rules' in snap and snap['rules'] is not None:
			for rule in snap['rules']:
				client.saveRlz(COLECTION_RULES, rule)

		if 'entitys' in snap and snap['entitys'] is not None:
			for entity in snap['entitys']:
				client.saveRlz(COLECTION_ENTITYS, entity)

		if 'tables' in snap and snap['tables'] is not None:
			for table in snap['tables']:
				client.saveRlz(COLECTION_TABLES, table)

		if 'functions' in snap and snap['functions'] is not None:
			for function in snap['functions']:
				client.saveRlz(COLECTION_FUNCTIONS, function)

		if 'formulas' in snap and snap['formulas'] is not None:
			for formula in snap['formulas']:
				client.saveRlz(COLECTION_FORMULAS, formula)

		if 'lists' in snap and snap['lists'] is not None:
			for li in snap['lists']:
				client.saveRlz(COLECTION_LISTS, li)

		if 'catalogs' in snap and snap['catalogs'] is not None:
			for catalog in snap['catalogs']:
				client.saveRlz(COLECTION_CATALOGS, catalog)

		if 'simulations' in snap and snap['simulations'] is not None:
			for simulation in snap['simulations']:
				client.saveRlz(COLECTION_SIMULATIONS, simulation)

		if 'instruments' in snap and snap['instruments'] is not None:
			for instrument in snap['instruments']:
				client.saveRlz(COLECTION_INSTRUMENTS, instrument)

		if 'drls' in snap and snap['drls'] is not None:
			for drl in snap['drls']:
				client.saveRlz(COLECTION_DRLS, drl)

	except Exception, e:
		getLogger('arg_log').exception(e)
		raise e


def getUserName():
	token_id = request.headers.get("Authorization")
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	token = json.loads(r.get(token_id))
	return token['cn']


def getRoles():
	token_id = request.headers.get("Authorization")
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	token = json.loads(r.get(token_id))
	roles = []
	for role in token['roles']:
		roles.append(str(role['rol_id']))
	print roles
	return roles
