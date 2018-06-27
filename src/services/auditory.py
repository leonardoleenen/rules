# -*- coding: UTF-8 -*-
'''
:Authors
    - Enzo D. Grosso
'''

from flask import Blueprint, current_app, request
from flask_cors import cross_origin
from security.security import secure_service
from logging import getLogger
from utils import repo
from time import time as timestamp
from datetime import datetime
from utils.toolbox import ensure_dir
import json

auditory = Blueprint('auditory', "luzia-rulz")

INSTANCE = 'auditoria_arg2'
COLLECTION_AUDITORY = 'audit'

FIELDS_TO_SEARCH = {'this_id': 1, 'data.name': 1, 'tabla': 1, 'data.description': 1, 'tipo_accion': 1, 'nombre_usuario': 1, 'fecha_hora': 1}

REFERENCES = {'user': 'nombre_usuario', 'method': 'tipo_accion', 'type': 'tabla', 'objName': 'data.name'}

KEYS_REFERENCE = ['tipo_accion', 'tabla']

VALUES_REFERENCE = {'Creacion': '(I): Insert', 'Modificacion': '(U): Update', 'Eliminacion': '(D): Delete', 'reglas': 'rules', 'tablas': 'tables', 'entidades': 'entitys', 'catalogos': 'catalogs', 'formulas': 'formulas', 'funciones': 'functions', 'Instrumentos Normativos': 'instruments', 'constantes': 'lists'}


@auditory.route('/auditory/registered_users', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getRegisteredUsers():
    try:
        client = repo.get_instance(INSTANCE)
        array = client.get_query_and_fields(COLLECTION_AUDITORY, {}, {'nombre_usuario': 1})
        response = list(set([x['nombre_usuario'] for x in array if x is not None]))
        return json.dumps({'success': True, 'response': response, 'message': 'Exito'}), 200
    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'response': None, 'message': e.message}), 200


@auditory.route('/auditory/search', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def searchData():
    try:
        data = json.loads(request.data)
        params = buildSearchParams(data)

        client = repo.get_instance(INSTANCE)
        array = client.get_query_and_fields(COLLECTION_AUDITORY, params, FIELDS_TO_SEARCH)

        response = getParsedList(array)

        return json.dumps({'success': True, 'response': response, 'message': 'Exito'}), 200
    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'response': None, 'message': e.message}), 200


@auditory.route('/auditory/getdata/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getData(id):
    try:
        client = repo.get_instance(INSTANCE)
        array = client.get_query_and_fields(COLLECTION_AUDITORY, {'this_id': id}, {'data': 1, 'tabla': 1})

        if array is None or array == []:
            return json.dumps({'success': False, 'response': None, 'message': 'Exito'}), 404

        return json.dumps({'success': True, 'response': array[0], 'message': 'Exito'}), 200
    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'response': None, 'message': e.message}), 200


@auditory.route('/auditory/getregistry/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getRegistry(id):
    try:
        client = repo.get_instance(INSTANCE)
        array = client.get_by_query(COLLECTION_AUDITORY, {'this_id': id})

        if array is None or array == []:
            return json.dumps({'success': False, 'response': None, 'message': 'Exito'}), 404

        return json.dumps({'success': True, 'response': array[0], 'message': 'Exito'}), 200
    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'response': None, 'message': e.message}), 200


def buildSearchParams(data):
    return {REFERENCES[key]: actualValue(REFERENCES[key], data[key]) for key in data if (data[key] is not None and data[key].strip() != '')}


def actualValue(key, value):
    return VALUES_REFERENCE[value] if key in KEYS_REFERENCE else value


def getParsedList(array):
    response = []
    for obj in array:
        robj = {}
        for key in obj:

            if key == 'this_id':
                robj[key] = obj[key]

            elif key == 'data':

                if 'name' in obj[key]:
                    robj['name'] = obj[key]['name']
                if 'description' in obj[key]:
                    robj['description'] = obj[key]['description']

            elif key == 'tabla':
                robj['type'] = obj[key]

            elif key == 'tipo_accion':
                robj['metod'] = obj[key]

            elif key == 'nombre_usuario':
                robj['user'] = obj[key]

            elif key == 'fecha_hora':
                robj['date'] = obj[key]

        response.append(robj)

    return response
