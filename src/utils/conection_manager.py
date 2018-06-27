# -*- coding: UTF-8 -*-
'''
:Authors
	- Enzo D. Grosso
'''

from flask import current_app
import requests
import json


ERRORS_MESSAGE = {400: 'El server no puede procesar la solicitud', 401: 'No posee aturización para acceder a este servicio', 402: 'Se requiere realizar un pago para acceder a este servicio', 403: 'No posee permisos necesarios para acceder a este servicio', 404: 'Servicio no encontrado o fuera de servicio', 405: 'Metodo no soportado', 408: 'Tiempo de solicitud agotado', 415: 'Tipo de datos no soportados', 500: 'Error interno del server de reglas'}


def post(url, data, headers={'Content-Type': 'text/plain'}):

    try:
        response = requests.post(url, data=data, headers=headers)

        if response.status_code == requests.codes.ok:
            if response.headers.get('content-type') == 'application/json' or response.headers.get('content-type') == 'application/json;charset=UTF-8':
                return response.json()
            else:
                return response.text

        elif response.status_code in ERRORS_MESSAGE:
            return {'success': False, 'msg': '(' + str(response.status_code) + ')' + ERRORS_MESSAGE[response.status_code]}
        else:
            return 'No se puede parsear la respuesta'
    except Exception as ex:
    	current_app.logger.exception(ex)
    	raise Exception('No ha sido posible realizar la conexion ' + str(ex.message))


def put(url, data, headers={'Content-Type': 'text/plain'}):

    try:
        response = requests.put(url, data=data, headers=headers)

        if response.status_code == requests.codes.ok:
            if response.headers.get('content-type') == 'application/json' or response.headers.get('content-type') == 'application/json;charset=UTF-8':
                return response.json()
            else:
                return response.text

        elif response.status_code in ERRORS_MESSAGE:
            return {'success': False, 'msg': '(' + str(response.status_code) + ')' + ERRORS_MESSAGE[response.status_code]}
        else:
            return 'No se puede parsear la respuesta'
    except Exception as ex:
        current_app.logger.exception(ex)
        raise Exception('No ha sido posible realizar la conexion ' + str(ex.message))


def delete(url, data={}, headers={'Content-Type': 'text/plain'}):

    try:
        response = requests.delete(url, data=data, headers=headers)

        if response.status_code == requests.codes.ok:
            if response.headers.get('content-type') == 'application/json' or response.headers.get('content-type') == 'application/json;charset=UTF-8':
                return response.json()
            else:
                return response.text

        elif response.status_code in ERRORS_MESSAGE:
            return {'success': False, 'msg': '(' + str(response.status_code) + ')' + ERRORS_MESSAGE[response.status_code]}
        else:
            return 'No se puede parsear la respuesta'
    except Exception as ex:
        current_app.logger.exception(ex)
        raise Exception('No ha sido posible realizar la conexion ' + str(ex.message))


def get(url, headers={}):

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == requests.codes.ok:
            if response.headers.get('content-type') == 'application/json' or response.headers.get('content-type') == 'application/json;charset=UTF-8':
                return response.json()
            else:
                return response.text

        elif response.status_code in ERRORS_MESSAGE:
        	return {'success': False, 'msg': '(' + response.status_code + ')' + ERRORS_MESSAGE[response.status_code]}
        else:
        	return 'No se puede parsear la respuesta'
    except Exception as e:
        current_app.logger.exception(e)
        raise Exception('No ha sido posible realizar la conexion ' + str(e.message))


def postJson(url, data):

    headers = {'Content-Type': 'application/json'}
    return post(url, json.dumps(data), headers)


def putJson(url, data):
    headers = {'Content-Type': 'application/json'}
    return put(url, json.dumps(data), headers)
