from flask import current_app
import json
import httplib2 as http
from bson.json_util import dumps
import redis

'''
Returns the user data corresponding to the given session token. Calls to Hera user service
@author: Eric X. Engstfeld
'''


def get_user_data_by_token(token, organization, attrs, suborg=""):
    current_app.logger.debug("Getting user data on Hera...")
    hera_url = current_app.config["LOAD_USER_DATA_URL"]
    http_client = http.Http(disable_ssl_certificate_validation=True)
    hera_response, hera_content = http_client.request(hera_url, 'POST', dumps({"organization": organization, "token": token, "attrs": attrs, "retrieve_roles": True, "suborganization": suborg}), {'Content-Type': 'application/json; charset=UTF-8'})
    current_app.logger.debug("Hera response content is " + str(hera_content))
    current_app.logger.debug("Hera reponse is: " + str(hera_response))
    if hera_response["status"] != '200':
        raise Exception("Problem with Hera communication. Maybe an invalid token was given")
    return json.loads(hera_content)


def get_user_data_on_redis(token):
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	data = json.loads(r.get(token))
	return data
