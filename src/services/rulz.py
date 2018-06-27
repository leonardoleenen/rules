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
from utils.toolbox import BussinessException, createFiles, Response, infixtopostfix, getJsons, makeModelForSimulation, indexOf, upcase_first_letter, dict_diff, asNumber, decode_base64, getTypes, getFactsFromSimulationsSources, storeJsonScenario
from logging import getLogger
import rules_engine as engine
import dateutil.parser as date_parser
import snapshots
import os
import uuid
import json
import base64
import re
import shutil
import copy

rulz = Blueprint('rulz', "luzia-rulz")

INSTANCE = 'rulz'
COLECTION_RULES = 'rules'
COLECTION_ENTITYS = 'entitys'
COLECTION_CATALOGS = 'catalogs'
COLECTION_TABLES = 'tables'
COLECTION_SIMULATIONS = 'simulations'
COLECTION_LISTS = 'lists'
COLECTION_FUNCTIONS = 'functions'
COLECTION_FORMULAS = 'formulas'
COLECTION_INSTRUMENTS = 'instruments'
COLECTION_PUBLICATIONS = 'publications'
COLECTION_DRLS = 'drls'

patron = re.compile('^f_|^F_')

SERVICE_MODEL = {'url': '', 'rest': {'servicio': '', 'method': ''}, 'soap': {'wsdl': '', 'method': ''}, 'data': {'facts': [{'fact_name': '', 'properties': {}}]}, 'secret_key': 'string'}


def getDataRequest():
    direct = current_app.config.get('HANDLED_BY_DIRECTOR')

    if direct is not None and direct is True:
        if request.data is not None:
            tempData = json.loads(request.data)

            if 'requestSize' in tempData and tempData['requestSize'] is not None and tempData['requestSize'] > 1048575:
                with open(tempData['path'], 'r') as dataFile:
                    data = json.loads(dataFile.read())
            else:
                data = tempData
    else:
        data = json.loads(request.data)

    return data


