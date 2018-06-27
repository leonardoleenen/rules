from flask import Blueprint, Flask, current_app, jsonify, render_template, request, url_for, redirect, flash, session
from flask_cors import cross_origin
import base64
import json
from utils import repo
from utils.toolbox import BussinessException
import os
import httplib2 as http


DOMAIN_HEADER = """
import json
from intellect.Intellect import Callable
"""


def create_scenario(message):

    '''
    Create a New Scenario given a JSON message (like this)

    {
        "name" : "Escenario de prueba",
        "owner" : "dev_user",
        "preload_plugin" : null,
        "catalogs":[{
                "service_id" : "catalog",
                "idPadre" : 0,
                "id" : "Asigancion directa de canal",
                "text" : "Asigancion directa de canal de importacion"
            }]
    }
    '''

    new_scenario={"name":message["name"],
                        "owner":message["owner"],
                        "forms":[],
                        "preload_plugin":message["preload_plugin"],
                        "catalogs":message["catalogs"]}


    entities=[]

    for c_id in message["catalogs"]:
       
        entities += [x for x in get_domain_by_catalog_name(c_id["id"])["domain"] if x not in entities]

    new_scenario["domain"]=entities 


    repo_client = repo.get_instance("rules")
    id_scenario=repo_client.save("scenarios",new_scenario)
 
    return id_scenario



def get_scenario_by_id(id):
    repo_client = repo.get_instance("rules")
    return repo_client.get_by_id("scenarios",id)



def remove_domain(id_domain):
    repo_client = repo.get_instance("rules")
    repo_client.remove("domain_classes", id_domain) 

def save_domain(class_spec):

    '''
    
    Save a all domain clases (not an individual classes)

    @param: we spect something like this: 

    {
      "header": {},
      "instance": {
        "name": "Dui",
        "description": "Declaracion Unica de Importacion",
        "package": "bo.aduana.importacion.selectividad",
        "properties": [
          {
            "name": "razon_social",
            "data_type": "string",
            "collection": false,
            "visibility": "public"
          },
          {
            "name": "nit",
            "data_type": "string",
            "collection": false,
            "visibility": "public"
          },
          {
            "name": "hijos",
            "data_type": "Persona",
            "collection": false,
            "visibility": "public"
          }
        ]
      }
    }  
    '''




    repo_client = repo.get_instance("rules")
    

    if class_spec.get("id") is None:
        '''Asume is an update '''
       
        if len(repo_client.get_by_query("domain_classes",{"instance.name":class_spec["instance"]["name"]})) !=0:
            raise BussinessException("Lo sentimos pero el nombre de clase que intenta ingresar ya existe.")

        message={}
        message["id"]=repo_client.save("domain_classes",class_spec)
        return message
    else:

        repo_client.update("domain_classes",class_spec["id"],class_spec)

    '''

    domain=get_domain()
    
    str_domain=  "import json \nfrom intellect.Intellect import Callable\n"  

    for entity in domain: 
        str_domain +=transform_json_to_class(entity["instance"])

    entity = open(current_app.config["RULE_STORAGE"] + os.sep + "domain.py","w")
    entity.write(str_domain)
    '''

def get_domain():
    repo_client = repo.get_instance("rules")
    return repo_client.get_by_query("domain_classes",{})

def import_bulk_domain(message):
    repo_client = repo.get_instance("rules")
    repo_client.clean_collection("domain_classes")
    repo_client.populate_collection("domain_classes",message)

def get_domain_by_catalog_name(catalog_name):
    repo_client = repo.get_instance("rules")
    catalog=repo_client.get_by_query("rule_spec",{"instance.name":catalog_name})


    domain=[]
   
    
    for entity in catalog[0]["instance"]["entities"]:

        result=repo_client.get_by_query("domain_classes",{"instance.name":entity["id"]})
        domain.append(result[0]["instance"])

    message={"domain":domain}
  
    return message

