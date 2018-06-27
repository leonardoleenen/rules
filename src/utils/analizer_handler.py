# -*- coding: UTF-8 -*-
'''
:Authors
	- Enzo D. Grosso
'''

import json

from flask import current_app, request, session
import redis

import conection_manager as http


def validate(drl):

    URL_VALIDATE = getURL('RULE_SERVER', 'RULE_SERVER_VALIDATE')

    try:
        validated = http.post(URL_VALIDATE, drl)

        if type(validated) is str:
            validated = json.loads(validated)

        response = {'success': validated['success']}

        if 'msg' in validated:
            response['message'] = validated['msg']

        if 'result' in validated:
            response['response'] = validated['result']

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e.message), 'response': str(e)}


def test(rule, facts=[]):

    URL_TEST = getURL('RULE_SERVER', 'RULE_SERVER_TEST')

    try:
        data = {
            'rule': rule,
            'facts': facts,
            'workspace': get_workspace()
        }

        tested = http.postJson(URL_TEST, data)

        if type(tested) is str:
            tested = json.loads(tested)

        response = {'success': tested['success']}

        if 'msg' in tested:
            response['message'] = tested['msg']

        if 'result' in tested:
            response['response'] = tested['result']

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e.message), 'response': str(e)}


def install(name, version, rule, initialDate=None, finalDate=None, secret_key=None):

    URL_INSTALL = getURL('RULE_SERVER', 'RULE_SERVER_INSTALL')

    try:
        data = {
            'trigger': {
                'name': name,
                'version': version
            },
            'rule': rule,
            'initialDate': initialDate,
            'finalDate': finalDate,
            'secret_key': secret_key,
            'workspace': get_workspace()
        }

        installed = http.postJson(URL_INSTALL, data)

        if type(installed) is str:
            installed = json.loads(installed)

        response = {'success': installed['success']}

        if 'msg' in installed:
            response['message'] = installed['msg']

        if 'result' in installed:
            response['response'] = installed['result']

        if 'soap' in installed:
            response['soap'] = installed['soap']

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e.message), 'response': str(e)}


def uninstall(name, version, secret_key=None):

    URL_UNINSTALL = getURL('RULE_SERVER', 'RULE_SERVER_UNISTALL')

    try:
        data = {
            'trigger': {
                'name': name,
                'version': version
            },
            'secret_key': secret_key
        }

        uninstalled = http.postJson(URL_UNINSTALL, data)

        if type(uninstalled) is str:
            uninstalled = json.loads(uninstalled)

        response = {'success': uninstalled['success']}

        if 'msg' in uninstalled:
            response['message'] = uninstalled['msg']

        if 'result' in uninstalled:
            response['response'] = uninstalled['result']

        return response

    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e.message), 'response': str(e)}


def list():

    URL_LIST = getURL('RULE_SERVER', 'RULE_SERVER_LIST')

    try:
        result = http.get(URL_LIST)

        if type(result) is str:
            result = json.loads(result)

        response = {'success': result['success']}

        if 'msg' in result:
            response['message'] = result['msg']

        if 'result' in result:
            response['response'] = result['result']

        return response

    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e), 'response': str(e)}


def getDRL(name, version):

    URL_DRL = getURL('RULE_SERVER', 'RULE_SERVER_DRL')

    try:
        result = http.get(URL_DRL + '/' + name + '/' + str(version))

        return result
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e), 'response': str(e)}


def serviceInfo(name, version):

    SERVICE_INFO = getURL('RULE_SERVER', 'RULE_SERVER_BASE')

    try:
        result = http.get(SERVICE_INFO + '/' + name + '/' + str(version))

        if type(result) is str:
            result = json.loads(result)

        response = {'success': result['success']}

        if 'msg' in result:
            response['message'] = result['msg']

        if 'result' in result:
            response['response'] = result['result']

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e), 'response': str(e)}


def insertList(payload):

    SERVICE_LIST = getURL('RULE_SERVER', 'RULE_SERVER_VALUE_LIST')

    try:
        data = {
            'workspace': get_workspace(),
            'payload': payload
        }

        inserted = http.postJson(SERVICE_LIST, data)

        if type(inserted) is str:
            inserted = json.loads(inserted)

        response = {
            'success': inserted['success'],
            'message': inserted.get('msg'),
            'response': inserted.get('result')
        }

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e), 'response': str(e)}


def updateList(payload):

    SERVICE_LIST = getURL('RULE_SERVER', 'RULE_SERVER_VALUE_LIST')

    try:
        data = {
            'workspace': get_workspace(),
            'payload': payload
        }

        inserted = http.putJson(SERVICE_LIST, data)

        if type(inserted) is str:
            inserted = json.loads(inserted)

        response = {
            'success': inserted['success'],
            'message': inserted.get('msg'),
            'response': inserted.get('result')
        }

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e), 'response': str(e)}


def deleteList(_id):

    SERVICE_LIST = getURL('RULE_SERVER', 'RULE_SERVER_VALUE_LIST') + '/' + _id

    try:
        SERVICE_LIST += '?workspace=' + get_workspace()

        inserted = http.delete(SERVICE_LIST)

        if type(inserted) is str:
            inserted = json.loads(inserted)

        response = {
            'success': inserted['success'],
            'message': inserted.get('msg'),
            'response': inserted.get('result')
        }

        return response
    except Exception as e:
        current_app.logger.exception(e)
        return {'success': False, 'message': str(e), 'response': e.message}


def getConfig(key):
    try:
        return current_app.config[key]
    except KeyError:
        return None


def getURL(k1, k2):
    try:
        domain = getConfig(k1)
        context = getConfig(k2)
        if domain is None or domain == '' or context is None or context == '':
            return ''
        else:
            return domain + context
    except Exception as e:
        current_app.logger.exception(e)
        return ''


def get_workspace():
    r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)

    token_id = request.headers.get("Authorization")

    if token_id is None:
        token_id = session['token_id']

    if token_id is not None:
        token = json.loads(r.get(token_id))

        if type(token['organization']) is dict:
            _id = "rulz_server_" + token['organization']['organization_id']
        else:
            _id = "rulz_server_" + token['organization']

    return _id
