import json
from pymongo import MongoClient
import uuid
from flask import request, current_app, session
import redis
import sys
import base64 as b64
from M2Crypto import RSA


# Data is stored in public db
PUBLIC_DATA = "PUBLIC"

# Data is stored in organization_id storage and only owner can read
PRIVATE_DATA = "PRIVATE"
# Data is stored in organization_id storage and all organization members can read
MEMBERS_DATA = "MEMBERS"


class Repository():

    schema = ""
    token = {}
    c = None

    def __init__(self, id):

        if current_app.config.get("MONGO_SECURITY_ENABLED") is True:

            ReadRSA = RSA.load_key(current_app.config['PRIVATE_KEY_PATH'])
            mongo_plain_password = ReadRSA.private_decrypt(b64.b64decode(current_app.config.get("MONGO_PASS")), RSA.pkcs1_padding)
            connection_string = "mongodb://{0}:{1}@{2}:{3}".format(current_app.config.get("MONGO_USER"), mongo_plain_password, current_app.config.get("MONGO_HOST"), current_app.config.get("MONGO_PORT"))
            self.c = MongoClient(connection_string)

        else:
            self.c = MongoClient(current_app.config['MONGO_HOST'], current_app.config['MONGO_PORT'])

        r = redis.StrictRedis(host=current_app.config.get('REDIS_HOST'), port=current_app.config.get('REDIS_PORT'), db=0)

        if type(id) is not dict:

            token_id = request.headers.get("Authorization")

            if token_id is None:
                token_id = session['token_id']

            if token_id is not None:
                self.token = json.loads(r.get(token_id))

                if type(self.token['organization']) is dict:
                    id = id + "_" + self.token['organization']['organization_id']
                else:
                    id = id + "_" + self.token['organization']
        else:
            id = id['instance'] + '_luzia'

        self.schema = self.c[id]

    def save(self, collection_name, message, visibility=MEMBERS_DATA):
        id = uuid.uuid4()
        message["id"] = str(id)
        message["commiter"] = {"userid": self.token["uid"], "token_id": request.headers.get("Authorization")}

        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].save(message)

        if visibility == PUBLIC_DATA:
            self.c["public"]["collection_name"].save(message)

        # if self.token["one_shoot"]==True:
        #   r = redis.StrictRedis(host='localhost', port=6379, db=0)
        #   r.delete(self.token["token"])

        return id

    def save_audit(self, collection_name, message):

        self.schema[collection_name].save(message)

        return True

    def saveRlz(self, collection_name, message, visibility=MEMBERS_DATA):
        message['user_name'] = self.token.get('cn')

        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].save(message)

        if visibility == PUBLIC_DATA:
            self.c["public"]["collection_name"].save(message)

        if '_id' in message:
            del message['_id']

        self.auditar(message, message['id'], collection_name, 'I')

    def updateRlz(self, collection_name, id, message, visibility=MEMBERS_DATA):
        if message.get('user_name') is None:
            # message['user_name'] = self.token.get('cn')
            raise Exception('No se puede actualizar si el owner no existe')

        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].update({'id': id}, message)

        if visibility == PUBLIC_DATA:
            self.c["public"]["collection_name"].update({'id': id}, message)

        if '_id' in message:
            del message['_id']

        self.auditar(message, id, collection_name, 'U')

    def updateByQuery(self, collection_name, query, message, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].update(query, message)

        if visibility == PUBLIC_DATA:
            self.c["public"]["collection_name"].update(query, message)

    def update_spec(self, flow_id, view, tasks):
        self.schema['spec'].update({"flow_id": flow_id}, {"$set": {"view": view, "tasks": tasks}})

    def remove(self, collection, id, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection].remove({"id": id})

        if visibility == PUBLIC_DATA:
            self.c["public"][collection].remove({"id": id})

        self.auditar(None, id, collection, 'D')

    def clean_collection(self, collection, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection].remove({})

        if visibility == PUBLIC_DATA:
            self.c["public"][collection].remove({})

        self.auditar(None, id, collection, 'D')

    def populate_collection(self, collection, message, visibility=MEMBERS_DATA):
        for m in message:
            self.save(collection, m)

    def remove_spec(self, flow_id):
        self.schema['spec'].remove({"flow_id": flow_id})

    def update(self, collection_name, id, message, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].update({"id": id}, {"$set": {"header": message["header"], "instance": message["instance"]}})
        if visibility == PUBLIC_DATA:
            self.c["public"][collection_name].update({"id": id}, {"$set": {"header": message["header"], "instance": message["instance"]}})

    def update_sub_org_data(self, collection_name, suborganization, data, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].update({"suborganization": suborganization}, {"$set": {"data": data}}, True)
        if visibility == PUBLIC_DATA:
            self.c["public"][collection_name].update({"suborganization": suborganization}, {"$set": {"data": data}}, True)

    def update_by_field(self, collection_name, id, field, message, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].update({"id": id}, {"$set": {field: message}})
        if visibility == PUBLIC_DATA:
            self.c["public"][collection_name].update({"id": id}, {"$set": {field: message}})

    def insert_doc(self, instance_id, doc, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema["instances"].update({"id": instance_id}, {"$push": {"instance.current_task.docs": doc}})
        if visibility == PUBLIC_DATA:
            self.c["public"]["instances"].update({"id": instance_id}, {"$push": {"instance.current_task.docs": doc}})

    def delete_doc(self, instance_id, key, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema["instances"].update({"id": instance_id}, {"$pull": {"instance.current_task.docs": {"key": key}}})
        if visibility == PUBLIC_DATA:
            self.c["public"]["instances"].update({"id": instance_id}, {"$pull": {"instance.current_task.docs": {"key": key}}})

    def update_header(self, collection_name, id, header, visibility=MEMBERS_DATA):
        self.schema[collection_name].update({"id": id}, {"$set": {"header": header}})

    def get_by_id(self, collection_name, id, visibility=MEMBERS_DATA):
        response = self.schema[collection_name].find_one({"id": id})
        if response is None:
            raise Exception("Could not find obj with id " + id + " on collection " + collection_name)
        del response["_id"]
        return response

    def get_by_sub_org(self, collection_name, suborganization, visibility=MEMBERS_DATA):
        response = self.schema[collection_name].find_one({"suborganization": suborganization})
        if response is None:
            return {}
        del response["_id"]
        return response

    # TODO(Eric) refactor this mtf
    def get_by_flow_id(self, collection_name, flow_id):
        response = self.schema[collection_name].find_one({"flow_id": flow_id})
        del response["_id"]
        return response

    def get_by_field(self, collection_name, value, field, visibility=MEMBERS_DATA):
        response = None

        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            response = self.schema[collection_name].find_one({field: value})

        if visibility == PUBLIC_DATA:
            response = self.c["public"][collection_name].find_one({field: value})

        if response is None:
            raise Exception("Could not find obj with id " + id + " on collection " + collection_name)
        del response["_id"]
        return response

    def get_field(self, collection_name, field, value, visibility=MEMBERS_DATA):

        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            response = self.schema[collection_name].find({field: value})

        if visibility == PUBLIC_DATA:
            response = self.c["public"][collection_name].find({field: value})

        if response is None:
            raise Exception("No se encontraron objectos con los parametros deseados")

        return response

    def get_by_query(self, collection_name, query, order_by=None, visibility=MEMBERS_DATA):
        if order_by is None:
            if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
                response = self.schema[collection_name].find(query)
            if visibility == PUBLIC_DATA:
                response = self.c["public"][collection_name].find(query)
        else:
            if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
                response = self.schema[collection_name].find(query).sort(order_by, 1)
            if visibility == PUBLIC_DATA:
                response = self.c["public"][collection_name].find(query).sort(order_by, 1)

        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        return list

    def get_query_and_fields(self, collection_name, query, fields={}, order_by=None, visibility=MEMBERS_DATA):
        if order_by is None:
            if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
                response = self.schema[collection_name].find(query, fields)
            if visibility == PUBLIC_DATA:
                response = self.c["public"][collection_name].find(query, fields)
        else:
            if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
                response = self.schema[collection_name].find(query, fields).sort(order_by, 1)
            if visibility == PUBLIC_DATA:
                response = self.c["public"][collection_name].find(query, fields).sort(order_by, 1)

        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        return list

    def get_page_by_query(self, collection_name, query, sortingInfo, page, limit, visibility=MEMBERS_DATA):
        skip = (page - 1) * limit
        if sortingInfo == '':
            if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
                response = self.schema[collection_name].find(query).sort("instance.created_on", -1).skip(skip).limit(limit)
            if visibility == PUBLIC_DATA:
                response = self.c["public"][collection_name].find(query).sort("instance.created_on", -1).skip(skip).limit(limit)
        else:
            if sortingInfo[:1] == "+":
                order = 1
            else:
                order = -1
            order_by = sortingInfo[1:]
            if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
                response = self.schema[collection_name].find(query).sort(order_by, order).skip(skip).limit(limit)

            if visibility == PUBLIC_DATA:
                response = self.c["public"][collection_name].find(query).sort(order_by, order).skip(skip).limit(limit)
        # Delete ID
        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        return list

    def count(self, collection_name, query, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            return self.schema[collection_name].find(query).count()
        if visibility == PUBLIC_DATA:
            return self.c["public"][collection_name].find(query).count()

    def get_id_list(self, collection_name, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            response = self.schema[collection_name].find()
        if visibility == PUBLIC_DATA:
            response = self.c["public"][collection_name].find()
        ids = []
        for obj in response:
            ids.append(obj['id'])
        return ids

    # TODO(Eric) Refactor this
    def get_specs(self):
        response = self.schema["spec"].find().sort("flow_description", 1)
        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        obj_list = []
        for component in list:
            new_list = {}
            new_list['text'] = component['flow_description']
            new_list['id'] = component['flow_id']
            new_list['idPadre'] = "0"
            new_list['service_id'] = "specs"
            obj_list.append(new_list)
        return obj_list

    def get_all_specs(self):
        response = self.schema["spec"].find().sort("flow_description", 1)
        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        return list

    # TODO(Eric) Refactor this
    def get_templates(self, key, filter):
        response = self.schema["instances"].find({"header.is_template": "true"}).sort("header.name", 1)
        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        obj_list = []
        for component in list:
            new_list = {}
            new_list['text'] = component['header']['name']
            new_list['id'] = component['id']
            new_list['idPadre'] = "0"
            new_list['service_id'] = "templates"
            obj_list.append(new_list)
        return obj_list

    def get_by_field(self, collection_name, field, id, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            response = self.schema[collection_name].find({field: id})
        if visibility == PUBLIC_DATA:
            response = self.c["public"][collection_name].find({field: id})
        list = []
        for r in response:
            del r["_id"]
            list.append(r)
        return list

    def insert(self, collection_name, array_name, message, visibility=MEMBERS_DATA):
        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            self.schema[collection_name].update({"header": {"name": "Eventos"}}, {"$push": {array_name: message}})
        if visibility == PUBLIC_DATA:
            self.c["public"][collection_name].update({"header": {"name": "Eventos"}}, {"$push": {array_name: message}})

    def getLastVersion(self, collection_name, query={}, visibility=MEMBERS_DATA):

        sort = {'$sort': {'version': -1}}
        group = {'$group': {'_id': '$name', 'doc': {'$first': '$$ROOT'}}}
        match = {'$match': query}  # RIGHT

        pipe = [sort, group, match]

        if visibility == MEMBERS_DATA or visibility == PRIVATE_DATA:
            resp = self.schema[collection_name].aggregate(pipe)

        if visibility == PUBLIC_DATA:
            resp = self.c['public'][collection_name].aggregate(pipe)

        response = []
        for r in resp:
            doc = r['doc']
            del doc["_id"]
            response.append(doc)
        return response

    def auditar(self, message, id, collection_name, tp='I'):

        # Audit Code
        sys.path.append(current_app.config["APP_PATH"] + "/src/services")
        audit_mod = __import__("auditorias")

        audit_mod.save(message, self.token, id, collection_name, tp)

    def test(self):
        pass


def get_instance(id):
    return Repository(id)
