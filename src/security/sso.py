# -*- coding: utf-8 -*-

from flask import current_app, request
from utils import conection_manager as http
import json


class SSOException(Exception):
    def __init__(self, message):
        self.message = message


def getSSOData():
    sso_data = current_app.config.get('SSO_DATA')

    if sso_data is None:
        raise SSOException('No existen datos del SSO')

    if sso_data.get('token_name') is None:
        raise SSOException('No existe token name definido en los datos del SSO')

    if sso_data.get('urls') is None or sso_data.get('urls') == {} or sso_data.get('urls') == '':
        raise SSOException('No existen URLs asociadas al servicio SSO')

    return sso_data


def verifySession(headersParams=None):

    try:
        sso_data = getSSOData()

        token_name = sso_data['token_name']

        if headersParams is not None:
            token = headersParams.get(token_name)
        else:
            token = request.headers.get(token_name, None)

        if token is None:
            raise SSOException('La request no provee token de SSO')

        url = sso_data['urls']['verify']

        headers = {'Auth-Token': token}

        response = http.get(url + '/' + token, headers)

        if type(response) is str or type(response) is unicode:
            response = json.loads(response)

        if response is None or 'success' not in response:
            return False

        return response['success']

    except Exception as e:
        current_app.logger.exception(e)
        return False


def userData(headersParams=None):

    try:
        sso_data = getSSOData()

        token_name = sso_data['token_name']

        user_name = sso_data['user_name']

        if headersParams is not None:
            token = headersParams.get(token_name)
            user = headersParams.get(user_name)
        else:
            token = request.headers.get(token_name, None)
            user = request.headers.get(user_name, None)

        if token is None:
            raise SSOException('La request no provee token de SSO')

        if user is None:
            raise SSOException('La request no provee Usuario valido')

        url = sso_data['urls']['user_data']

        headers = {'Auth-Token': token}

        response = http.get(url + '/' + user, headers)

        if type(response) is str or type(response) is unicode:
            response = json.loads(response)

        if response is None or 'success' not in response or response['success'] is False:
            return None

        result = response['result']

        user_data_ref = sso_data['user_data_ref']

        data = {}

        for key in user_data_ref:
            tmp = result

            path = user_data_ref[key]

            for item in path.split('.'):
                tmp = tmp[item]

            data[key] = tmp

        return data

    except Exception as e:
        current_app.logger.exception(e)
        return None


def userRoles(headersParams=None):

    try:
        sso_data = getSSOData()

        token_name = sso_data['token_name']

        if headersParams is not None:
            token = headersParams.get(token_name)
        else:
            token = request.headers.get(token_name, None)

        if token is None:
            raise SSOException('La request no provee token de SSO')

        url = sso_data['urls']['user_roles']

        headers = {'Auth-Token': token}

        response = http.get(url + '/' + token, headers)

        if type(response) is str or type(response) is unicode:
            response = json.loads(response)

        if response is None or 'success' not in response or response['success'] is False:
            return []

        data = response['result']

        path = sso_data['roles_path']

        for key in path.split('.'):
            data = data[key]

        roles_name = sso_data['roles_name']

        roles_reference = sso_data['roles_reference']

        roles = []

        for item in data:
            rol = item[roles_name]

            for key in roles_reference:

                if indexOf(roles_reference[key], rol) != -1:
                    roles.append(key)

        return roles

    except Exception as e:
        current_app.logger.exception(e)
        return []


def indexOf(obj, key):
    try:
        return obj.index(key)
    except Exception:
        return -1