def get_rule_by_catalog_name(catalog_name,order):
    repo_client = repo.get_instance("rules")
    catalog=repo_client.get_by_query("rule_spec",{"instance.name":catalog_name})


 
    str_rule=""

    for rule in catalog[0]["instance"]["rules"]:
        halt=""
        if rule["halt"]:
            halt="kcontext.halt();"
  
        str_rule = str_rule +  ''' 
rule \"{0}\"
    no-loop true
    dialect "mvel" 
    salience {4}
    when
        {1}
    then 
        {2}
        {3}
    end
'''.format(rule["name"],base64.b64decode(rule["condition"]),base64.b64decode(rule["action"]),halt,order)

    return str_rule





def save_static_list(list_spec):
    repo_client = repo.get_instance("rules")

    if list_spec.get("id") is None: 

        if len(repo_client.get_by_query("static_list",{"instance.name":list_spec["instance"]["name"]})) !=0:
            raise BussinessException("Lo sentimos pero el nombre de lista que intenta ingresar ya existe.")


        message={}
        message["id"]=repo_client.save("static_list",list_spec)
        return message 
    else:
        repo_client.update("static_list",list_spec["id"],list_spec)

def get_statics_list():
    '''
        Return a json list of static_list 
        
        Args:
            None
        '''
    repo_client = repo.get_instance("rules")
    return repo_client.get_by_query("static_list",{})

def remove_static_list(id):
    repo_client = repo.get_instance("rules")
    repo_client.remove("static_list", id) 

def import_bulk_static_list(message):
    repo_client = repo.get_instance("rules")
    repo_client.clean_collection("static_list")
    repo_client.populate_collection("static_list",message)


def get_data_types(): 
    data_types=["date","string","integer","currency"]

    domain=get_domain()

    for d in domain:
        data_types.append(d["instance"]["name"])

    return data_types














def save_rule_spec(rule_spec):


    '''

    @param Except a JSON message like this 

    {
      "header": {},
      "instance": {
        "name": "Asigancion directa de canal",
        "package": "bo.aduana.importacion.selectividad",
        "descripcion": "Regla de Asignacion directa de canal",
        "entities": [
          {
            "service_id": "domain_classes",
            "idPadre": 0,
            "id": "Dui",
            "text": "Declaracion Unica de Importacion"
          }
        ],
        "list": [
          {
            "service_id": "static_list",
            "idPadre": 0,
            "id": "PAISES_RIESGO_BAJO",
            "text": "PAISES_RIESGO_BAJO"
          }
        ],
        "rules": [
          {
            "name": "Pais de Procedencia ",
            "condition": "as234gfvdf234y2434523rq3453413r232535",
            "action": "13sdf234233453rfwefwe345r34efwef23453",
            "halt": true,
            "message": "Un mensaje de salida"
          },
          {
            "name": "Pais de Origen ",
            "condition": "as234gfvdf234y2434523rq3453413r232535",
            "action": "13sdf234233453rfwefwe345r34efwef23453",
            "halt": true,
            "message": "Un mensaje de salida para pais de Origen"
          }
        ]
      }
    }

    '''

    repo_client = repo.get_instance("rules")

    if rule_spec.get("id") is None: 

        if len(repo_client.get_by_query("rule_spec",{"instance.name":rule_spec["instance"]["name"]})) !=0:
            raise BussinessException("Lo sentimos pero el nombre de la regla  que intenta ingresar ya existe.")


        message={}
        
        message["id"]=repo_client.save("rule_spec",rule_spec)

        '''
        cat_temp={"id": rule_spec["instance"]["name"]}
        catalogs=[]
        catalogs.append(cat_temp)

        new_scenario={"name":rule_spec["instance"]["name"],"owner":"undefined","forms":[],"preload_plugin":None, "catalogs":catalogs}
        id_scenario= create_scenario(new_scenario)

        
        rule_spec["scenario_id"]=id_scenario
        '''

        return message 
    else:

        repo_client.update("rule_spec",rule_spec["id"],rule_spec)

def get_rule_spec_by_name(name):
    repo_client = repo.get_instance("rules")
    value=repo_client.get_by_query("rule_spec",{"instance.name":name})[0]

    return value
def get_rules_spec():
    repo_client = repo.get_instance("rules")
    return repo_client.get_by_query("rule_spec",{})

def remove_rule_spec(id):
    repo_client = repo.get_instance("rules")
    rs=repo_client.get_by_id("rule_spec",id)

    repo_client.remove("rule_spec", id) 

