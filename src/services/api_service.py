# -*- coding: UTF-8 -*-
'''
:Authors
  - Enzo D. Grosso
'''

from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin
from security.security import secure_service
from utils import repo, analizer_handler
from time import time as timestamp
from datetime import datetime
from utils.toolbox import BussinessException, createFiles, Response, infixtopostfix, getJsons, makeModelForSimulation, indexOf, upcase_first_letter, dict_diff
from logging import getLogger
import redis
import os
import uuid
import json
import base64
import re
import shutil
import copy

api_service = Blueprint('api_service', "luzia-rulz")

INSTANCE = {'instance': 'app_keys'}
COLECTION_APP_KEYS = 'keys'


@api_service.route('/api/register_key', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def register_key():
    try:
        data = json.loads(request.data)

        if data.get('name') is None:
            return jsonify(success=False, message='debe introducir un nombre para la aplicación a registrar'), 200

        response = {}
        if data.get('id') is not None:
            msg = getFinalData(data)
            update(data)

            register_app(data['id'], msg)
            response['message'] = 'Se ha actualizado con exito la key para ' + data['name']
            response['success'] = True
            response['response'] = data

        elif not existName(data['name']):
            msg = getFinalData(data)
            data['id'] = str(uuid.uuid1())
            insert(data)

            register_app(data['id'], msg)
            response['message'] = 'Se ha almacenado con exito la key para ' + data['name']
            response['success'] = True
            response['response'] = data
        else:
            response['message'] = 'Ya existe una regla con el nombre ' + data['name']
            response['success'] = False

    except Exception as e:
        getLogger('arg_log').exception(e)
        response['message'] = e.message
        response['success'] = False

    return json.dumps(response), 200


@api_service.route('/api/all_keys', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def all_keys():
    try:
        list = []

        client = repo.get_instance(INSTANCE)

        list = client.get_by_query(COLECTION_APP_KEYS, {})

        response = {'message': 'Exito', 'success': True, 'response': list}

    except Exception as e:
        getLogger('arg_log').exception(e)
        response['message'] = e.message
        response['success'] = False

    return json.dumps(response), 200


@api_service.route('/api/delete_key/<kid>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def delete_key(kid):
    try:

        client = repo.get_instance(INSTANCE)

        client.remove(COLECTION_APP_KEYS, kid)

        remove_app(kid)

        response = {'message': 'Exito al eliminar la app key', 'success': True}

    except Exception as e:
        getLogger('arg_log').exception(e)
        response['message'] = e.message
        response['success'] = False

    return json.dumps(response), 200


def register_app(token, msg):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(token, json.dumps(msg))


def remove_app(token):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete(token)


def register_all():
    client = repo.get_instance(INSTANCE)
    app_keys = client.get_by_query(COLECTION_APP_KEYS, {})

    for item in app_keys:
        if item.get('token') is not None:
            register_app(item['id'], item['token'])


def getFinalData(data):
    token = getUserToken()
    if data.get('id') is None:
        data['organization_id'] = token['organization']['organization_id']

    if data.get('creator') is None:
        data['created_by'] = token['cn']

    data['edited_by'] = token['cn']

    if data.get('created_at') is None:
        data['created_at'] = str(datetime.now().isoformat())

    data['edited_at'] = str(datetime.now().isoformat())

    app_token = {
        'uid': 'Aplication',
        'cn': data['name'],
        'email': token.get('email'),
        'one_shoot': False,
        'user_profiles': [{"profile_id": "Aplicacion", "profile_description": "Aplicacion registrada para usar los servicios de reglas"}],
        'roles': [dict([('rol_id', key), ('rol_description', '')]) for key in data['matrix'] if data['matrix'][key] is True],
        'organization': {'organization_id': data['organization_id']}
    }

    data['token'] = app_token
    return app_token


def getUserToken():
    token_id = request.headers.get("Authorization")
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    token = json.loads(r.get(token_id))
    return token


def insert(source):
    client = repo.get_instance(INSTANCE)
    client.saveRlz(COLECTION_APP_KEYS, source)
    return


def update(source):
    client = repo.get_instance(INSTANCE)
    client.updateRlz(COLECTION_APP_KEYS, source['id'], source)
    return


def existName(name):
    try:
        client = repo.get_instance(INSTANCE)
        info = client.get_by_field(COLECTION_APP_KEYS, "name", name)
        if info:
            d = info[0]
        else:
            return False
        return d['name'] == name
    except Exception as e:
        getLogger('arg_log').exception(e)
        return False