@rulz.route('/rulz/status')
@cross_origin(headers=['Content-Type'])
@secure_service
def live():
    response = Response()
    response.setSuccess(True)
    response.setMessage('System ok!')
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/status/check/<entity>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def statusCheck(entity):
    response = Response()
    try:
        data = getDataRequest()

        if data.get('id') is None:
            return jsonify(success=True, message='no se detectan modificaciones', response=False), 200

        entity = getCollection(entity)

        if entity == '':
            return jsonify(success=False, message='debe indicar un nombre de entidad valido'), 200

        client = repo.get_instance(INSTANCE)

        current = client.get_by_id(entity, data['id'])

        result = dict_diff(current, data) != {}

        response.setMessage(('no se detectan modificaciones', 'modificaciones detectadas')[result])
        response.setSuccess(True)
        response.setResponse(result)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/count/all', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def countAllCollections():
    response = Response()
    try:
        count = {}

        client = repo.get_instance(INSTANCE)

        count['rule'] = client.count(COLECTION_RULES, {})
        count['entity'] = client.count(COLECTION_ENTITYS, {})
        count['catalog'] = client.count(COLECTION_CATALOGS, {})
        count['table'] = client.count(COLECTION_TABLES, {})
        count['simulation'] = client.count(COLECTION_SIMULATIONS, {})
        count['list'] = client.count(COLECTION_LISTS, {})
        count['function'] = client.count(COLECTION_FUNCTIONS, {})
        count['formula'] = client.count(COLECTION_FORMULAS, {})
        count['instrument'] = client.count(COLECTION_INSTRUMENTS, {})
        count['publication'] = client.count(COLECTION_PUBLICATIONS, {})
        count['drl'] = client.count(COLECTION_DRLS, {})

        response.setMessage('todo ok')
        response.setSuccess(True)
        response.setResponse(count)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/count/<tp>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def countCollections(tp):
    response = Response()
    try:
        col = getCollection(tp)

        client = repo.get_instance(INSTANCE)

        count = client.count(col, {})

        response.setMessage('todo ok')
        response.setSuccess(True)
        response.setResponse(count)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/rule', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistRule():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='debe introducir un nombre para la regla'), 200

        drl = getRuleDRL(copy.deepcopy(data))

        validated = analizer_handler.validate(drl)

        if 'success' not in validated or not validated['success']:
            return json.dumps(validated), 200

        if 'id' in data and data['id'] is not None:
            updateInstRefOf(data, 'rules')
            checkDomain(data, 'rules')
            update(data)
            response.setMessage('Se ha actualizado con exito la regla ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)

        elif not existName(data['name']):
            data['id'] = str(uuid.uuid1())

            updateInstRefOf(data, 'rules')
            checkDomain(data, 'rules')
            insert(data)
            response.setMessage('Se ha almacenado con exito la regla ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe una regla con el nombre ' + data['name'])
            response.setSuccess(False)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def updateInstRefOf(data, ty):
    try:
        try:
            force = current_app.config['NEED_INSTRUMENTS']
        except Exception:
            force = True
        if force and ('instruments' not in data or data['instruments'] is None or len(data['instruments']) == 0):
            raise BussinessException('No se puede almacenar una ' + ('regla', 'tabla')[ty == 'tables'] + ' sin estar relacionada a un instrumento normativo')

        client = repo.get_instance(INSTANCE)

        instruments = client.get_by_query(COLECTION_INSTRUMENTS, {})

        for inst in instruments:

            if ty in inst and inst[ty] is not None and len(inst[ty]) != 0:
                for rule in inst[ty]:
                    if 'id' in rule and rule['id'] == data['id']:
                        del inst[ty][inst[ty].index(rule)]
                        update(inst, COLECTION_INSTRUMENTS)
                        break

            if 'instruments' in data and data['instruments'] is not None and len(data['instruments']) != 0:

                for rinst in data['instruments']:
                    if 'id' in rinst and rinst['id'] == inst['id']:
                        if ty not in inst or inst[ty] is None:
                            inst[ty] = []

                        inst[ty].append({'id': data['id'], 'name': data['name']})
                        update(inst, COLECTION_INSTRUMENTS)
                        break

    except BussinessException as e:
        raise e
    except Exception as e:
        raise e


@rulz.route('/rulz/drl/<ent>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getDRLOf(ent):
    response = Response()
    try:
        data = getDataRequest()

        names = {'rule': 'regla', 'table': 'tabla', 'simulation': 'escenario'}

        if ent == 'rule':
            drl = getRuleDRL(data)
        elif ent == 'table':
            drl = getTableDRL(data)
        elif ent == 'simulation':
            drl = getDRLFromSimulation(data)
        else:
            drl = None

        if drl is not None:
            response.setMessage('DRL generado por ' + ('la', 'el')[ent == 'simulation'] + ' ' + names[ent] + ' ' + data['name'])
            response.setSuccess(True)
            response.setResponse(drl)
        else:
            response.setMessage('el tipo de entidad aportado no es correcto, debe proveer tipo "rule", "table" o "simulation"')
            response.setSuccess(False)
            response.setResponse(None)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def getRuleDRL(data):
    try:
        functNames = []
        r = engine.makeRuleMVEL(data, functNames)

        declares = getDeclares(set(data['types']))

        functions = getFunctions(set(functNames))

        drl = engine.getStructure().format('\n'.join(declares), r, current_app.config['RULE_DIALECT'], functions)

        getLogger('arg_log').debug("DRL generado:\n" + drl)

        return drl
    except Exception as e:
        raise e


def getTableDRL(data):
    try:
        functNames = []
        r = engine.makeTableMVEL(data, functNames)

        se = set()

        for ent in data['entities']:
            se.add(ent['entity']['id'])

        declares = getDeclares(se)

        functions = getFunctions(set(functNames))

        drl = engine.getStructure().format('\n'.join(declares), r, current_app.config['RULE_DIALECT'], functions)

        getLogger('arg_log').debug("DRL generado:\n" + drl)

        return drl
    except Exception as e:
        raise e


@rulz.route('/rulz/table', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistTable():
    response = Response()
    try:
        data = getDataRequest()

        drl = getTableDRL(copy.deepcopy(data))

        validated = analizer_handler.validate(drl)

        if 'success' not in validated or not validated['success']:
            return json.dumps(validated), 200
        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='debe instroducir un nombre para la tabla'), 200

        if 'id' in data and data['id'] is not None:

            updateInstRefOf(data, 'tables')
            checkDomain(data, 'tables')

            update(data, COLECTION_TABLES)
            response.setMessage('Se ha actualizado con exito la tabla ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_TABLES):
            data['id'] = str(uuid.uuid1())

            updateInstRefOf(data, 'tables')
            checkDomain(data, 'tables')

            insert(data, COLECTION_TABLES)
            response.setMessage('Se ha almacenado con exito la tabla ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe una tabla con el nombre ' + data['name'])
            response.setSuccess(False)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def checkDomain(data, tp):
    try:
        client = repo.get_instance(INSTANCE)
        if 'atomic' in data and data['atomic'] is True:
            if 'id' in data and data['id'] is not None and data['id'] != '':
                obj = None
                try:
                    obj = client.get_by_id((COLECTION_RULES, COLECTION_TABLES)[tp == 'tables'], data['id'])
                except Exception as ew:
                    getLogger('arg_log').debug(ew)

                if obj is not None:

                    if 'atomic' in obj and obj['atomic'] is True:

                        if 'catalog' in data and data['catalog']is not None and len(obj['catalog']) != 0 and obj['catalog']['name'] == (data['name'] + 'Dom'):
                            return
                        else:
                            catId = newAtomicDomain(data['name'])
                            if updateCatalogs(data['id'], data['name'], catId, tp):
                                data['catalog'] = {'id': catId, 'name': data['name'] + 'Dom'}
                                return
                            else:
                                raise Exception('No se pudieron actualizar las referencias de los dominios')

                    elif 'catalog' in obj and obj['catalog'] is not None and len(obj['catalog']) != 0:
                        catId = newAtomicDomain(data['name'])
                        if updateCatalogs(data['id'], data['name'], catId, tp):
                            data['catalog'] = {'id': catId, 'name': data['name'] + 'Dom'}
                            return
                        else:
                            raise Exception('No se pudieron actualizar las referencias de los dominios')

                else:

                    catId = newAtomicDomain(data['name'])
                    if updateCatalogs(data['id'], data['name'], catId, tp):
                        data['catalog'] = {'id': catId, 'name': data['name'] + 'Dom'}
                        return
                    else:
                        raise Exception('No se pudieron actualizar las referencias de los dominios')

            else:
                catId = newAtomicDomain(data['name'])
                if updateCatalogs(data['id'], data['name'], catId, tp):
                    data['catalog'] = {'id': catId, 'name': data['name'] + 'Dom'}
                    return
                else:
                    raise Exception('No se pudieron actualizar las referencias de los dominios')

        else:
            if 'catalog' in data and data['catalog'] is not None and len(data['catalog']) != 0:
                if not updateCatalogs(data['id'], data['name'], data['catalog']['id'], tp):
                    raise Exception('No se pudieron actualizar las referencias de los dominios')
    except Exception as e:
        raise e


def newAtomicDomain(name):
    try:
        if not existName(name, COLECTION_CATALOGS):
            domain = {'id': str(uuid.uuid1()), 'name': name + 'Dom', 'description': 'Dominio creado por solicitud de regla atomica ' + str(name), 'rules': [], 'tables': []}
            insert(domain, COLECTION_CATALOGS)
            return domain['id']
        else:
            info = repo.get_instance(INSTANCE).get_by_field(COLECTION_CATALOGS, "name", name)

            if info:
                return info[0]['id']
    except Exception as e:
        raise e


@rulz.route('/rulz/entity', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistEntity():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'].strip() == '':
            return jsonify(success=False, message='debe introducir un nombre valido para la entidad'), 200

        if 'schema' not in data or data['schema'] is None or data['schema'] == {}:
            return jsonify(success=False, message='No es posible almacenar una entidad que se encuentre vacia'), 200

        if patron.match(data['name']) is not None:
            response.setMessage('El nombre de la entidad comienza con F_ o f_ por favor verifique que esto no ocurra')
            response.setSuccess(False)

        elif 'id' in data and data['id'] is not None:
            try:
                deleteEntity(data, repo.get_instance(INSTANCE))
            except BussinessException as be:
                sameName(data['id'], data['name'], COLECTION_ENTITYS)

            if 'force' not in data:
                if hasChanges(data):
                    sims = checkInSimulations(data['id'])
                    if sims != []:
                        return jsonify(success=False, message='La entidad se encuentra en escenarios', retry=True, response=sims), 200

            elif data['force'] is True:
                changeSimulationsJsons(data)
                del data['force']

            else:
                disableSimulations(data['id'])
                del data['force']

            update(data, COLECTION_ENTITYS)
            response.setMessage('Se ha actualizado con exito la entidad ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_ENTITYS):
            data['id'] = str(uuid.uuid1())
            insert(data, COLECTION_ENTITYS)
            response.setMessage('Se ha almacenado con exito la entidad ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe una entidad con el nombre ' + data['name'])
            response.setSuccess(False)

    except BussinessException as be:
        response.setMessage(be.message)
        response.setSuccess(False)
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/entity/rules_related', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def whichRulesOnEntity():
    response = Response()
    try:
        data = getDataRequest()
        client = repo.get_instance(INSTANCE)
        result = {'rules': [], 'tables': []}
        array = client.get_by_query(COLECTION_RULES, {'types': data['id']})

        for item in array:
            iresult = {'rule_name': item.get('name'), 'id': item.get('id')}
            attrs = []

            for cond in item['rules']:
                if cond.get('parentesis') is True:
                    continue

                if cond['type'] == data['name']:
                    for rest in cond['conds']:
                        attrs.append(rest['attr']['name'])

            iresult['attrs'] = list(set(attrs))

            result['rules'].append(iresult)

        array = client.get_by_query(COLECTION_TABLES, {'entities.entity.id': data['id']})

        for item in array:
            iresult = {'table_name': item.get('name'), 'id': item.get('id')}
            attrs = []

            for ent in item['entities']:
                if ent['entity']['name'] == data['name']:
                    for cond in ent['conds']:
                        attrs.append(cond['attribute'].split('.', 1)[1])

                    break

            iresult['attrs'] = attrs

            result['tables'].append(iresult)

        response.setMessage('todo ok')
        response.setSuccess(True)
        response.setResponse(result)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/entity/in_catalogs', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def whichEntittiesOnCatalogs():
    response = Response()
    try:
        data = getDataRequest()

        client = repo.get_instance(INSTANCE)

        ids = getTypes(data, client)

        query = {'id': {'$in': ids}}

        result = client.get_by_query(COLECTION_ENTITYS, query)

        response.setMessage('todo ok')
        response.setSuccess(True)
        response.setResponse(result)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def hasChanges(data):

    client = repo.get_instance(INSTANCE)
    old = client.get_by_id(COLECTION_ENTITYS, data['id'])

    return dict_diff(old['schema']['properties'], data['schema']['properties']) != {}


def checkInSimulations(objId):
    client = repo.get_instance(INSTANCE)
    objs = client.get_by_query(COLECTION_SIMULATIONS, {'collection.id': objId})

    if objs is None or len(objs) == 0:
        return []

    names = []

    for obj in objs:
        names.append(obj['name'])

    return names


def changeSimulationsJsons(data):
    client = repo.get_instance(INSTANCE)
    objs = client.get_by_query(COLECTION_SIMULATIONS, {'collection.id': data['id']})

    for obj in objs:
        for i, val in enumerate(obj['collection']):
            newVal = copy.deepcopy(data)
            del newVal['plainAttr']
            del newVal['description']
            changeCollections(val['schema']['properties'], newVal['schema']['properties'])
            obj['collection'][i] = newVal

        obj['disabled'] = False
        obj['version'] += 1
        update(obj, COLECTION_SIMULATIONS)


def disableSimulations(objId):
    client = repo.get_instance(INSTANCE)
    objs = client.get_by_query(COLECTION_SIMULATIONS, {'collection.id': objId})

    for obj in objs:
        obj['disabled'] = True
        update(obj, COLECTION_SIMULATIONS)


def changeCollections(obj, newObj):

    def allNone(obj):
        if obj['type'] != 'object':
            obj['value'] = None
            return

        for key in obj['properties']:
            allNone(obj['properties'][key])

    for key in obj:
        if key in newObj and newObj[key]['type'] == obj[key]['type']:
            if obj[key]['type'] != 'object':
                newObj[key]['value'] = obj[key].get('value')
            else:
                changeCollections(obj[key]['properties'], newObj[key]['properties'])
        elif key not in newObj:
            continue
        else:
            allNone(newObj[key])


'''
{
    entity:{
        id:'',
        name:''
    },
    attr:''
}
'''


@rulz.route('/rulz/check/entity/attribute', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def checkEntityAttribute():
    response = Response()
    try:
        data = getDataRequest()

        attr = data['attr']
        entity = data['entity']

        checkInRules(entity['id'], entity['name'], attr)

        checkInTables(entity['name'], entity['name'] + '.' + attr)

        response.setSuccess(True)
        response.setMessage('Exito')

    except BussinessException as be:
        response.setSuccess(False)
        response.setMessage(be.message)
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setSuccess(False)
        response.setMessage('Ocurrio un error ' + e.message)
    return json.dumps(response.__dict__), 200


'''
{
    entity:{
        id:'',
        name:''
    },
    attr:{
        'old':'',
        'new':''
    }
}
'''


@rulz.route('/rulz/change/entity/attribute', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def changeEntityAttribute():
    response = Response()
    try:
        data = getDataRequest()

        oldAttr = data['attr'].get('old')
        newAttr = data['attr'].get('new')
        entity = data['entity']

        changeInRules(entity['id'], entity['name'], oldAttr, newAttr)

        changeInTables(entity['name'], entity['name'] + '.' + oldAttr, entity['name'] + '.' + newAttr)

        changeInFormula(entity['id'], oldAttr, newAttr)

        obj = changeInEntity(entity['id'], oldAttr, newAttr)

        response.setResponse(obj)
        response.setSuccess(True)
        response.setMessage('Exito')

    except BussinessException as be:
        response.setSuccess(False)
        response.setMessage(be.message)
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setSuccess(False)
        response.setMessage('Ocurrio un error ' + e.message)
    return json.dumps(response.__dict__), 200


def changeInEntity(id, oldAttr, newAttr):
        client = repo.get_instance(INSTANCE)

        obj = client.get_by_id(COLECTION_ENTITYS, id)

        oldA = oldAttr.split('.')
        newA = newAttr.split('.')
        newA = newA[len(newA) - 1]

        properties = obj['schema']['properties']

        for i, attr in enumerate(oldA):
            if i < (len(oldA) - 1):
                properties = properties[attr]['properties']
                continue

            properties[newA] = copy.deepcopy(properties[attr])
            del properties[attr]

        for plainAttr in obj['plainAttr']:
            if plainAttr.get('name') == oldAttr:
                plainAttr['name'] = newAttr

        update(obj, COLECTION_ENTITYS)

        return obj


def checkInRules(id, name, attr):
    try:
        client = repo.get_instance(INSTANCE)

        objs = client.get_by_query(COLECTION_RULES, {'types': id})

        if objs is None or len(objs) == 0:
            return

        for obj in objs:
            for rl in obj['rules']:
                if 'parentesis' in rl and rl['parentesis'] is True:
                    continue

                if rl['type'] == name:
                    for cn in rl['conds']:
                        if cn['attr']['name'] == attr:
                            raise BussinessException('No se puede eliminar el attributo "' + attr + '" pues esta siendo usado en una condición de la regla ' + str(obj['name']))

            if 'actions' not in obj or obj['actions'] is None:
                continue

            for act in obj['actions']:

                if 'message' in act and act['message'] is True:
                    if indexOf(act['value'], attr) != -1:
                        raise BussinessException('No se puede eliminar el attributo "' + attr + '" pues esta siendo usado en un mensaje de la regla ' + str(obj['name']))
                    continue

                bind = act['binding']['name'].split('.', 1)[1]

                if bind == attr or indexOf(act['value'], attr) != -1:
                    raise BussinessException('No se puede eliminar el attributo "' + attr + '" pues esta siendo usado en una accion de la regla ' + str(obj['name']))

    except BussinessException as be:
        raise be
    except Exception as e:
        raise e


def changeInRules(id, name, oldAttr, newAttr):

    try:
        client = repo.get_instance(INSTANCE)

        objs = client.get_by_query(COLECTION_RULES, {'types': id})

        if objs is None or len(objs) == 0:
            return

        for obj in objs:
            for rl in obj['rules']:
                if 'parentesis' in rl and rl['parentesis'] is True:
                    continue

                if rl['type'] == name:
                    for cn in rl['conds']:
                        if cn['attr']['name'] == oldAttr:
                            cn['attr']['name'] = newAttr

                        val = cn['value']
                        if indexOf(val, '$') == 0:
                            bind = val.split('.', 1)

                            if len(bind) >= 2:
                                if bind[1] == oldAttr:
                                    cn['value'] = bind[0] + '.' + newAttr

                        funct = cn.get('funct')

                        if funct is not None:
                            for field in funct['fields']:
                                val = field['name']
                                if indexOf(val, '$') == 0:
                                    bind = val.split('.', 1)

                                    if len(bind) >= 2:
                                        if bind[1] == oldAttr:
                                            field['name'] = bind[0] + '.' + newAttr

                        formula = cn.get('formula')

                        if formula is not None:
                            formula['acums'] = formula['acums'].replace(oldAttr.replace('.', '_'), newAttr.replace('.', '_')).replace(oldAttr, newAttr)

                            formula['line'] = formula['line'].replace(oldAttr, newAttr)

            if 'actions' not in obj or obj['actions'] is None:
                continue

            for act in obj['actions']:

                if 'message' in act and act['message'] is True:
                    if indexOf(act['value'], oldAttr) != -1:
                        msg = act['value'].split(oldAttr)
                        act['value'] = newAttr.join(msg)

                    continue

                bind = act['binding']['name'].split('.', 1)

                if bind[1] == oldAttr:
                    act['binding']['name'] = bind[0] + '.' + newAttr

                if indexOf(act['value'], oldAttr) != -1:
                    msg = act['value'].split(oldAttr)
                    act['value'] = newAttr.join(msg)

                funct = act.get('funct')

                if funct is not None:
                    for field in funct['fields']:
                        val = field['name']
                        if indexOf(val, '$') == 0:
                            bind = val.split('.', 1)

                            if len(bind) >= 2:
                                if bind[1] == oldAttr:
                                    field['name'] = bind[0] + '.' + newAttr

                formula = act.get('formula')

                if formula is not None:
                    formula['acums'] = formula['acums'].replace(oldAttr.replace('.', '_'), newAttr.replace('.', '_')).replace(oldAttr, newAttr)

                    formula['line'] = formula['line'].replace(oldAttr, newAttr)

            update(obj, COLECTION_RULES)

    except Exception as e:
        raise e


def checkInTables(name, attr):
    try:
        client = repo.get_instance(INSTANCE)

        objs = client.get_by_query(COLECTION_TABLES, {})

        if objs is None or len(objs) == 0:
            return

        for obj in objs:
            for et in obj['entities']:
                if et['entity']['name'] == name:
                    for cn in et['conds']:
                        if cn['attribute'] == attr:
                            raise BussinessException('No se puede eliminar el attributo "' + attr.split('.', 1)[1] + '" pues esta siendo usado en una tabla (' + str(obj['name']) + ')')

    except BussinessException as be:
        raise be
    except Exception as e:
        raise e


def changeInTables(name, oldAttr, newAttr):
    try:
        client = repo.get_instance(INSTANCE)

        objs = client.get_by_query(COLECTION_TABLES, {})

        if objs is None or len(objs) == 0:
            return

        for obj in objs:
            for et in obj['entities']:
                if et['entity']['name'] == name:
                    for cn in et['conds']:
                        if cn['attribute'] == oldAttr:
                            cn['attribute'] = newAttr

            update(obj, COLECTION_TABLES)

    except Exception as e:
        raise e


def changeInFormula(id, oldAttr, newAttr):

    try:
        client = repo.get_instance(INSTANCE)

        objs = client.get_by_query(COLECTION_FORMULAS, {'types': id})

        for formula in objs:

            acums = formula.get('acums')

            if acums is not None and acums != '':
                acums = acums.replace(oldAttr.replace('.', '_'), newAttr.replace('.', '_')).replace(oldAttr, newAttr)

            selectedItems = formula.get('selectedItems')

            if selectedItems is not None:
                for item in selectedItems:
                    attr = item.get('attr')

                    if attr is not None and attr['name'] == oldAttr:
                        attr['name'] = newAttr

                        item['name'] = newAttr.join(item['name'].split(oldAttr))

                        item['_lowername'] = newAttr.lower().join(item['_lowername'].split(oldAttr.lower()))

            postfija = formula.get('postfija')

            if postfija is not None:
                for i, e in enumerate(postfija):
                    if indexOf(e, oldAttr) != -1:
                        postfija[i] = newAttr.join(e.split(oldAttr))

            line = formula.get('line')

            if line is not None and line != '' and indexOf(line, oldAttr) != -1:
                line = newAttr.join(line.split(oldAttr))

            update(formula, COLECTION_FORMULAS)

    except Exception, e:
        raise e


@rulz.route('/rulz/catalog', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistCatalog():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='Los datos recibidos no son correctos'), 200

        if 'id' in data and data['id'] is not None:
            if not updateCatalogReference(data):
                raise Exception('No se pudieron actualizar las referencias al dominio')
            update(data, COLECTION_CATALOGS)
            response.setMessage('Se ha actualizado con exito el dominio ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_CATALOGS):
            data['id'] = str(uuid.uuid1())
            if not updateCatalogReference(data):
                raise Exception('No se pudieron actualizar las referencias al dominio')
            insert(data, COLECTION_CATALOGS)
            response.setMessage('Se ha almacenado con exito el dominio ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe un dominio con el nombre ' + data['name'])
            response.setSuccess(False)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/simulation', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistSimulation():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='El nombre es requerido'), 200

        if 'catalogs' not in data or data['catalogs'] is None or len(data['catalogs']) == 0:
            return jsonify(success=False, message='bebe seleccionar al menos 1 Dominio'), 200

        if data.get('id') is not None:
            client = repo.get_instance(INSTANCE)
            obj = client.get_by_id(COLECTION_SIMULATIONS, data['id'])

            if 'disabled' in obj and obj['disabled'] is True:
                return jsonify(success=False, message='No es posible actualizar un escenario que se encuentra desactivado'), 200

            data['version'] = simulationVersion(data['version'])

            checkSimFiles(data)

            update(data, COLECTION_SIMULATIONS)
            response.setMessage('Se ha actualizado con exito el escenario ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)

        elif not existName(data['name'], COLECTION_SIMULATIONS) or not existVersion(data['name'], data['version']):
            data['id'] = str(uuid.uuid1())
            data['version'] = simulationVersion(data['version'])
            insert(data, COLECTION_SIMULATIONS)
            response.setMessage('Se ha almacenado con exito el escenario ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)

        else:
            response.setMessage('Ya existe un escenario con el nombre ' + data['name'])
            response.setSuccess(False)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def simulationVersion(val):
    if val is None:
        return 1
    elif current_app.config.get('AUTO_VERSION') is False:
        return asNumber(val)
    else:
        return val + 1


def checkSimFiles(data):

    _id = data.get('id')

    client = repo.get_instance(INSTANCE)
    obj = client.get_by_id(COLECTION_SIMULATIONS, _id)

    if obj.get('sources') is None:
        return

    if obj.get('sources').get('files') is None:
        return

    names = [_file.get('name') for _file in data.get('sources').get('files')]

    for _file in obj.get('sources').get('files'):
        if _file.get('name') not in names:
            _path = _file.get('path')
            if os.path.exists(_path):
                os.remove(_path)


@rulz.route('/rulz/simulation/model/get', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getSimulationModel():
    response = Response()
    try:
        data = getDataRequest()

        if 'id' in data and data['id'] is not None:
            client = repo.get_instance(INSTANCE)
            obj = client.get_by_id(COLECTION_SIMULATIONS, data['id'])

            if 'disabled' in obj and obj['disabled'] is True:
                return jsonify(success=False, message='No es posible obtener modelos de un escenario que se encuentra desactivado'), 200

        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='El nombre es requerido'), 200

        if 'catalogs' not in data or data['catalogs'] is None or len(data['catalogs']) == []:
            return jsonify(success=False, message='bebe seleccionar al menos 1 Dominio'), 200

        bb = makeModelForSimulation(data)

        response.setSuccess(True)
        response.setMessage('Todo ok')
        response.setResponse({'b64': bb, 'filetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'name': data['name'] + '.xlsx'})

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/simulation/jsons', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getJsonsForSimulation():
    response = Response()
    try:
        data = getDataRequest()

        if data.get('id') is not None:
            client = repo.get_instance(INSTANCE)
            obj = client.get_by_id(COLECTION_SIMULATIONS, data['id'])

            if 'disabled' in obj and obj['disabled'] is True:
                return jsonify(success=False, message='No es posible importar datos a un escenario que se encuentra desactivado'), 200

        jsons = getJsons(data)

        has_facts = False
        for key in jsons:
            value = jsons.get(key)

            if value is not None and len(value) != 0:
                has_facts = True
                break

        if has_facts:

            name = data.get('name')
            if name is None:
                name = 'undefined'

            file_info = storeJsonScenario(name, jsons)

            file_info['filename'] = data.get('file').get('filename')
        else:
            file_info = None

        response.setMessage('La importación se realizo correctamente' if has_facts else 'El archivo no posee datos validos')
        response.setResponse(file_info)
        response.setSuccess(has_facts)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/list', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistValueList():
    response = Response()
    try:
        data = getDataRequest()
        if data.get('name') is None or data.get('name').strip() == '':
            return jsonify(success=False, message='debe ingresar un nombre valido para la lista de valores'), 200

        if 'id' in data and data['id'] is not None:
            data['elements'] = checkValueList(data['elements'], data.get('type'))
            result = analizer_handler.updateList(data)

            if result.get('success') is not True:
                raise BussinessException('No se ha podido almacenar la lista de valores')

            update(data, COLECTION_LISTS)
            response.setMessage('Se ha actualizado con exito la lista de valores ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_LISTS):
            data['id'] = str(uuid.uuid1())
            data['elements'] = checkValueList(data['elements'], data.get('type'))
            result = analizer_handler.insertList(data)

            if result.get('success') is not True:
                raise BussinessException('No se ha podido almacenar la lista de valores')

            insert(data, COLECTION_LISTS)
            response.setMessage('Se ha almacenado con exito la lista de valores ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe una lista de valores con el nombre ' + data['name'])
            response.setSuccess(False)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def checkValueList(elements, tp='string'):
    return [element for element in elements if element.get('value') is not None and element.get('type') == tp and valid_cast(element.get('value'), tp)]


def valid_cast(value, tp):
    result = False
    try:
        if tp == 'string':
            str(value)
            result = True
        elif tp == 'integer':
            int(value)
            result = True
        elif tp == 'float':
            float(value)
            result = True
        elif tp == 'date':
            date_parser.parse(value)
            result = True
    except ValueError:
        result = False

    return result


@rulz.route('/rulz/function', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistFunction():
    response = Response()
    try:
        data = getDataRequest()
        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='Los datos recibidos no son correctos'), 200

        f = engine.makeFunctionMVEL(data)

        drl = engine.getStructure().format('', '', current_app.config['RULE_DIALECT'], f)

        validated = analizer_handler.validate(drl)
        if 'success' not in validated or not validated['success']:
            return json.dumps(validated), 200
        if 'id' in data and data['id'] is not None:
            update(data, COLECTION_FUNCTIONS)
            response.setMessage('Se ha actualizado con exito la funcion ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_FUNCTIONS):
            data['id'] = str(uuid.uuid1())
            insert(data, COLECTION_FUNCTIONS)
            response.setMessage('Se ha almacenado con exito la funcion ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe una funcion con el nombre ' + data['name'])
            response.setResponse('Ya existe una funcion con el nombre ' + data['name'])
            response.setSuccess(False)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/formula', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistFormula():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='Los datos recibidos no son correctos'), 200

        getFinalFormula(data)

        if 'id' in data and data['id'] is not None:
            update(data, COLECTION_FORMULAS)
            response.setMessage('Se ha actualizado con exito la formula ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_FORMULAS):
            data['id'] = str(uuid.uuid1())
            insert(data, COLECTION_FORMULAS)
            response.setMessage('Se ha almacenado con exito la formula ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe una formula con el nombre ' + data['name'])
            response.setResponse('Ya existe una formula con el nombre ' + data['name'])
            response.setSuccess(False)
    except BussinessException as be:
        getLogger('arg_log').debug(be)
        response.setMessage(be.message)
        response.setSuccess(False)
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def getFinalFormula(data=None):
    string = data['line']
    array = infixtopostfix(string)
    dic = engine.makeFormula(string, data['name'])

    types = []
    for item in data['selectedItems']:
        if 'entity' in item and item['entity'] is not None:
            types.append(item['entity'])

    data['postfija'] = array
    data['acums'] = dic['acums']
    data['formula'] = dic['formula']
    data['types'] = types


@rulz.route('/rulz/function/test', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def testFunction():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None:
            return jsonify(success=False, response='La funcion no posee un nombre valido'), 200

        if 'returnType' not in data or data['returnType'] is None:
            return jsonify(success=False, response='La funcion no posee un tipo de retorno valido'), 200

        f = engine.makeFunctionMVEL(data)

        drl = engine.getStructure().format('', '', current_app.config['RULE_DIALECT'], f)

        validated = analizer_handler.validate(drl)

        return json.dumps(validated), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
        return json.dumps(response.__dict__), 200


@rulz.route('/rulz/instrument', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def persistInstrument():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'] == '' or data['name'] == ' ':
            return jsonify(success=False, message='Los datos recibidos no son correctos'), 200

        if 'id' in data and data['id'] is not None:
            createFiles(data, data['tmpinst'])
            del data['tmpinst']
            updateInstRef(data)
            update(data, COLECTION_INSTRUMENTS)
            response.setMessage('Se ha actualizado con exito el instrumento normativo ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_INSTRUMENTS):
            data['id'] = str(uuid.uuid1())
            createFiles(data, data['tmpinst'])
            del data['tmpinst']
            updateInstRef(data)
            insert(data, COLECTION_INSTRUMENTS)
            response.setMessage('Se ha almacenado con exito el instrumento normativo ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe un instrumento normativo con el nombre ' + data['name'])
            response.setSuccess(False)
    except BussinessException as be:
        getLogger('arg_log').debug(be)
        response.setMessage(be.message)
        response.setSuccess(False)
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + e.message)
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def updateInstRef(data):
    try:
        client = repo.get_instance(INSTANCE)

        rules = client.get_by_query(COLECTION_RULES, {})

        for rule in rules:
            if 'instruments' in rule and rule['instruments'] is not None and len(rule['instruments']) != 0:
                for ins in rule['instruments']:
                    if 'id' in ins and ins['id'] == data['id']:
                        del rule['instruments'][rule['instruments'].index(ins)]
                        update(rule, COLECTION_RULES)
                        break

            if 'rules' in data and data['rules'] is not None and len(data['rules']) != 0:
                for irule in data['rules']:
                    if 'id' in irule and irule['id'] == rule['id']:

                        if 'instruments' not in rule or rule['instruments'] is None:
                            rule['instruments'] = []

                        rule['instruments'].append({'id': data['id'], 'name': data['name']})

                        update(rule, COLECTION_RULES)
                        break

        rules = client.get_by_query(COLECTION_TABLES, {})

        for rule in rules:
            if 'instruments' in rule and rule['instruments'] is not None and len(rule['instruments']) != 0:
                for ins in rule['instruments']:
                    if 'id' in ins and ins['id'] == data['id']:
                        del rule['instruments'][rule['instruments'].index(ins)]
                        update(rule, COLECTION_TABLES)
                        break

            if 'tables' in data and data['tables'] is not None and len(data['tables']) != 0:
                for irule in data['tables']:
                    if 'id' in irule and irule['id'] == rule['id']:

                        if 'instruments' not in rule or rule['instruments'] is None:
                            rule['instruments'] = []

                        rule['instruments'].append({'id': data['id'], 'name': data['name']})

                        update(rule, COLECTION_TABLES)
                        break

    except Exception as e:
        raise e


@rulz.route('/rulz/files/<inst>/<name>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
def serveFiles(inst, name):
    try:
        f = open(current_app.config['FILE_STORAGE_BUCKET_PATH'] + '/' + inst.replace(' ', '_') + '/' + name)
        bb = base64.b64encode(f.read())
        return json.dumps({'success': True, 'response': bb, 'message': 'ok'}), 200
    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'response': None, 'message': e.message}), 200


@rulz.route('/rulz/instrument/file/delete', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def deleteInstFile():
    response = Response()
    try:
        data = getDataRequest()

        if 'id' not in data or data['id'] is None or data['id'] == '' or data['id'] == ' ' or 'file' not in data or data['file'] is None:
            response.setMessage('Los datos aportados no son los correctos')
            response.setResponse(None)
            response.setSuccess(False)
        else:

            client = repo.get_instance(INSTANCE)
            obj = client.get_by_id(COLECTION_INSTRUMENTS, data['id'])

            for f in obj['files']:

                if f['name'] == data['file']:

                    try:
                        os.remove(f['path'])

                        del obj['files'][obj['files'].index(f)]

                        update(obj, COLECTION_INSTRUMENTS)

                        response.setMessage('Exito al eliminar el archivo ' + data['file'])
                        response.setSuccess(True)
                        response.setResponse(None)

                        return json.dumps(response.__dict__), 200

                    except Exception as e:
                        getLogger('arg_log').exception(e)
                        response.setMessage('No se pudo realizar la eliminación del archivo ' + e.message)
                        response.setSuccess(False)
                        response.setResponse(None)

                        return json.dumps(response.__dict__), 200

            response.setMessage('No se encontro el archivo deseado')
            response.setSuccess(False)
            response.setResponse(None)

    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage(e.message)
        response.setResponse(None)
        response.setSuccess(False)

    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/drls', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get_drls():
    try:
        array = []

        client = repo.get_instance(INSTANCE)

        array.extend(client.get_by_query(COLECTION_DRLS, {}))

        rules = []

        for rule in client.get_by_query(COLECTION_RULES, {}):
            rules.append({'id': rule.get('id'), 'name': rule.get('name'), 'description': rule.get('description'), 'drl': getRuleDRL(rule), 'type': 'regla', 'user_name': rule.get('user_name')})

        array.extend(rules)
        tables = []

        for table in client.get_by_query(COLECTION_TABLES, {}):
            tables.append({'id': table.get('id'), 'name': table.get('name'), 'description': table.get('description'), 'drl': getTableDRL(table), 'type': 'tabla', 'user_name': table.get('user_name')})

        array.extend(tables)

        response = {'message': 'Exito', 'success': True, 'response': array}
    except BussinessException as e:
        response = {'message': e.message, 'success': False, 'response': []}
    except Exception as e:
        getLogger('arg_log').exception(e)
        response = {'message': 'Ocurrio un error ' + e.message, 'success': False, 'response': []}
    return json.dumps(response), 200


@rulz.route('/rulz/drls/<tp>/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get_drl_of(tp, id):
    try:
        client = repo.get_instance(INSTANCE)

        if tp == 'regla':
            rule = client.get_by_id(COLECTION_RULES, id)

            drlData = {'id': rule.get('id'), 'name': rule.get('name'), 'description': rule.get('description'), 'drl': getRuleDRL(rule), 'type': 'regla', 'user_name': rule.get('user_name')}

        elif tp == 'tabla':
            table = client.get_by_id(COLECTION_TABLES, id)
            drlData = {'id': table.get('id'), 'name': table.get('name'), 'description': table.get('description'), 'drl': getTableDRL(table), 'type': 'tabla', 'user_name': table.get('user_name')}
        else:
            drlData = client.get_by_id(COLECTION_DRLS, id)

        response = {'message': 'Exito', 'success': True, 'response': drlData}
    except BussinessException as e:
        response = {'message': e.message, 'success': False, 'response': {}}
    except Exception as e:
        getLogger('arg_log').exception(e)
        response = {'message': 'Ocurrio un error ' + e.message, 'success': False, 'response': {}}
    return json.dumps(response), 200


@rulz.route('/rulz/drls_new', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def save_drls():
    response = Response()
    try:
        data = getDataRequest()

        if 'name' not in data or data['name'] is None or data['name'].strip() == '':
            return jsonify(success=False, message='debe introducir un nombre valido para el drl'), 200

        if 'id' in data and data['id'] is not None:

            if isSame(data['id'], data['name'], COLECTION_DRLS) is False:
                return jsonify(success=False, message='Ya existe un drl registrado con el nombre ' + data['name']), 200

            update(data, COLECTION_DRLS)
            response.setMessage('Se ha actualizado con exito el drl ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        elif not existName(data['name'], COLECTION_DRLS):
            data['id'] = str(uuid.uuid1())
            insert(data, COLECTION_DRLS)
            response.setMessage('Se ha almacenado con exito el drl con el nombre ' + data['name'])
            response.setSuccess(True)
            response.setResponse(data)
        else:
            response.setMessage('Ya existe un drl registrado con el nombre ' + data['name'])
            response.setSuccess(False)

    except BussinessException as be:
        response.setMessage(be.message)
        response.setSuccess(False)
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage('Se produjo un error: ' + str(e))
        response.setSuccess(False)
    return json.dumps(response.__dict__), 200


def isSame(oid, oname, col):
    client = repo.get_instance(INSTANCE)

    obj = client.get_by_query(col, {'name': oname})

    if obj is not None and obj != []:
        return obj[0]['id'] == oid

    return True


@rulz.route('/rulz/<type>/all', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def get(type):
    try:
        list = []

        col = getCollection(type)

        if col is not None and col != '':
            client = repo.get_instance(INSTANCE)

            if col == COLECTION_PUBLICATIONS:
                list = getAllPublications(client)
            else:
                list = client.get_by_query(col, {})

            response = {'message': 'Exito', 'success': True, 'response': list}
        else:
            response = {'message': 'El tipo que se ha proporsionado no es valido', 'success': False, 'response': list}
    except BussinessException as e:
        response = {'message': e.message, 'success': False, 'response': []}
    except Exception as e:
        getLogger('arg_log').exception(e)
        response = {'message': 'Ocurrio un error ' + e.message, 'success': False, 'response': []}
    return json.dumps(response), 200


def getAllPublications(client):
    try:
        eList = client.get_by_query(COLECTION_PUBLICATIONS, {})

        pList = analizer_handler.list()

        if 'success' in pList and pList['success']:

            sList = []

            for service in pList['response']:
                sList.append(service['serviceId'])

            for esc in eList:

                if (esc['name'].replace(' ', '_') + '-' + str(esc['version'])) in sList:
                    esc['installed'] = True
                else:
                    esc['installed'] = False

            return [x for x in eList]

        else:
            raise BussinessException('No se pudo conseguir la lista de escenarios publicados en el analizador')
    except BussinessException as e:
        raise e
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


@rulz.route('/rulz/<type>/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getById(type, id):
    try:
        response = Response()

        col = getCollection(type)

        if col is not None and col != '':
            client = repo.get_instance(INSTANCE)
            try:
                obj = client.get_by_id(col, id)
            except Exception, e:
                return json.dumps(response.__dict__), 404

            response.setMessage('Exito')
            response.setSuccess(True)
            response.setResponse(obj)
        else:
            response.setMessage('El tipo que se ha proporsionado no es valido')
            response.setSuccess(False)
            response.setResponse(None)
            return json.dumps(response.__dict__), 404
    except Exception as e:
        getLogger('arg_log').exception(e)
        response.setMessage(str(e))
        response.setSuccess(False)
        response.setResponse(None)
    return json.dumps(response.__dict__), 200


@rulz.route('/rulz/<type>/remove', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def delete(type):
    try:
        data = getDataRequest()

        if 'id' not in data or data['id'] is None or data['id'] == '':
            raise Exception("No se recibio ID")
        col = getCollection(type)
        if col is not None and col != '':

            client = repo.get_instance(INSTANCE)

            if col == COLECTION_PUBLICATIONS:
                if isPublished(data['name'].replace(' ', '_') + '-' + str(data['version'])):
                    raise BussinessException('No es posible eliminar una publicacion que se encuentra instalada')
            if col == COLECTION_SIMULATIONS:
                deleteSimulations(data)
            elif col == COLECTION_CATALOGS:
                deleteCatalog(data, client)
            elif col == COLECTION_LISTS:
                deleteList(data, client)
            elif col == COLECTION_TABLES or col == COLECTION_RULES:
                ty = ('tables', 'rules')[col != COLECTION_TABLES]
                deleteTablesAndRules(data, client, col, ty)
            elif col == COLECTION_ENTITYS:
                deleteEntity(data, client)
            elif col == COLECTION_INSTRUMENTS:
                deleteInstrument(data)

            client.remove(col, data['id'])
            response = {'message': 'Exito al eliminar el objeto deseado', 'success': True}

        else:
            response = {'message': 'El tipo que se ha proporsionado no es valido', 'success': False}
    except BussinessException as e:
        getLogger('arg_log').debug(e.message)
        response = {'message': e.message, 'success': False}
    except Exception as e:
        getLogger('arg_log').exception(e)
        response = {'message': 'Ocurrio un error ' + str(e), 'success': False}
    return json.dumps(response), 200


def isPublished(name):
    try:
        pList = analizer_handler.list()
        if 'success' in pList and pList['success']:
            array = []

            for serv in pList['response']:
                array.append(serv['serviceId'])

            return name in array

        else:
            raise BussinessException('No se pudo conseguir la lista de escenarios publicados en el analizador')
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def deleteCatalog(data, client):
    try:

        escs = client.get_by_query(COLECTION_SIMULATIONS, {})

        for esc in escs:
            for ct in esc['catalogs']:
                if ct['id'] == data['id']:
                    del esc['catalogs'][esc['catalogs'].index(ct)]
                    update(esc, COLECTION_SIMULATIONS)
                    break

        rids = []

        for e in data['rules']:
            rids.append(e['id'])

        query = {'id': {'$in': rids}}

        rules = client.get_by_query(COLECTION_RULES, query)

        for rule in rules:
            rule['catalog'] = {}
            update(rule)

        rids = []

        for e in data['tables']:
            rids.append(e['id'])

        query = {'id': {'$in': rids}}

        tables = client.get_by_query(COLECTION_TABLES, query)

        for table in tables:
            table['catalog'] = {}
            update(table, COLECTION_TABLES)

    except BussinessException as be:
        raise be
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def deleteEntity(data, client):
    try:
        objs = client.get_by_query(COLECTION_RULES, {'types': data['id']})

        if objs is None or len(objs) != 0:
            raise BussinessException("No se puede eliminar una entidad que se encuentra asociada a una regla (" + str(objs[0]['name']) + ')')

        objs = client.get_by_query(COLECTION_TABLES, {})

        if objs is not None:
            for obj in objs:
                for ent in obj['entities']:
                    if data['id'] == ent['entity']['id']:
                        raise BussinessException("No se puede eliminar una entidad que se encuentra asociada a una tabla (" + str(obj['name']) + ')')
    except BussinessException as be:
        raise be
    except Exception as e:
        raise e


def deleteTablesAndRules(data, client, col, ty):
    try:
        obj = client.get_by_id(col, data['id'])

        if 'catalog' in obj and obj['catalog'] is not None and 'id' in obj['catalog'] and obj['catalog']['id'] is not None and obj['catalog']['id'] != '':
            cid = obj['catalog']['id']
            cat = client.get_by_id(COLECTION_CATALOGS, cid)

            for e in cat[ty]:
                if e['id'] == data['id']:
                    del cat[ty][cat[ty].index(e)]
                    update(cat, COLECTION_CATALOGS)
                    break

    except BussinessException as be:
        raise be
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def isInPublishedCatalog(id, client):
    try:
        escs = client.get_by_query(COLECTION_SIMULATIONS, {})

        for esc in escs:
            for ct in esc['catalogs']:
                if ct['id'] == id:
                    if isPublished(esc['name'].replace(' ', '_') + '-' + esc['version']):
                        return True
                    else:
                        break

        return False
    except Exception as e:
        raise e


def deleteSimulations(data):
    try:
        if data.get('sources') is None:
            return

        files = data.get('sources').get('files')

        if files is None or files == []:
            return

        for file_info in files:
            file_path = file_info.get('path')

            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)

    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def deleteInstrument(data):
    try:
        shutil.rmtree(current_app.config['FILE_STORAGE_BUCKET_PATH'] + '/' + data['name'].replace(' ', '_'))
    except OSError as oe:
        getLogger('arg_log').exception(oe)
        if oe.errno == 2:
            return
    except BussinessException as be:
        getLogger('arg_log').debug(be)
        raise be
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def deleteList(data, client):
    try:
        objs = client.get_by_query(COLECTION_RULES, {})

        _name = data.get('name')
        _is_list = data.get('list')

        if objs is not None and len(objs) != 0:
            for rule in objs:
                need_update = False
                cond_indexes = []
                for cond_index, cond in enumerate(rule.get('rules')):
                    restrict_indexes = []
                    for index, restric in enumerate(cond.get('conds')):
                        if _is_list:
                            if restric.get('memberOf') == _name:
                                restrict_indexes.append(index)
                        else:
                            if restric.get('value') == '$PC.' + _name:
                                restrict_indexes.append(index)

                    _to_decrease = 0
                    for value in restrict_indexes:
                        del cond.get('conds')[value - _to_decrease]
                        _to_decrease += 1
                        need_update = True

                    if len(cond.get('conds')) == 0:
                        cond_indexes.append(cond_index)

                _to_decrease = 0
                for value in cond_indexes:
                    del rule.get('rules')[value - _to_decrease]
                    _to_decrease += 1
                    need_update = True

                if need_update:
                    update(rule, COLECTION_RULES)

        objs = client.get_by_query(COLECTION_TABLES, {})

        if objs is not None and len(objs) != 0:
            for table in objs:
                need_update = False

                for row in table.get('rows'):
                    for ent in row.get('entities'):
                        conds_index = []
                        for cond_index, cond in enumerate(ent.get('conds')):

                            _found = False
                            if _is_list:
                                _found = cond.get('value') == _name
                            else:
                                _found = cond.get('value') == '$PC.' + _name

                            if _found:
                                conds_index.append(cond_index)

                        _to_decrease = 0
                        for value in conds_index:
                            del ent.get('conds')[value - _to_decrease]
                            _to_decrease += 1
                            need_update = True

                if need_update:
                    update(table, COLECTION_TABLES)

        analizer_handler.deleteList(data.get('id'))

    except Exception as e:
        raise e


@rulz.route('/rulz/<type>/notincatalog', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def notInCatalog(type):
    try:
        col = ''
        if type is None or type == '':
            response = {'message': 'No se ha proporsionado el tipo de elementos a buscar', 'success': False}
        elif type == 'rule':
            col = COLECTION_RULES
        elif type == 'table':
            col = COLECTION_TABLES
        else:
            response = {'message': 'El tipo que se ha proporsionado no es valido', 'success': False}
        if col is not None and col != '':
            client = repo.get_instance(INSTANCE)
            items = client.get_by_query(col, {})

            result = []

            for item in items:
                if 'catalog' not in item or item['catalog'] is None or item['catalog'] == {}:
                    result.append(item)

            response = {'message': 'Exito', 'success': True, 'response': result}
    except Exception as e:
        getLogger('arg_log').exception(e)
        response = {'message': 'Ocurrio un error ' + str(e), 'success': False, 'response': []}
    return json.dumps(response), 200


@rulz.route('/rulz/simulate/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def simulate(id):

    try:
        client = repo.get_instance(INSTANCE)

        obj = client.get_by_id(COLECTION_SIMULATIONS, id)

        if obj.get('disabled') is True:
            return jsonify(success=False, message='No es posible realizar la simulación de un escenario que se encuentra desactivado'), 200

        sources = obj.get('sources')
        instances = obj.get('instances')
        if sources is not None:
            if instances is None:
                instances = []
                obj['instances'] = instances

            instances.extend(getFactsFromSimulationsSources(sources))

        if obj.get('instances') is None or obj['instances'] == []:
            return jsonify(success=False, message='es necesario al menos un fact para realizar la simulacion del escenario'), 200

        drl = getDRLFromSimulation(obj)

        validated = analizer_handler.validate(drl)

        if 'success' not in validated or validated['success'] is None or not validated['success']:

            validated['message'] = 'El DRL generado a partir de los dominios almacenados\
             en el sistema no es valido, razon: ' + str(validated['response'])

            return json.dumps(validated), 200

        b64 = validated['response']

        facts = []

        for inst in obj['instances']:
            facts.append({'properties': inst['instance'], 'fact_name': inst['entity']})

        tested = analizer_handler.test(b64, facts)

        return json.dumps(tested), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': e.message, 'response': None}), 200


@rulz.route('/rulz/install/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def installDRL(id):

    try:
        force = request.args.get('force')

        if force == 'true':
            force = True
        else:
            force = False

        client = repo.get_instance(INSTANCE)

        obj = client.get_by_id(COLECTION_SIMULATIONS, id)

        if 'disabled' in obj and obj['disabled'] is True:
            return jsonify(success=False, message='No es posible realizar la instalación de un escenario que se encuentra desactivado'), 200

        instList = []

        entIds = []

        drl = getDRLFromSimulation(obj, instList, entIds)

        if hasPublication(obj['name'], drl, client):
            return json.dumps({'response': None, 'success': False, 'message': 'El escenario es exactamente igual a otro publicado con el mismo nombre'}), 200

        if force is not True and sameNameAndVersion(obj['name'], obj['version'], client):
            return json.dumps({'response': None, 'success': False, 'message': 'No es posible realizar la publicacion pues ya existe una registrada para el escenario ' + obj['name'] + ' y version ' + str(obj['version']), 'retry': True}), 200

        validated = analizer_handler.validate(drl)

        if 'success' not in validated or validated['success'] is None or not validated['success']:

            validated['message'] = 'El DRL generado a partir de los dominios almacenados\
             en el sistema no es valido, razon: ' + str(validated['message'])

            return json.dumps(validated), 200

        if current_app.config.get('NEED_INSTRUMENTS') is False:
            initialDate = obj.get('initial_date')
            endingDate = obj.get('ending_date')
        else:
            initialDate = getInitialDate(instList)
            endingDate = getEndingDate(instList)

        if initialDate is not None:
            initialDate = ''.join(initialDate.split('T')[0].split('-'))

        if endingDate is not None:
            endingDate = ''.join(endingDate.split('T')[0].split('-'))

        secret_key = None

        if force is True:
            oldPub = client.get_by_query(COLECTION_PUBLICATIONS, {'name': obj['name'], 'version': obj['version']})[0]
            secret_key = oldPub.get('servicio').get('secret_key')

        installed = analizer_handler.install(obj['name'].replace(' ', '_'), str(obj['version']), validated['response'], initialDate, endingDate, secret_key)

        if 'success' in installed and installed['success'] is True:

            publication = {}

            publication['date'] = datetime.fromtimestamp(timestamp()).strftime('%Y-%m-%d %H:%M:%S')

            publication['initialDate'] = initialDate

            publication['name'] = obj['name']

            publication['version'] = obj['version']

            publication['drl'] = drl

            publication['id'] = str(uuid.uuid1())

            publication['snapshot'] = snapshots.create(obj['name'].replace(' ', '_'), str(obj['version']), 'Snapshot creado al publicar el escenario ' + str(obj['name']) + 'con version ' + str(obj['version']))

            publication['endingDate'] = endingDate

            publication['instruments'] = instList

            publication['servicio'] = getServiceSLA(obj, installed, entIds)

            if force is True:
                publication['id'] = oldPub['id']
                update(publication, COLECTION_PUBLICATIONS)
            else:
                insert(publication, COLECTION_PUBLICATIONS)

        return json.dumps(installed), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


def getServiceSLA(obj, installed, entIds):
    service_data = copy.deepcopy(SERVICE_MODEL)
    service_data['url'] = current_app.config.get('RULE_SERVER')
    service_data['rest']['servicio'] = (current_app.config.get('RULE_SERVER_BASE'), '/selectividad/rest/rule_engine/execute')[current_app.config.get('RULE_SERVER_BASE') is None] + '/' + obj['name'].replace(' ', '_') + '/' + str(obj['version'])
    service_data['rest']['method'] = 'POST'

    if 'soap' in installed and installed['soap'] is not None:
        service_data['soap'] = installed['soap']
    else:
        service_data['soap'] = None

    if 'response' in installed and installed['response'] is not None:
        service_data['secret_key'] = installed['response']

    facts = getFactsModel(entIds)

    if facts is not None:
        service_data['data']['facts'] = facts
    elif 'servicio' in obj and obj['servicio'] is not None and 'data' in obj['servicio']:
        service_data['data'] = obj['servicio']['data']

    return service_data


def getFactsModel(ids):

    if ids is None or len(ids) == 0:
        return None

    client = repo.get_instance(INSTANCE)

    objs = client.get_by_query(COLECTION_ENTITYS, {'id': {'$in': list(ids)}})

    facts = []

    for obj in objs:
        prop = {}
        plainFact(obj['schema']['properties'], prop)
        facts.append({'fact_name': upcase_first_letter(obj['name']), 'properties': prop})

    return facts


def plainFact(obj, tobj):
    for key in obj:
        value = obj[key]
        if value['type'] != 'object':
            tobj[key] = None
        else:
            tobj[key] = {}
            plainFact(value['properties'], tobj[key])


def hasPublication(name, drl, client):
    objs = client.get_by_query(COLECTION_PUBLICATIONS, {'name': name})
    if objs is not None and len(objs) != 0 and drl is not None and drl != '':
        return objs[0]['drl'] == drl
    return False


def sameNameAndVersion(name, version, client):
    objs = client.get_by_query(COLECTION_PUBLICATIONS, {'name': name, 'version': version})
    return objs is not None and len(objs) != 0

'''
%Y-%m-%dT%H:%M:%S.%fZ
'''


def getEndingDate(instList):
    try:
        client = repo.get_instance(INSTANCE)
        instruments = client.get_by_query(COLECTION_INSTRUMENTS, {'id': {'$in': instList}})
        dates = []

        for instrument in instruments:
            dates.append(instrument['ending_date'])

        if len(dates) == 0:
            return None
        return min(dates)
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def getInitialDate(instList):
    try:
        client = repo.get_instance(INSTANCE)
        instruments = client.get_by_query(COLECTION_INSTRUMENTS, {'id': {'$in': instList}})
        dates = []

        for instrument in instruments:
            dates.append(instrument['application_date'])

        if len(dates) == 0:
            return None
        return max(dates)
    except Exception as e:
        getLogger('arg_log').exception(e)
        raise e


def getDRLFromSimulation(sim, instList=None, eids=[]):
    try:
        dic = mvelsFromCatalogs(sim['catalogs'], instList)

        mvels = dic['mvels']

        se = dic['entid']

        fNames = dic['functNames']

        eids.extend(se)

        declares = getDeclares(se)

        functions = getFunctions(fNames)

        drl = engine.getStructure().format('\n'.join(declares), '\n'.join(mvels), current_app.config['RULE_DIALECT'], functions)

        getLogger('arg_log').debug("DRL generado:\n" + drl)

        return drl
    except Exception as e:
        raise e


@rulz.route('/rulz/install/publication/<id>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def installPublication(id):
    try:
        client = repo.get_instance(INSTANCE)

        obj = client.get_by_id(COLECTION_PUBLICATIONS, id)

        if not isPublished(obj['name'].replace(' ', '_') + '-' + str(obj['version'])):

            initDate = None
            finDate = None
            secret_key = None

            if 'initialDate' in obj:
                initDate = obj['initialDate']

            if 'endingDate' in obj:
                finDate = obj['endingDate']

            if obj.get('servicio') is not None and obj['servicio'].get('secret_key') is not None:
                secret_key = obj['servicio']['secret_key']

            installed = analizer_handler.install(obj['name'].replace(' ', '_'), str(obj['version']), base64.b64encode(obj['drl']), initDate, finDate, secret_key)

            if 'success' in installed and installed['success'] is True:

                obj['date'] = datetime.fromtimestamp(timestamp()).strftime('%Y-%m-%d %H:%M:%S')

                obj['servicio'] = getServiceSLA(obj, installed, [])

                update(obj, COLECTION_PUBLICATIONS)

            return json.dumps(installed), 200

        else:
            return json.dumps({'success': False, 'message': 'La publicacion ya se encuentra instalada', 'response': None}), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'response': None, 'message': e.message, 'success': False}), 200


@rulz.route('/rulz/uninstall/publication/<id>', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def uninstallPublication(id):
    try:
        client = repo.get_instance(INSTANCE)

        obj = client.get_by_id(COLECTION_PUBLICATIONS, id)

        if isPublished(obj['name'].replace(' ', '_') + '-' + str(obj['version'])):

            secret_key = None

            if obj.get('servicio') is not None and obj['servicio'].get('secret_key') is not None:
                secret_key = obj['servicio']['secret_key']

            uninstalled = analizer_handler.uninstall(obj['name'].replace(' ', '_'), str(obj['version']), secret_key)

            return json.dumps(uninstalled), 200

        else:
            return json.dumps({'success': False, 'message': 'La publicacion no se encuentra instalada', 'response': None}), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'response': None, 'message': e.message, 'success': False}), 200


@rulz.route('/rulz/uninstall/<id>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def uninstallDRL(id):

    try:
        client = repo.get_instance(INSTANCE)

        obj = client.get_by_id(COLECTION_SIMULATIONS, id)

        if isPublished(obj['name'].replace(' ', '_') + '-' + str(obj['version'])):

            secret_key = None

            if obj.get('servicio') is not None and obj['servicio'].get('secret_key') is not None:
                secret_key = obj['servicio']['secret_key']

            uninstalled = analizer_handler.uninstall(obj['name'].replace(' ', '_'), str(obj['version']), secret_key)

            return json.dumps(uninstalled), 200

        else:
            return json.dumps({'success': False, 'message': 'El escenario no se encuentra instalado', 'response': None}), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


@rulz.route('/rulz/test', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def testValidate():
    try:

        drl = request.data

        return json.dumps(analizer_handler.validate(drl)), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


@rulz.route('/rulz/test/data', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def testTestData():
    try:
        data = getDataRequest()

        rule = data['drl']
        facts = data['facts']

        tested = analizer_handler.test(rule, facts)

        return json.dumps(tested), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


@rulz.route('/rulz/test/install', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def installTEST():

    try:
        data = getDataRequest()

        force = request.args.get('force')

        if force == 'true':
            force = True
        else:
            force = False

        client = repo.get_instance(INSTANCE)

        drl = decode_base64(data['drl'])

        if hasPublication(data['name'], drl, client):
            return json.dumps({'response': None, 'success': False, 'message': 'Ya existe una publicacion con el nombre y drl proporcionados'}), 200

        if force is not True and sameNameAndVersion(data['name'], data['version'], client):
            return json.dumps({'response': None, 'success': False, 'message': 'No es posible realizar la publicacion pues ya existe una registrada para el escenario ' + data['name'] + ' y version ' + str(data['version']), 'retry': True}), 200

        initialDate = data.get('initial_date')
        endingDate = data.get('ending_date')

        if initialDate is not None:
            initialDate = ''.join(initialDate.split('T')[0].split('-'))

        if endingDate is not None:
            endingDate = ''.join(endingDate.split('T')[0].split('-'))

        secret_key = None

        if force is True:
            oldPub = client.get_by_query(COLECTION_PUBLICATIONS, {'name': data['name'], 'version': data['version']})[0]
            secret_key = oldPub.get('servicio').get('secret_key')
            data['servicio'] = oldPub.get('servicio')

        installed = analizer_handler.install(data['name'].replace(' ', '_'), str(data['version']), data['drl'], initialDate, endingDate, secret_key)

        if 'success' in installed and installed['success'] is True:

            publication = {}

            publication['date'] = datetime.fromtimestamp(timestamp()).strftime('%Y-%m-%d %H:%M:%S')

            publication['initialDate'] = initialDate

            publication['name'] = data['name']

            publication['version'] = data['version']

            publication['drl'] = drl

            publication['id'] = str(uuid.uuid1())

            publication['endingDate'] = endingDate

            publication['instruments'] = None

            publication['servicio'] = getServiceSLA(data, installed, None)

            if force is True:
                publication['id'] = oldPub['id']
                update(publication, COLECTION_PUBLICATIONS)
            else:
                publication['snapshot'] = "Desde editor DRL"
                insert(publication, COLECTION_PUBLICATIONS)

        return json.dumps(installed), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


@rulz.route('/rulz/test/uninstall', methods=['POST'])
@cross_origin(headers=['Content-Type'])
@secure_service
def uninstallTest():

    try:
        data = getDataRequest()

        uninstalled = analizer_handler.uninstall(data['name'], data['version'])

        return json.dumps(uninstalled), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


@rulz.route('/rulz/test/list', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@secure_service
def getTestList():

    try:

        return json.dumps(analizer_handler.list()), 200

    except Exception as e:
        getLogger('arg_log').exception(e)
        return json.dumps({'success': False, 'message': str(e), 'response': None}), 200


def getCollection(type):
    try:
        if type is None or type == '':
            return ''
        elif type == 'rule':
            return COLECTION_RULES
        elif type == 'entity':
            return COLECTION_ENTITYS
        elif type == 'simulation':
            return COLECTION_SIMULATIONS
        elif type == 'table':
            return COLECTION_TABLES
        elif type == 'catalog':
            return COLECTION_CATALOGS
        elif type == 'list':
            return COLECTION_LISTS
        elif type == 'instrument':
            return COLECTION_INSTRUMENTS
        elif type == 'function':
            return COLECTION_FUNCTIONS
        elif type == 'formula':
            return COLECTION_FORMULAS
        elif type == 'publication':
            return COLECTION_PUBLICATIONS
        elif type == 'drls':
            return COLECTION_DRLS
        else:
            return ''
    except Exception as e:
        getLogger('arg_log').exception(e)
        return ''


def insert(source, col=COLECTION_RULES):
    client = repo.get_instance(INSTANCE)
    client.saveRlz(col, source)
    return


def update(source, col=COLECTION_RULES):
    client = repo.get_instance(INSTANCE)
    client.updateRlz(col, source['id'], source)
    return


def existName(name, col=COLECTION_RULES):
    try:
        client = repo.get_instance(INSTANCE)
        info = client.get_by_field(col, "name", name)
        if info:
            d = info[0]
        else:
            return False
        return d['name'] == name
    except Exception as e:
        getLogger('arg_log').exception(e)
        return False


def sameName(oid, oname, col):
    try:
        client = repo.get_instance(INSTANCE)
        obj = client.get_by_id(col, oid)

        if obj['name'] != oname:
            raise BussinessException('El nombre de una entidad no puede ser modificado cuando se encuentra asociada a una regla o tabla')
    except Exception as e:
        raise e


def existVersion(name, ver):
    try:
        client = repo.get_instance(INSTANCE)
        query = {'name': name, 'version': ver}
        info = client.get_by_query(COLECTION_SIMULATIONS, query)
        if info is not None and len(info) != 0:
            d = info[0]
        else:
            return False
        return d['version'] == ver
    except Exception, e:
        getLogger('arg_log').exception(e)
        return False


def updateCatalogs(objId, objName, catalogId, type):
    try:
        if type is None or type == '':
            return False
        query = {}

        client = repo.get_instance(INSTANCE)
        catalogs = client.get_by_query(COLECTION_CATALOGS, query)

        for catalog in catalogs:
            elements = catalog[type]
            for values in elements:
                if 'id' in values and values['id'] == objId:
                    del elements[elements.index(values)]
                    update(catalog, COLECTION_CATALOGS)
                    break

        try:
            catalog = client.get_by_id(COLECTION_CATALOGS, catalogId)
            catalog[type].append({'id': objId, 'name': objName})
            update(catalog, COLECTION_CATALOGS)
        except Exception as ex:
            getLogger('arg_log').exception(ex)

        return True
    except Exception as e:
        getLogger('arg_log').exception(e)
        return False


def updateCatalogReference(data):

    try:
        client = repo.get_instance(INSTANCE)

        rids = []

        rules = client.get_by_query(COLECTION_RULES, {})

        for r in rules:
            if 'catalog' in r and r['catalog'] is not None and len(r['catalog']) != 0 and r['catalog']['id'] == data['id']:
                r['catalog'] = {}
                update(r)

        rules = []

        for e in data['rules']:
            rids.append(e['id'])

        query = {'id': {'$in': rids}}

        rules = client.get_by_query(COLECTION_RULES, query)

        for rule in rules:
            ct = {'id': data['id'], 'name': data['name']}
            rule['catalog'] = ct
            update(rule)

        rids = []

        tables = client.get_by_query(COLECTION_TABLES, {})

        for t in tables:
            if 'catalog' in t and t['catalog'] is not None and 'id' in t['catalog'] and t['catalog']['id'] == data['id']:
                t['catalog'] = {}
                update(t, COLECTION_TABLES)

        for e in data['tables']:
            rids.append(e['id'])

        query = {'id': {'$in': rids}}

        tables = client.get_by_query(COLECTION_TABLES, query)

        for table in tables:
            ct = {'id': data['id'], 'name': data['name']}
            table['catalog'] = ct
            update(table, COLECTION_TABLES)

        sims = client.get_by_query(COLECTION_SIMULATIONS, {})

        for sim in sims:
            upd = False
            for cat in sim['catalogs']:
                if cat['id'] == data['id']:
                    cat['name'] = data['name']
                    upd = True
                    break

            if upd:
                update(sim, COLECTION_SIMULATIONS)

        return True
    except Exception as e:
        getLogger('arg_log').exception(e)
        return False


def mvelsFromCatalogs(catalogs=[], instList=None):
    try:
        se = set()
        mvels = []
        functNames = []
        client = repo.get_instance(INSTANCE)
        if catalogs is None:
            return mvels

        i = 0

        n = len(catalogs)

        for catalogId in catalogs:

            try:
                catalog = client.get_by_id(COLECTION_CATALOGS, catalogId['id'])
            except Exception, e:
                catalog = None

            if catalog is None:
                continue

            salience = (n - i) * 1000

            for ruleObj in catalog['rules']:
                ei = catalog['rules'].index(ruleObj)
                try:
                    rule = client.get_by_id(COLECTION_RULES, ruleObj['id'])
                except Exception, e:
                    rule = None

                if rule is None:
                    continue

                rule['salience'] = salience - (ei * 10)

                mvels.append(engine.makeRuleMVEL(rule, functNames))

                for eid in rule['types']:
                    se.add(eid)

                if 'instruments' in rule and instList is not None:
                    for instrument in rule['instruments']:
                        if instrument['id'] not in instList:
                            instList.append(instrument['id'])

            for tableId in catalog['tables']:

                try:
                    table = client.get_by_id(COLECTION_TABLES, tableId['id'])
                except Exception, e:
                    table = None

                if table is None:
                    continue

                table['salience'] = salience - 10
                mvels.append(engine.makeTableMVEL(table, functNames))

                for entid in table['entities']:
                    se.add(entid['entity']['id'])

                if 'instruments' in table and instList is not None:
                    for instrument in table['instruments']:
                        if instrument['id'] not in instList:
                            instList.append(instrument['id'])

            i += 1

        resp = {'mvels': mvels, 'entid': se, 'functNames': list(set(functNames))}

        return resp
    except Exception as e:
        getLogger('arg_log').exception(e)
        return {'mvels': [], 'entid': set()}


def getDeclares(eids=set()):
    try:
        client = repo.get_instance(INSTANCE)
        declares = []

        query = {'id': {'$in': list(eids)}}

        entitys = client.get_by_query(COLECTION_ENTITYS, query)

        for entity in entitys:

            schema = entity['schema']

            schema['properties']['fact_id'] = {'type': 'string'}

            declares.extend(engine.makeDeclares(entity['name'], schema['properties']))

        return declares
    except Exception as e:
        getLogger('arg_log').exception(e)
        return []


# def getConstants():
#     try:
#         client = repo.get_instance(INSTANCE)

#         li = client.get_by_query(COLECTION_LISTS, {})
#         constant = engine.declareList(li)
#         return constant
#     except Exception as e:
#         getLogger('arg_log').exception(e)
#         return engine.getConstantStructure()


# def getConstantsValues():
#     try:
#         client = repo.get_instance(INSTANCE)

#         li = client.get_by_query(COLECTION_LISTS, {})
#         values = engine.declarListsValues(li)
#         return values
#     except Exception as e:
#         getLogger('arg_log').exception(e)
#         return ''


def getFunctions(fnames=[]):
    try:
        query = {'name': {'$in': list(fnames)}}

        client = repo.get_instance(INSTANCE)

        li = client.get_by_query(COLECTION_FUNCTIONS, query)

        ar = []

        for f in li:
            ar.append(engine.makeFunctionMVEL(f))

        return '\n'.join(ar)
    except Exception as e:
        getLogger('arg_log').exception(e)
        return ''
