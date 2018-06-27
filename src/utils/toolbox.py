# -*- coding: UTF-8 -*-

import os
import json
import shutil
import copy
import base64 as b64
import datetime
import logging
import logging.config

from flask import current_app
from werkzeug import secure_filename
from M2Crypto import RSA
import dateutil.parser as date_parser
import httplib2 as http
import yaml
import xlrd
import xlsxwriter
import csv

import repo
import conection_manager

NOT_ALLOWED_FILES = ['sh', 'py', 'js', 'java', 'exe', 'war', 'jar', 'deb', 'bat', 'vbs', 'php', 'asp', 'jsp', 'dll']
RESERVED_WORDS = ['SUMAR', 'MAXIMO', 'MINIMO', 'PROMEDIO', 'CONTAR']
ACUMULADORES = {'SUMAR': 'sum', 'MAXIMO': 'max', 'MINIMO': 'min', 'PROMEDIO': 'average', 'CONTAR': 'count'}


class BussinessException(Exception):
    def __init__(self, message):
        self.message = message


def gen_key(pem_path, cipher=None):
    rsaKey = RSA.gen_key(2048, 65537)
    rsaKey.save_pem(pem_path, cipher=cipher)


def rsa_encrypt(pem_path, plain_text):
    ReadRSA = RSA.load_key(pem_path)
    return b64.b64encode(ReadRSA.public_encrypt(plain_text, RSA.pkcs1_padding))


def rsa_decrypt(pem_path, b64_text):
    ReadRSA = RSA.load_key(pem_path)
    return ReadRSA.private_decrypt(b64.b64decode(b64_text), RSA.pkcs1_padding)


def json_decoder(message):
    return json.loads(json.dumps(message, encoding="iso-8859-1"))


def multiSelection_to_text(message):
    result_text = []
    for linea in message:
        result_text.append(linea['text'])
    return ', '.join(result_text)


def server_is_alive(url):
    try:
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(url, "GET", {'Content-Type': 'application/json; charset=UTF-8'})
        return True
    except Exception, ex:
        return False
        current_app.logger.error("No se ha logrado la conexion con el server: {0}".format(url))
        current_app.logger.exception(ex)


def valida_cuit(message):
    cuit = str(message.replace('-', ''))
    if len(cuit) != 11:
        return False
    else:
        base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        aux = 0
        for i in xrange(10):
            aux += int(cuit[i]) * base[i]
        aux = 11 - (aux - (int(aux / 11) * 11))
        if aux == 11:
            aux = 0
        if aux == 10:
            aux = 9
        if aux != int(cuit[10]):
            return False

    return True


class Response():

    success = False
    response = {}
    message = ""

    def setSuccess(self, success):
        self.success = success

    def getSuccess(self):
        return self.success

    def setResponse(self, response):
        self.response = response

    def getResponse(self):
        return self.response

    def setMessage(self, message):
        self.message = message

    def getMessage(self):
        return self.message

'''
Funciones sobre archivos (instrumentos normativos)
:Authors
    - Enzo D. Grosso
'''


def createFiles(data, files):
    if(files is None):
        return
    try:
        folder = current_app.config['FILE_STORAGE_BUCKET_PATH'] + '/' + data['name'].replace(' ', '_') + '/'
        ensure_dir(folder)
        for f in files:
            if f and allowed_file(f['filename']):
                filename = secure_filename(f['filename'])

                with open(os.path.join(folder, filename), 'w') as fil:
                    fil.write(b64.b64decode(f['base64']))

                size = os.path.getsize(os.path.join(folder, filename))
                data['files'].append({'name': filename, 'path': folder + filename, 'filetype': f['filetype'], 'size': size})
            else:
                if f:
                    raise BussinessException('El archivo "' + f['filename'] + '" posee una extención no permitida')
    except Exception, e:
        raise e


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] not in NOT_ALLOWED_FILES


def ensure_dir(folder):
    d = os.path.dirname(folder)
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno == 13:
                raise BussinessException('No se poseen permisos para crear los archivos en el sistema')