def import_bulk_rule_spec(message):
    repo_client = repo.get_instance("rules")
    repo_client.clean_collection("rule_spec")
    repo_client.populate_collection("rule_spec",message)




def update_intance_form(message): 

    try:
        repo_client = repo.get_instance("rules")
        sc=repo_client.get_by_id("scenarios",message["scenario_id"])

        cont=0
        finded=False
        for form in sc["forms"]:
            if form["instance_id"]==message["form"]["instance_id"]:
                form["data"]=message["form"]["data"]
                finded=True
                break
            cont+=1

        if finded:
            sc["forms"][cont]=form

        repo_client.update_by_field("scenarios",message["scenario_id"],"forms",sc["forms"])

        return jsonify(success=True,msg="La operacion se ha realizado con exito")

    except Exception, ex:
        current_app.logger.exception(ex)
        return jsonify(success=False,msg="Lo sentimos pero ha ocurrido un error en el sistema"),500

def save_catalog(message):
    '''
    {
      "catalog_id":"PING",
      "catalog_name":"Regla de Testing Unitario",
        "domain":[
            {

              "class":"Ping",
              "native_properties": ["codigo","descripcion"]
            },

            {

              "class":"Ping2",
              "natie_properties": ["codigo","descripcion"]
            }
        ],
        "rules":"CmZyb20gcGluZ19kb21haW4gaW1wb3J0IFBpbmcKZnJvbSBwaW5nX2RvbWFpbiBpbXBvcnQgUGluZzIKCnJ1bGUgIlRlc3QiOgogICAgd2hlbjoKICAgICAgICAkcDo9UGluZyhjb2RpZ28gPT0yKQogICAgdGhlbjoKICAgICAgICBwcmludCAiU2UgZWplY3V0byBjb3JyZWN0YW1lbnRlIGxhIHJlZ2xhIgogICAgICAgICRwLm1lc3NhZ2VzLmFwcGVuZCh7ImxhYmVsIjoiSU5GTyIsImRlc2NyaXB0aW9uIjoiVW5hIG11ZXN0cmEifSkKICAgICAgICBtb2RpZnkgJHA6CiAgICAgICAgICAgIG1lc3NhZ2VzPSRwLm1lc3NhZ2VzCg=="
    }
    '''

    domain = DOMAIN_HEADER
    domain_module = message["catalog_id"].lower() + "_domain"
    domain_file = message["catalog_id"].lower() + "_domain.py"
    rule_dinamic_import_class = ""

    for m in message["domain"]:
    	rule_dinamic_import_class += "from {0} import {1}".format(domain_module, m["class"] + "\n")
    	domain += transform_json_to_class(m)

    file = open(current_app.config[ "RULE_STORAGE"] + os.sep + message["catalog_id"].lower() + "_domain.py", "w")
    file.write( domain)
    file.close()

    rule = base64.b64decode(message["rules"])
    file = open(current_app.config[ "RULE_STORAGE"] + os.sep + message["catalog_id"].lower() + ".policy", "w")
    file.write(rule_dinamic_import_class +rule)
    file.close()

    file = open(current_app.config[ "RULE_STORAGE"] + os.sep + message["catalog_id"].lower() + ".meta", "w")
    file.write(json.dumps(message))
    file.close()


def transform_json_to_class(message):



    
    native_properties=""
    list_properties=""
    private_properties=""


    rule="""
class {0}(object): 
    def __init__(self,message):
    	self.__dict__ = message
	
    def to_JSON(self):
        str_json=json.dumps(self, default=lambda o: o.__dict__,sort_keys=True,indent=4)
    	return json.loads(str_json)

    _messages=[]

    @property 
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self,value):
        self._messages=value

    @Callable
    def addMessage(self,message):
        self._messages.append(message)
        return self._messages

    _new_message=[]

    @property 
    def new_message(self):
        return self._new_message

    @new_message.setter
    def new_message(self,value):
        self._new_message=value
        self._messages.append(value)

""".format(message["class"])


    properties=""

    for property in message["native_properties"]:
        native_properties+="""
    {0}=None

    @property
    def {1}(self):
	    return self.{0}

    @{1}.setter
    def {1}(self,value):
	    self.{0}=value
""".format("_" + property,property)

    for property in message["hidden_properties"]:
        native_properties+="""
    {0}=None

    @property
    def {1}(self):
        return self.{0}

    @{1}.setter
    def {1}(self,value):
        self.{0}=value
""".format("_" + property,property)




	if message.get("list_properties") is not None:  
		for property in message["list_properties"]:
			list_properties+="""
    {0}=[]

    @property
    def {1}(self):
        return self.{0}

    @{1}.setter
    def {1}(self,value):
        self.{0}=value

    @Callable
    def cantidad_{1}(self):
        return len(self.{0})
    """.format("_" + property['property_cod'],property['property_cod']) 

     
    if message.get("private_properties") is not None: 
        for property in message["private_properties"]:
            private_properties+="""
            {0}=None
            """.format(property)
    
   
    return rule + "{0} \n {1} \n {2}".format(native_properties,list_properties,private_properties)  


