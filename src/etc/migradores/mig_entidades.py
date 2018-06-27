import json
from pymongo import MongoClient


def doit():
    client = MongoClient('127.0.0.1', 27017)
    schema = client['rulz_luzia']
    entitys = schema['entitys'].find({})

    for entity in entitys:
        del entity['_id']
        migrate(entity['schema']['properties'])
        schema['entitys'].update({'id': entity['id']}, entity)


def migrate(properties):
    print json.dumps(properties)

    for key in properties:
        print properties[key]['type']
        if properties[key]['type'] == 'integer':
            properties[key]['type'] = 'long'
        elif properties[key]['type'] == 'float':
            properties[key]['type'] = 'double'
        elif properties[key]['type'] == 'object':
            migrate(properties[key]['properties'])