def makeModelForSimulation(data):
    try:
        client = repo.get_instance('rulz')

        tpids = getTypes(data, client)

        folder = current_app.config['TMP_FOLDER'] + '/export_model/'
        ensure_dir(folder)

        workbook = xlsxwriter.Workbook(folder + data['name'] + '.xlsx')

        for tid in tpids:
            try:
                entity = client.get_by_id('entitys', tid)
            except Exception as e:
                entity = None

            if entity is None:
                continue

            # fields = [x['name'] if x['name'] != 'this' else entity['name'] for x in entity['plainAttr']]

            fields = []

            for x in entity['plainAttr']:
                if x['name'] != 'this' and x['type'] != 'object':
                    fields.append(x['name'])
                elif x['name'] == 'this':
                    fields.append(entity['name'])

            worksheet = workbook.add_worksheet()

            worksheet.write_row('A1', fields)

        workbook.close()

        f = open(folder + data['name'] + '.xlsx')

        bb = b64.b64encode(f.read())

        f.close()

        os.remove(folder + data['name'] + '.xlsx')

        return bb

    except Exception as e:
        raise e


def getTypes(data, client):
    try:
        tpids = set()

        for catalogId in data['catalogs']:
            try:
                catalog = client.get_by_id('catalogs', catalogId['id'])
            except Exception as e:
                catalog = None

            if catalog is None:
                continue

            for ruleObj in catalog['rules']:
                try:
                    rule = client.get_by_id('rules', ruleObj['id'])
                except Exception, e:
                    rule = None

                if rule is None:
                    continue

                for eid in rule['types']:
                    tpids.add(eid)

            for tableId in catalog['tables']:

                try:
                    table = client.get_by_id('tables', tableId['id'])
                except Exception, e:
                    table = None

                if table is None:
                    continue

                for entid in table['entities']:
                    tpids.add(entid['entity']['id'])

        return list(tpids)

    except Exception as e:
        raise e


def xlsToCsv(xlsFile, csvBase, csvs=[]):
    workbook = xlrd.open_workbook(xlsFile)

    nroSheets = workbook.nsheets

    if nroSheets == 0:
        return

    for i in xrange(nroSheets):
        currentCSV = csvBase + str(i) + '.csv'
        csvs.append(currentCSV)

        with open(currentCSV, 'wb') as csvfile:
            wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            worksheet = workbook.sheet_by_index(i)

            for rownum in xrange(worksheet.nrows):
                wr.writerow(list(x.encode('utf-8') if isinstance(x, unicode) else x for x in worksheet.row_values(rownum)))


def storeJsonScenario(scenario, payload):
    folder = current_app.config.get('FILE_STORAGE_FACTS')

    file_name = scenario + '.' + datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + '.json'

    file_path = folder + os.sep + file_name

    ensure_dir(file_path)

    with open(file_path, 'w') as fil:
        payload_str = json.dumps(payload)

        fil.write(payload_str)

    number_facts = 0
    for key in payload:
        value = payload.get(key)

        if value is None:
            continue

        number_facts += len(value)

    file_info = {
        'name': file_name,
        'path': file_path,
        'facts': number_facts
    }

    return file_info


def getJsons(data):
    try:
        folder = current_app.config['TMP_FOLDER'] + '/import/'
        ensure_dir(folder)
        f = data['file']
        models = data['models']
        jsons = {}

        if f:

            filename = secure_filename(f['filename'])

            with open(os.path.join(folder, filename), 'w') as fil:
                fil.write(b64.b64decode(f['base64']))

            csvs = []
            xlsToCsv(os.path.join(folder, filename), os.path.join(folder, filename.rsplit('.', 1)[0]), csvs)
            if len(csvs) == 0:
                deletetmp()
                return jsons

            work(models, csvs, jsons)

            deletetmp()

            return jsons

        raise BussinessException('El archivo no es valido')
    except Exception as e:
        current_app.logger.exception(e)
        raise e


def work(models, csvs, jsons={}):
    for csvpath in csvs:
        info = getInfoFromCSV(csvpath)

        if info['type'] not in models or models[info['type']] is None:
            deletetmp()
            raise BussinessException('La entidad ' + info['type'] + ' no es valida, por favor no modifique las cabeceras del excel modelo')

        if info['type'] not in jsons or jsons[info['type']] is None:
            jsons[info['type']] = []

        model = models[info['type']]

        attrsTypes = getAttrsTypes(info['type'])

        cant = 0

        for row in info['rows']:
            if cant == 100000:
                deletetmp()
                raise BussinessException('No es posible generar más de 1000 elementos de la misma entidad')
            jsons[info['type']].append(buildJSON(copy.deepcopy(model), info['headers'], row, attrsTypes))
            cant += 1

    return jsons