def get_scenarios(): 
    repo_client = repo.get_instance("rules")
    return repo_client.get_by_query("scenarios",{})


def get_rules_by_catalogs(catalogs):
    full_rule="" 

    salience=len(catalogs) * 100

    for catalog in catalogs:
        full_rule+=  "\n" + get_rule_by_catalog_name(catalog,salience)
        salience=salience -100

    return full_rule

def wrap_entities(entities): 

    
    if current_app.config["RULE_DIALECT"].strip()=='intellect':
        return wrap_intellect_entities(entities)

    if current_app.config["RULE_DIALECT"].strip()=='mvel':
        return wrap_drools_entities(entities)


def wrap_intellect_entities(entities):
    entity_imports=""

    for entity in entities: 
            entity_imports +="from domain import {0} \n". format(entity["name"])

    return entity_imports

def wrap_drools_constants(static_list):
    #current_app.logger.debug(static_list)
    
    query_array=[]
    for sl in static_list: 
        query_array.append(sl["id"])
    
    
    repo_client = repo.get_instance("rules")
    result_list=repo_client.get_by_query("static_list",{"instance.name":{"$in":query_array}})
    
    list_literal=""
    for sl in result_list:
        value_literal=""
        for value in sl["instance"]["values"]:
            value_literal+=",\"{0}\"".format(value)
    
        
        list_literal+=sl["instance"]["name"] + " : String[] =  new String[]{" + value_literal[1:] + "}\n"

    
    
    return list_literal 

def wrap_drools_entities(entities):
    full_text=''

    for entity in entities:
        entity_spec='''\n
    declare {0}
    @typesafe(false)
        '''.format(entity["name"])

        for prop in entity["properties"]: 
            if prop["visibility"]["id"]=="private": 
                entity_spec=entity_spec + "\thidden_{0} : Object\n".format(prop["name"])
            
            if prop["visibility"]["id"]=="public":
                entity_spec=entity_spec + "\t{0} : Object\n".format(prop["name"])

            
        entity_spec= entity_spec + '''

    form_name : Object
        '''

        entity_spec= entity_spec + "hidden_messages : ArrayList = new ArrayList()\nend\n"



    return full_text + entity_spec + ''' \n
    rule "Add Contstants "
        no-loop true
        salience 100000
        dialect "mvel"
    
        when
            not Constant()
        then
            insert (new Constant());
    end

    '''

def remote_test(message):
    
    '''
    Call remote server and send rules, facts and Domain for Test rule. 
    '''


    #current_app.logger.debug("Realizando la conexion con: {0} Enviando Mensaje: {1}".format(current_app.config["RULE_SERVER_TEST"],message))
    try:
        method = 'POST'
        h = http.Http(disable_ssl_certificate_validation=True)
        response, content = h.request(current_app.config["RULE_SERVER_TEST"], "POST",json.dumps(message),{'Content-Type': 'application/json; charset=UTF-8'})
        
        msg_response=json.loads(content)
        if msg_response.get("success") is not None and msg_response["success"]==False:
            current_app.logger.error(msg_response)
            raise Exception("Ha ocurrido un error al procesar el pedido de testeo de regla")


        return  json.loads(content)['result']   
    except Exception,ex: 
        current_app.logger.exception(ex)
        raise Exception("Lo sentimos pero no podemos conectarnos al servicio de testing de reglas")

    
    