def getAttrsTypes(etype):
    try:
        client = repo.get_instance('rulz')
        obj = client.get_by_query('entitys', {'name': etype})

        if obj is None or obj == []:
            raise BussinessException('La entidad ' + etype + ' no es valida, por favor no modifique las cabeceras del excel modelo')

        obj = obj[0]

        attrsTypes = {}

        for x in obj['plainAttr']:
            if x['name'] != 'this' and x['type'] != 'object':
                attrsTypes[x['name']] = x['type']

        return attrsTypes
    except Exception as e:
        current_app.logger.exception(e)
        raise e


def getInfoFromCSV(csvpath):
    info = {}

    with open(csvpath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        headers = reader.next()
        tp = eval(headers[0])
        headers = [eval(x) for x in headers if headers.index(x) != 0]
        rows = []

        for row in reader:
            xrow = []
            for i, x in enumerate(row):
                if i != 0:
                    xrow.append(eval(x))
            rows.append(xrow)

        info['headers'] = headers
        info['type'] = tp
        info['rows'] = rows

    return info


def buildJSON(model, headers, values, attrsTypes):

    for i in xrange(len(values)):

        if headers[i] not in attrsTypes:
            continue
        sp = headers[i].split('.')

        inerLVL(model, values[i], sp, attrsTypes[headers[i]])

    return model


def inerLVL(model, value, headers, attrType):
    if len(headers) == 1:
        if value != '' and value is not None:
            try:
                value = validateType(value, attrType)
            except ValueError:
                raise BussinessException('El atributo ' + headers[0] + ' es de tipo ' + attrType + ' pero el valor encontrado ' + str(value) + ' no es compatible, por favor verifique los datos cargados en el excel')
        model[headers[0]] = value
    else:
        inerLVL(model[headers[0]], value, headers[1:], attrType)


def validateType(value, attrType):
    if attrType.lower() == 'string':
        return value
    elif attrType.lower() == 'integer' or attrType.lower() == 'long':
        return long(float(value))
    elif attrType.lower() == 'float' or attrType.lower() == 'double':
        return float(value)
    elif attrType.lower() == 'boolean':
        if value == 'True' or value == 'true' or value == 'verdadero':
            return True
        else:
            return False
    elif attrType.lower() == 'date':
        value = float(value)
        tple = xlrd.xldate_as_tuple(value, 0)
        value = str(tple[0]).zfill(4) + '-' + str(tple[1]).zfill(2) + '-' + str(tple[2]).zfill(2) + 'T' + str(tple[3]).zfill(2) + ':' + str(tple[4]).zfill(2) + ':' + str(tple[5]).zfill(2) + '.000Z'
        return value
    else:
        return None


def getFactsFromSimulationsSources(sources):

    facts = []
    if sources is None or sources == {}:
        return facts

    services = sources.get('services')

    if services is not None and services != []:
        models = {}

        for service in services:
            kindId = service.get('entityId')

            model = models.get(kindId)
            if model is None:
                model = getEntityModel(kindId)
                models[kindId] = model

            facts.extend(getFactsFromService(service.get('url'), model))

    files = sources.get('files')

    if files is not None and files != []:

        for file_info in files:
            facts.extend(getFactsFromFile(file_info))

    return facts


def getFactsFromFile(file_info):
    file_path = file_info.get('path')

    facts = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as fil:
            fil_payload = fil.read()

            jsons = json.loads(fil_payload)

            for key in jsons:
                array = jsons.get(key)

                for _json in array:
                    fact = {
                        'entity': key,
                        'instance': _json
                    }

                    facts.append(fact)

    return facts


def getFactsFromService(url, model):
    facts = []
    if url is None:
        raise BussinessException('El servicio proporcionado es erroneo')

    srv_resp = conection_manager.get(url)

    if type(srv_resp) != dict and (type(srv_resp) == unicode or type(srv_resp) == str):
        try:
            srv_resp = json.loads(srv_resp)
        except Exception:
            raise BussinessException('Error contactando servicio de obtención de facts: ' + url)

    if srv_resp.get('success') is not True or srv_resp.get('response') is None:
        raise BussinessException('No se pudieron obtener facts del servicio ' + url)

    array = srv_resp.get('response')

    for event in array:
        if event is None:
            continue

        try:
            checkProperties(model.get('model'), event)
        except Exception:
            continue

        fact = {
            'entity': model.get('name'),
            'instance': event
        }

        facts.append(fact)

    return facts


def getEntityModel(kindId):
    if kindId is None:
        return None

    client = repo.get_instance('rulz')

    entity = client.get_by_id('entitys', kindId)

    if entity is None:
        return None

    model = {
        'name': entity.get('name'),
        'model': entity.get('schema').get('properties')
    }

    return model


def checkProperties(properties, event):
    for key in properties:
        value = properties.get(key)
        this_type = value.get('type')
        if this_type == "object":
            checkProperties(value.get('properties'), event.get(key))
        else:
            this_value = event.get(key)
            this_value_type = type(this_value)
            if this_type == 'boolean' and this_value_type != bool:
                raise TypeError('El campo ' + key + ' no es un booleano valido')
            elif this_type == 'integer' and (this_value_type != int and this_value_type != long):
                raise TypeError('El campo ' + key + ' no es un numero valido')
            elif this_type == 'string' and (this_value_type != unicode and this_value_type != str):
                raise TypeError('El campo ' + key + ' no es un string valido')
            elif this_type == 'date' and (this_value_type == unicode or this_value_type == str):
                try:
                    date_parser.parse(this_value)
                except Exception:
                    raise TypeError('El campo ' + key + ' no es una fecha valida')


def deletetmp():
    try:
        shutil.rmtree(current_app.config['TMP_FOLDER'] + '/import')
    except OSError as oe:
        current_app.logger.exception(oe)
        if oe.errno == 2:
            return
    except BussinessException as be:
        current_app.logger.exception(be)
        raise be
    except Exception as e:
        current_app.logger.exception(e)
        raise e


def indexOf(string, value):

    try:
        i = string.index(value)
    except ValueError:
        i = -1

    return i


def infixtopostfix(infixexpr):

    s = StackClass([])
    outlst = []
    prec = {}
    prec['/'] = 3
    prec['*'] = 3
    prec['+'] = 2
    prec['-'] = 2
    prec['('] = 1

    if infixexpr.strip() == '':
        raise BussinessException('Linea vacia')

    tokenlst = infixexpr.strip().split()

    for token in tokenlst:

        if asNumber(token) is not None:
            outlst.append(token)
        elif len(token.split('(')) != 0 and ''.join(token.split('(')) != '' and token.split('(')[0] in RESERVED_WORDS:
            outlst.append(token)

        elif token == '(':
            s.push(token)

        elif token == ')':
            try:
                topToken = s.pop()
                while topToken != '(':
                    outlst.append(topToken)
                    topToken = s.pop()
            except IndexError:
                raise BussinessException('Parentesis de cierre sin su apertura correspondiente')
        else:
            try:
                while (not s.isEmpty()) and (prec[s.peek()] >= prec[token]):
                    outlst.append(s.pop())

                s.push(token)
            except KeyError as ke:
                raise BussinessException('La palabra ' + str(ke) + ' no se encuentra dentro de las palabras reservadas, por favor verifique la formula')

    while not s.isEmpty():
        opToken = s.pop()
        outlst.append(opToken)

    if s.isEmpty():
        return outlst

    raise BussinessException('No se logro vaciar el stack de elementos, verifique que no exista una apertura de parentesis sin su cierre correspondiente')


class StackClass:

    def __init__(self, itemlist=[]):
        self.items = itemlist

    def isEmpty(self):
        if self.items == []:
            return True
        else:
            return False

    def peek(self):
        return self.items[-1:][0]

    def pop(self):
        return self.items.pop()

    def push(self, item):
        self.items.append(item)
        return 0


def asNumber(val):
    if val is None or val == '':
        return None
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return None


def upcase_first_letter(s):
    return s[0].upper() + s[1:]


def configLogger():
    logger_path = current_app.config.get("LOGGER_CONFIG")

    if logger_path is not None:
        with open(logger_path) as f:
            D = yaml.load(f)
            D.setdefault('version', 1)
            logging.config.dictConfig(D)
    else:
        with open(current_app.config["APP_PATH"] + '/src/arg-logger-config.yaml') as f:
            D = yaml.load(f)
            D.setdefault('version', 1)
            logging.config.dictConfig(D)


def dict_diff(actual, original):
    return dict([
                (key, original.get(key, actual.get(key)))
                for key in set(actual.keys() + original.keys())
                if ((key in actual and (key not in original or actual[key] != original[key])) or (key in original and (key not in actual or actual[key] != original[key])))])


def is_alike(spattern, spath):

    if len(spattern) != len(spath):
        return False

    for inx, elem in enumerate(spattern):
        if (elem == '*'):
            continue
        if not (elem == spath[inx]):
            return False
    return True


def decode_base64(data):
    """Decode base64, padding being optional.
    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.
    """

    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'=' * missing_padding

    return b64.decodestring(data)
