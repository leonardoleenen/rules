NoAutors: German Leotta, Facundo Caselles, Enzo D. Grosso
<br>Date: 20 de Diciembre de 2016

# Indice
1. [ARG APP](#about)
2. [Como instalar](#id-how-to-install)
	* [Requisitos Previos](#id-req-prev)
	* [Archivo arg-properties.cfg](#id-arch-conf)
	* [Instalar en Desarrollo](#id-inst-des)
	* [Instalar en Produccion](#id-inst-prod)
3. [Instalar en ANSES](#id-inst-anses)
4. [Servicios](#id-services)

	* [Funciones](#id-abms-functions)
	* [Entidades](#id-abms-entitys)
	* [Listas](#id-abms-lists)
	* [Reglas](#id-abms-rules)
	* [Tablas](#id-abms-tables)
	* [Dominios](#id-abms-domains)
	* [Escenarios](#id-abms-stage)
	* [Seguridad](#id-service-security)


<div id='about'/>
# 1. ARG APP
ARG APP (tambien conocida como ARG) es un aplicativo pensado para la confección de reglas de nogocio.
El mismo esta compuesto por una interfaz web desarrollada con "angular" y una interfaz de servicios REST desarrollada en "python" (v2.7) utilizando el framework [FLASK](http://flask.pocoo.org/).

<div id='id-how-to-install'/>
# 2. Como Instalar

<div id='id-req-prev'/>
## 2.1 Requisitos previos:

	- Python 2.7
	- [MongoDB](#id-214)
	- [Python DEV TOOLS](#id-212)
	- [PyPA](#id-213)
	- [REDIS SERVER](#id-215)


<div id='id-214'/>
### Instalar MongoDB

** En Debian/Ubuntu **

* Importar la clave publica

	```sh
	$ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
	```

* Crear la lista de archivos de MongoDB

	```sh
	$ echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
	```

* Actualizar los paquetes

	```sh
	$ sudo apt-get update
	```

* Instalar los paquetes de MongoDB

	```sh
	$ sudo apt-get install -y mongodb-org
	```

** En Centos/fedora/rhel **

* Crear el archivo /etc/yum.repos.d/mongodb.repo

	```sh
	$ vi /etc/yum.repos.d/mongodb.repo
	```

    ```sh
	[mongodb]
	name=MongoDB Repository
	baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/
	gpgcheck=0
	enabled=1
	```

* Instalar los paquetes de MongoDB

	```sh
	$ sudo yum install -y mongodb-org
	```


<div id='id-212'/>
### Instalar python-dev

** En Debian/Ubuntu **

```sh
$ sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
```

** En Centos/fedora/rhel **

```sh
$ sudo yum install python-devel openldap-devel cyrus-sasl-devel libopenssl-devel
```


<div id='id-213'/>
### Instalar PyPA

```sh
$ sudo apt-get install python-pip
```


<div id='id-215'/>
### Instalar Redis-Server

** En Debian/Ubuntu **

```sh
$ sudo apt-get install redis-server
```

** En Centos/fedora/rhel **

* Instalar EPEL Repo

	```sh
	wget -r --no-parent -A 'epel-release-*.rpm' http://dl.fedoraproject.org/pub/epel/7/x86_64/e/

	rpm -Uvh dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-*.rpm
	```

* Instalar server

	```sh
	$ yum install redis
	```




<div id='id-arch-conf'/>
## 2.2 Archivo luzia-rlz.cfg

	#Tech Configuration

	ARG_RULZ_PORT=5000
	DEBUG_MODE=True

	#PATH a donde se encuentran los archivos de la app

	APP_PATH='/home/enzo/TRABAJO/luzia-rlz/git'

	#Rule Server

	RULE_DIALECT="mvel"
	RULE_SERVER="http://104.131.195.229:8080"
	RULE_SERVER_VALIDATE="/selectividad/rest/rule_engine/drl/validate"
	RULE_SERVER_TEST="/selectividad/rest/rule_engine/execute/approval"
	RULE_SERVER_INSTALL="/selectividad/rest/rule_engine/execute/install"
	RULE_SERVER_UNISTALL="/selectividad/rest/rule_engine/execute/uninstall"
	RULE_SERVER_LIST="/selectividad/rest/rule_engine/execute/list"
	RULE_SERVER_IS_ALIVE="/rest/rule_engine/test"
	RULE_STORAGE="/home/enzo/TRABAJO/deploy/rule_storage"

	#Configuración de conexion con MongoDB
	MONGO_HOST="localhost"
	MONGO_PORT=27017

	PLUGINS_PATH="/home/enzo/TRABAJO/deploy/plugins"

	TMP_FOLDER='/home/enzo/TRABAJO/deploy/tmp'

	#Path a donde se almacenan archivos adjuntos (.txt,.jpg,.pdf,etc)

	FILE_STORAGE_BUCKET_PATH="/home/enzo/TRABAJO/deploy/storage/bucket"
	FILE_STORAGE_SIGNED_FILES_PATH="/home/enzo/TRABAJO/deploy/storage/signed"

	FIXED_EVENTS_URL=""

	#[ROLES]
	MODULE_TEMPLATE_PUBLICATION="ONC, Administrador"
	MODULE_TEMPLATE_CONSUMPTION="Operador,Publicador,Administrador"
	MODULE_CALENDAR="Operador,Publicador,Administrador,ONC"
	MODULE_RULES="Administrador"
	MODULE_ADMINISTRATION="Administrador"

	#[INTERNATIONALIZATION]
	i18n="es"

	#[DEV MODE]
	DEV_ORGANIZATION="ARG Anses"
	DEV_MODE=True
	FILTER_BY_ROLES=True

	LOAD_USER_DATA_URL="http://localhost:5000/security/user/get_roles"
	FETCH_SUBORGS_URL="http://localhost:5000/security/get_organizations"
	LOGOUT_URL=""
	FIXED_EVENTS_URL=""
	LOGO_SRC="src/img/aduana_logo.png"

	USER_PROFILES_MODULES_MATRIX=[("BTN_PUBLICAR_ESCENARIO",["ADMINISTRADOR","EDITOR","PUBLICADOR"]),("TEMPLATE_PUBLICATION",["ADMINISTRADOR", "ONC"]), ("TEMPLATE_CONSUMPTION",["ADMINISTRADOR","EDITOR","PUBLICADOR"]), ("CALENDAR",["ONC","Publicador","Operador","ADMINISTRADOR"]), ("RULES",["ADMINISTRADOR"]), ("ADMINISTRATION",["ADMINISTRADOR"])]

	ROLESxMODULES_MATRIX_SERVICE="/security/rxf/matrix"



<div id='id-inst-des'/>
## 2.3 Instalar en Desarrollo

* Instalar virtualenv

	```sh
	$ sudo pip install --upgrade virtualenv
	```

* Crear un ambiente virtual para la aplicación

	```sh
	$ virtualenv mi_virtual_env
	```

* Iniciar virtualenv

	```sh
	$ source mi_virtual_env/bin/activate
	```

* Instalar los pquetes necesarios

	```sh
	$ python setup.py [develop|install]
	```

* Instalar la aplicación y seguir todos los pasos para generar el [archivo de configuración](#id-arch-conf) de Luzia Rulz

	```sh
	$ python install.py [develop|install]
	```

* Importamos la variable ARG_SETTINGS (condición necesaria y excluyente para ejecutar la aplicación)

	```sh
	$ export ARG_SETTINGS=path-absoluto-a-carpeta-de-instalacion/conf/luzia-rlz.cfg
	```

* Iniciamos la aplicaicón desde la carpeta src

	```sh
	$ python initserver.py
	```

* Si se desea iniciar la aplicación en segundo plano (recuperar control de terminal) usar "nohup"

	```sh
	$ nohup python initserver.py &
	```

<div id='id-inst-prod'/>
## 2.4 Instalar en Produccion

### 2.4.1 Instalar apache y el modulo WSGI

* Ubuntu/Debian *

	```sh
	$ sudo apt-get install apache2 libapache2-mod-wsgi
	```

* CentOS/Fedora *

	```sh
	$ sudo yum install httpd mod_wsgi
	```

### 2.4.2 Instalar aplicación

* Crear un ambiente virtual para la aplicación

	```sh
	$ virtualenv mi_virtual_env
	```

* Iniciar virtualenv

	```sh
	$ source mi_virtual_env/bin/activate
	```

* Instalar los pquetes necesarios

	```sh
	$ python setup.py [develop|install]
	```

* Instalar la aplicación y seguir todos los pasos para generar el [archivo de configuración](#id-arch-conf) de Luzia Rulz

	```sh
	$ python install.py [develop|install]
	```

### 2.4.3 Crear archivo app.wsgi y domain.conf

* Desde la carpeta raiz del proyecto utilizamos el script "create_wsgi.py"

	```sh
	$ python create_wsgi.py
	```

* Seguir los pasos para genererar app.wsgi:

	```py
	import sys
	import os
	import site
	from os import environ, getcwd
	import logging, sys

	sys.path.append('/var/www/luzia-rulz/src')
	os.environ['PYTHON_EGG_CACHE']="/var/www/luzia-rulz/luzia_rlz.egg-info"
	os.environ['ARG_SETTINGS']="/var/www/luzia-rulz/deployment/conf/luzia-rlz.cfg"
	site.addsitedir('/var/www/.local/lib/python2.7/site-packages')

	from initserver import app as application
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

	LOG = logging.getLogger(__name__)
	LOG.debug('Current path: {0}'.format(getcwd()))

	# Application config
	application.debug = True

	with application.app_context():
	        pass
	```

* Ademas se generara el archivo domain.conf siendo domain el nombre del dominio que nosotros elegimos:

	```conf
	 <VirtualHost *:80>
        ServerName luzia.site.com

        <Directory /var/www/luzia-rulz>
            Require all granted
            Options +FollowSymLinks -Indexes
        </Directory>


        <Directory "/var/www/luzia-rulz/deployment">
            Options -Indexes +FollowSymLinks
            AllowOverride All
            Require all granted
        </Directory>

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel debug

        WSGIDaemonProcess luzia-rulz user=www-data group=www-data threads=5
        WSGIScriptAlias / /var/www/luzia-rulz/deployment/wsgi/app.wsgi
        WSGIPassAuthorization On

        ErrorLog ${APACHE_LOG_DIR}/error-127.0.0.1.log
        CustomLog ${APACHE_LOG_DIR}/access-127.0.0.1.log combined
    </VirtualHost>
	```


<div id="id-inst-anses"/>
3. Instalar en ANSES

* [Componenete Gateway](https://github.com/LuziaSol/LuziaRules/tree/alpha/src/etc/gateway.pdf)

* [Componente SOAP-SERVER](https://github.com/LuziaSol/LuziaRules/tree/alpha/src/etc/soap_server.pdf)





<div id='id-services'/>
# 4. Servicios

A continuación se describen los servicios utilizados por el sistema, todos aquellos valores que son "variables" se escriben entre "&lt;" y "&gt;"

<div id='id-abms-functions'/>
## 4.1 Funciones

* Obtener todas las funciones definidas en el sistema:

	```
	Servicio: rulz/function/all

	METHOD: GET
	```

* Guardar y Actualizar una nueva función:

	```
	Servicio: rulz/function

	METHOD: POST
	```
	```json
	DATA: {"name": "suma", "body": "return primer + segundo;", "params": [{"type": "Integer", "name": "primer"},{"type": "Integer", "name": "segundo"}], "returnType": "Integer", "id": "148be5f2-4065-11e5-ab76-c417fef93ab4"}
	```

* Obtener una función a travez de su id

	```
	Servicio: rulz/function/<id>

	METHOD: GET
	```

* Remover una función del sistema a partir de su id

	```
	Servicio: rulz/function/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}
	```

* Verificar sintaxis y declaración de la función

	```
	Servicio: rulz/function/test

	METHOD: POST
	```
	```json
	DATA: {"name": "suma", "body": "return primer + segundo;", "params": [{"type": "Integer", "name": "primer"},{"type": "Integer", "name": "segundo"}], "returnType": "Integer", "id": "148be5f2-4065-11e5-ab76-c417fef93ab4"}
	```


<div id='id-abms-entitys'/>
## 4.2 Entidades

* Obtener todas las entidades definidas en el sistema:

	```
	Servicio: rulz/entity/all

	METHOD: GET
	```

* Guardar y aActualizar una nueva entidad:

	```
	Servicio: rulz/entity

	METHOD: POST
	```
	```json
	DATA: {"name":"Persona", "schema":{"adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"dni":{"readableType":"numero entero","adding":false,"type":"integer"}},"tempName":""},"description":"","plainAttr":[{"name":"this","type":"object"},{"name":"dni","type":"integer"}],"id":"cfdc97aa-4fda-11e5-81cb-c417fef93ab4"}
	```

* Obtener una entidad a travez de su id

	```
	Servicio: rulz/entity/<i>

	METHOD: GET
	```

* Remover una entidad a partir de su id

	```
	Servicio: rulz/entity/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}
	```

* Chequear si un atributo de la entidad se encuentra en uso

	```
	Servicio: rulz/check/entity/attribute

	METHOD: POST
	```
	```json
	DATA: {"entity":{"id":"cfdc97aa-4fda-11e5-81cb-c417fef93ab4","name":"Persona"},"attr":"dni"}
	```


<div id='id-abms-lists'/>
## 4.3 Listas

* Obtener todas las listas de valores definidas en el sistema:

	```
	Servicio: rulz/list/all

	METHOD: GET
	```

* Guardar y Actualizar una nueva lista de valores:

	```
	Servicio: rulz/list

	METHOD: POST
	```
	```json
	DATA: {"name": "masculino", "description": "", "id": "113d7568-4066-11e5-ab76-c417fef93ab4", "elements": [{"type": "string", "value": "m"}, {"type": "string", "value": "M"}, {"type": "string", "value": "masculino"}, {"type": "string", "value": "hombre"}]}
	```

* Obtener una lista de valores a travez de su id

	```
	Servicio: rulz/list/<id>

	METHOD: GET
	```

* Remover una lista de valores del sistema a partir de su id

	```
	Servicio: rulz/list/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}
	```

<div id='id-abms-rules'/>
## 4.4 Reglas

* Obtener todas las reglas definidas en el sistema:

	```
	Servicio: rulz/rule/all

	METHOD: GET
	```

* Guardar y Actualizar una nueva regla:

	```
	Servicio: rulz/rule

	METHOD: POST
	```
	```json
	DATA: {"name":"ReglaDeTest","actions":[],"rules":[{"type":"NuevaPersona","conds":[{"attr":{"name":"documento.nro_documento","type":"integer"},"value":"34917399","operator":"==","binding":"","used":false,"connector":"&&"},{"attr":{"name":"documento.nro_documento","type":"integer"},"value":"null","operator":"==","binding":"","used":false,"connector":"&&","funct":{"fields":[{"type":"Integer","name":"5","at":"primer"},{"type":"Integer","name":"8","at":"segundo"}],"type":"Integer","name":"suma"}}],"binding":"","connector":"AND"}],"cep":false,"types":["4afd5f28-40ea-11e5-ab76-c417fef93ab4"],"rule":null,"bindings":"{}","bindingRules":{},"id":"ccb82d38-4129-11e5-ab76-c417fef93ab4","active":true,"published":false,"limited":false,"catalog":{"id":"2500725e-40f1-11e5-ab76-c417fef93ab4","name":"Persona con BeneficioCat"},"atomic":false,"enabled":true}
	```

* Obtener una regla a travez de su id

	```
	Servicio: rulz/rule/<id>

	METHOD: GET
	```

* Remover una regla del sistema a partir de su id

	```
	Servicio: rulz/rule/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}
	```

* Obtener reglas que no se encuentren asociadas a un dominio

	```
	Servicio: rulz/rule/notincatalog

	METHOD: GET
	```

* Obtener el DRL generado a partir de la regla

	```
	Servicio: rulz/drl/rule

	METHOD: POST
	```
	```json
	DATA: {"name":"ReglaDeTest","actions":[],"rules":[{"type":"NuevaPersona","conds":[{"attr":{"name":"documento.nro_documento","type":"integer"},"value":"34917399","operator":"==","binding":"","used":false,"connector":"&&"},{"attr":{"name":"documento.nro_documento","type":"integer"},"value":"null","operator":"==","binding":"","used":false,"connector":"&&","funct":{"fields":[{"type":"Integer","name":"5","at":"primer"},{"type":"Integer","name":"8","at":"segundo"}],"type":"Integer","name":"suma"}}],"binding":"","connector":"AND"}],"cep":false,"types":["4afd5f28-40ea-11e5-ab76-c417fef93ab4"],"rule":null,"bindings":"{}","bindingRules":{},"id":"ccb82d38-4129-11e5-ab76-c417fef93ab4","active":true,"published":false,"limited":false,"catalog":{"id":"2500725e-40f1-11e5-ab76-c417fef93ab4","name":"Persona con BeneficioCat"},"atomic":false,"enabled":true}
	```


<div id='id-abms-tables'/>
## 4.5 Tablas

* Obtener todas las tablas definidas en el sistema:

	```
	Servicio: rulz/rule/all

	METHOD: GET
	```

* Guardar y Actualizar una nueva tabla:

	```
	Servicio: rulz/rule

	METHOD: POST
	```
	```json
	DATA: {"rows":[{"case":"mujer1","entities":[{"conds":[{"type":"normal","value":"m"},{"type":"normal","value":"true"}]},{"conds":[{"type":"normal","value":"$NuevaPersona.documento.nro_documento"}]}],"actions":[{"attrType":"string","type":"modify","attr":"nro_beneficio","value":"1","entity":"NuevoBeneficio"}]},{"case":"mujer2","entities":[{"conds":[{"type":"normal","value":"m"},{"type":"none","value":""}]},{"conds":[{"type":"normal","value":"159963"}]}],"actions":[{"attrType":"string","type":"modify","attr":"nro_beneficio","value":"2","entity":"NuevoBeneficio"}]},{"case":"persona","entities":[{"conds":[{"type":"none","value":""},{"type":"normal","value":"true"}]},{"conds":[{"type":"none","value":""}]}],"actions":[{"attrType":"string","type":"modify","attr":"nro_beneficio","value":"80","entity":"NuevoBeneficio"},{"attrType":"integer","type":"modify","attr":"nro_documento","value":"$NuevaPersona.documento.nro_documento","entity":"NuevoBeneficio"}]}],"name":"Persona con Beneficio","entities":[{"conds":[{"connector":"==","attribute":"NuevaPersona.sexo","type":"normal","attrType":"string"},{"connector":"==","attribute":"NuevaPersona.documento.tipo_doc_valido","type":"normal","attrType":"boolean"}],"entity":{"description":"","plainAttr":[{"type":"object","name":"this"},{"type":"object","name":"documento"},{"type":"string","name":"documento.caracter"},{"type":"boolean","name":"documento.copia_valida"},{"type":"integer","name":"documento.nro_documento"},{"type":"boolean","name":"documento.tipo_doc_valido"},{"type":"integer","name":"documento.tipo_documento"},{"type":"boolean","name":"persona_valida"},{"type":"string","name":"sexo"},{"type":"boolean","name":"sexo_valido"},{"type":"integer","name":"tipo_documento"}],"id":"4afd5f28-40ea-11e5-ab76-c417fef93ab4","name":"NuevaPersona","schema":{"adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"sexo_valido":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"persona_valida":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"sexo":{"readableType":"texto","adding":false,"type":"string"},"tipo_documento":{"readableType":"numero entero","adding":false,"type":"integer"},"documento":{"readableType":"Objeto","adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"copia_valida":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"nro_documento":{"readableType":"numero entero","adding":false,"type":"integer"},"tipo_doc_valido":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"tipo_documento":{"readableType":"numero entero","adding":false,"type":"integer"},"caracter":{"readableType":"texto","adding":false,"type":"string"}},"tempName":""}},"tempName":""}}},{"conds":[{"connector":"==","attribute":"NuevoBeneficio.nro_documento","type":"normal","attrType":"integer"}],"entity":{"description":"","plainAttr":[{"type":"object","name":"this"},{"type":"string","name":"nro_beneficio"},{"type":"integer","name":"nro_documento"}],"id":"81492094-40ea-11e5-ab76-c417fef93ab4","name":"NuevoBeneficio","schema":{"adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"nro_beneficio":{"readableType":"texto","adding":false,"type":"string"},"nro_documento":{"readableType":"numero entero","adding":false,"type":"integer"}},"tempName":""}}}],"catalog":{"id":"2500725e-40f1-11e5-ab76-c417fef93ab4","name":"Persona con BeneficioCat"},"atomic":true,"id":"d3ecfa44-40ec-11e5-ab76-c417fef93ab4"}
	```

* Obtener una tabla a travez de su id

	```
	Servicio: rulz/rule/<id>

	METHOD: GET
	```

* Remover una tabla del sistema a partir de su id

	```
	Servicio: rulz/rule/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}

* Obtener tablas que no se encuentren asociadas a un dominio

	```
	Servicio: rulz/rule/notincatalog

	METHOD: GET
	```

* Obtener el DRL generado a partir de la tabla

	```
	Servicio: rulz/drl/rule

	METHOD: POST
	```
	```json
	DATA: {"rows":[{"case":"mujer1","entities":[{"conds":[{"type":"normal","value":"m"},{"type":"normal","value":"true"}]},{"conds":[{"type":"normal","value":"$NuevaPersona.documento.nro_documento"}]}],"actions":[{"attrType":"string","type":"modify","attr":"nro_beneficio","value":"1","entity":"NuevoBeneficio"}]},{"case":"mujer2","entities":[{"conds":[{"type":"normal","value":"m"},{"type":"none","value":""}]},{"conds":[{"type":"normal","value":"159963"}]}],"actions":[{"attrType":"string","type":"modify","attr":"nro_beneficio","value":"2","entity":"NuevoBeneficio"}]},{"case":"persona","entities":[{"conds":[{"type":"none","value":""},{"type":"normal","value":"true"}]},{"conds":[{"type":"none","value":""}]}],"actions":[{"attrType":"string","type":"modify","attr":"nro_beneficio","value":"80","entity":"NuevoBeneficio"},{"attrType":"integer","type":"modify","attr":"nro_documento","value":"$NuevaPersona.documento.nro_documento","entity":"NuevoBeneficio"}]}],"name":"Persona con Beneficio","entities":[{"conds":[{"connector":"==","attribute":"NuevaPersona.sexo","type":"normal","attrType":"string"},{"connector":"==","attribute":"NuevaPersona.documento.tipo_doc_valido","type":"normal","attrType":"boolean"}],"entity":{"description":"","plainAttr":[{"type":"object","name":"this"},{"type":"object","name":"documento"},{"type":"string","name":"documento.caracter"},{"type":"boolean","name":"documento.copia_valida"},{"type":"integer","name":"documento.nro_documento"},{"type":"boolean","name":"documento.tipo_doc_valido"},{"type":"integer","name":"documento.tipo_documento"},{"type":"boolean","name":"persona_valida"},{"type":"string","name":"sexo"},{"type":"boolean","name":"sexo_valido"},{"type":"integer","name":"tipo_documento"}],"id":"4afd5f28-40ea-11e5-ab76-c417fef93ab4","name":"NuevaPersona","schema":{"adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"sexo_valido":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"persona_valida":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"sexo":{"readableType":"texto","adding":false,"type":"string"},"tipo_documento":{"readableType":"numero entero","adding":false,"type":"integer"},"documento":{"readableType":"Objeto","adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"copia_valida":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"nro_documento":{"readableType":"numero entero","adding":false,"type":"integer"},"tipo_doc_valido":{"readableType":"Verdadero/falso","adding":false,"type":"boolean"},"tipo_documento":{"readableType":"numero entero","adding":false,"type":"integer"},"caracter":{"readableType":"texto","adding":false,"type":"string"}},"tempName":""}},"tempName":""}}},{"conds":[{"connector":"==","attribute":"NuevoBeneficio.nro_documento","type":"normal","attrType":"integer"}],"entity":{"description":"","plainAttr":[{"type":"object","name":"this"},{"type":"string","name":"nro_beneficio"},{"type":"integer","name":"nro_documento"}],"id":"81492094-40ea-11e5-ab76-c417fef93ab4","name":"NuevoBeneficio","schema":{"adding":false,"tempType":"{\"value\":\"integer\",\"readable\":\"numero entero\"}","type":"object","properties":{"nro_beneficio":{"readableType":"texto","adding":false,"type":"string"},"nro_documento":{"readableType":"numero entero","adding":false,"type":"integer"}},"tempName":""}}}],"catalog":{"id":"2500725e-40f1-11e5-ab76-c417fef93ab4","name":"Persona con BeneficioCat"},"atomic":true,"id":"d3ecfa44-40ec-11e5-ab76-c417fef93ab4"}
	```

<div id='id-abms-domains'/>
## 4.6 Dominios

* Obtener todos los dominios definidos en el sistema:

	```
	Servicio: rulz/catalog/all

	METHOD: GET
	```

* Guardar y Actualizar un nuevo dominio:

	```
	Servicio: rulz/catalog

	METHOD: POST
	```
	```json
	DATA: {"tables":[{"id":"d3ecfa44-40ec-11e5-ab76-c417fef93ab4","name":"Persona con Beneficio"}],"description":"Dominio creado por solicitud de regla atomica Persona con Beneficio","rules":[{"name":"nuevoteste","id":"89e5654e-476d-11e5-ab76-c417fef93ab4"},{"id":"ccb82d38-4129-11e5-ab76-c417fef93ab4","name":"ReglaDeTest"}],"id":"2500725e-40f1-11e5-ab76-c417fef93ab4","name":"Persona con BeneficioCat"}
	```

* Obtener un dominio a travez de su id

	```
	Servicio: rulz/catalog/<id>

	METHOD: GET
	```

* Remover un dominio del sistema a partir de su id

	```
	Servicio: rulz/catalog/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}
	```

<div id='id-abms-stage'/>
## 4.7 Escenarios

* Obtener todos los escenarios definidos en el sistema:

	```
	Servicio: rulz/simulation/all

	METHOD: GET
	```

* Guardar y Actualizar un nuevo escenario:

	```
	Servicio: rulz/simulation

	METHOD: POST
	```
	```json
	DATA: {"name": "testing", "catalogs": [{"id": "2500725e-40f1-11e5-ab76-c417fef93ab4", "name": "Persona con BeneficioCat"}], "description": "", "collection": [{"id": "4afd5f28-40ea-11e5-ab76-c417fef93ab4", "plainAttr": [{"type": "object", "name": "this"}, {"type": "object", "name": "documento"}, {"type": "string", "name": "documento.caracter"}, {"type": "boolean", "name": "documento.copia_valida"}, {"type": "integer", "name": "documento.nro_documento"}, {"type": "boolean", "name": "documento.tipo_doc_valido"}, {"type": "integer", "name": "documento.tipo_documento"}, {"type": "boolean", "name": "persona_valida"}, {"type": "string", "name": "sexo"}, {"type": "boolean", "name": "sexo_valido"}, {"type": "integer", "name": "tipo_documento"}], "description": "", "name": "NuevaPersona", "schema": {"adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"sexo_valido": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "persona_valida": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "documento": {"readableType": "Objeto", "adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"copia_valida": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "nro_documento": {"readableType": "numero entero", "adding": false, "type": "integer", "value": "369852147"}, "tipo_doc_valido": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean", "value": "true"}, "tipo_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}, "caracter": {"readableType": "texto", "adding": false, "type": "string"}}, "tempName": ""}, "sexo": {"readableType": "texto", "adding": false, "type": "string", "value": "m"}, "tipo_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}}, "tempName": ""}}, {"id": "81492094-40ea-11e5-ab76-c417fef93ab4", "plainAttr": [{"type": "object", "name": "this"}, {"type": "string", "name": "nro_beneficio"}, {"type": "integer", "name": "nro_documento"}], "description": "", "name": "NuevoBeneficio", "schema": {"adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"nro_beneficio": {"readableType": "texto", "adding": false, "type": "string"}, "nro_documento": {"readableType": "numero entero", "adding": false, "type": "integer", "value": "369852147"}}, "tempName": ""}}, {"id": "4afd5f28-40ea-11e5-ab76-c417fef93ab4", "plainAttr": [{"type": "object", "name": "this"}, {"type": "object", "name": "documento"}, {"type": "string", "name": "documento.caracter"}, {"type": "boolean", "name": "documento.copia_valida"}, {"type": "integer", "name": "documento.nro_documento"}, {"type": "boolean", "name": "documento.tipo_doc_valido"}, {"type": "integer", "name": "documento.tipo_documento"}, {"type": "boolean", "name": "persona_valida"}, {"type": "string", "name": "sexo"}, {"type": "boolean", "name": "sexo_valido"}, {"type": "integer", "name": "tipo_documento"}], "description": "", "name": "NuevaPersona", "schema": {"adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"sexo_valido": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "persona_valida": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "documento": {"readableType": "Objeto", "adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"copia_valida": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "nro_documento": {"readableType": "numero entero", "adding": false, "type": "integer", "value": "159963"}, "tipo_doc_valido": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "tipo_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}, "caracter": {"readableType": "texto", "adding": false, "type": "string"}}, "tempName": ""}, "sexo": {"readableType": "texto", "adding": false, "type": "string", "value": "m"}, "tipo_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}}, "tempName": ""}}, {"id": "81492094-40ea-11e5-ab76-c417fef93ab4", "plainAttr": [{"type": "object", "name": "this"}, {"type": "string", "name": "nro_beneficio"}, {"type": "integer", "name": "nro_documento"}], "description": "", "name": "NuevoBeneficio", "schema": {"adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"nro_beneficio": {"readableType": "texto", "adding": false, "type": "string"}, "nro_documento": {"readableType": "numero entero", "adding": false, "type": "integer", "value": "159963"}}, "tempName": ""}}, {"id": "4afd5f28-40ea-11e5-ab76-c417fef93ab4", "plainAttr": [{"type": "object", "name": "this"}, {"type": "object", "name": "documento"}, {"type": "string", "name": "documento.caracter"}, {"type": "boolean", "name": "documento.copia_valida"}, {"type": "integer", "name": "documento.nro_documento"}, {"type": "boolean", "name": "documento.tipo_doc_valido"}, {"type": "integer", "name": "documento.tipo_documento"}, {"type": "boolean", "name": "persona_valida"}, {"type": "string", "name": "sexo"}, {"type": "boolean", "name": "sexo_valido"}, {"type": "integer", "name": "tipo_documento"}], "description": "", "name": "NuevaPersona", "schema": {"adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"sexo_valido": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "persona_valida": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "documento": {"readableType": "Objeto", "adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"copia_valida": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean"}, "nro_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}, "tipo_doc_valido": {"readableType": "Verdadero/falso", "adding": false, "type": "boolean", "value": "true"}, "tipo_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}, "caracter": {"readableType": "texto", "adding": false, "type": "string"}}, "tempName": ""}, "sexo": {"readableType": "texto", "adding": false, "type": "string"}, "tipo_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}}, "tempName": ""}}, {"description": "", "plainAttr": [{"type": "object", "name": "this"}, {"type": "string", "name": "nro_beneficio"}, {"type": "integer", "name": "nro_documento"}], "id": "81492094-40ea-11e5-ab76-c417fef93ab4", "name": "NuevoBeneficio", "schema": {"adding": false, "tempType": "{\"value\":\"integer\",\"readable\":\"numero entero\"}", "type": "object", "properties": {"nro_beneficio": {"readableType": "texto", "adding": false, "type": "string"}, "nro_documento": {"readableType": "numero entero", "adding": false, "type": "integer"}}, "tempName": ""}}], "installed": false, "instances": [{"instance": {"sexo": "m", "documento": {"nro_documento": "369852147", "tipo_doc_valido": "true"}}, "entity": "NuevaPersona"}, {"instance": {"nro_documento": "369852147"}, "entity": "NuevoBeneficio"}, {"instance": {"sexo": "m", "documento": {"nro_documento": "159963"}}, "entity": "NuevaPersona"}, {"instance": {"nro_documento": "159963"}, "entity": "NuevoBeneficio"}, {"instance": {"documento": {"tipo_doc_valido": "true"}}, "entity": "NuevaPersona"}, {"instance": {}, "entity": "NuevoBeneficio"}], "installedON": {"date": "2015-08-20 11:18:11", "url": "/selectividad/rest/rule_engine/execute/testing/0", "message": "DRL Instalado correctamente: com.leafnoise.pathfinder:testing:0", "response": "com.leafnoise.pathfinder:testing:0", "success": true}, "version": "1.0", "result": "{\"message\": \"DRL Ejecutado correctamente\", \"response\": [{\"fact_name\": \"NuevaPersona\", \"properties\": {\"sexo_valido\": false, \"persona_valida\": false, \"tipo_documento\": 0, \"documento\": {\"copia_valida\": false, \"nro_documento\": 369852147, \"tipo_doc_valido\": true, \"tipo_documento\": 0, \"caracter\": null}, \"sexo\": \"m\"}}, {\"fact_name\": \"NuevoBeneficio\", \"properties\": {\"nro_beneficio\": \"1\", \"nro_documento\": 369852147}}, {\"fact_name\": \"NuevaPersona\", \"properties\": {\"sexo_valido\": false, \"persona_valida\": false, \"tipo_documento\": 0, \"documento\": {\"copia_valida\": false, \"nro_documento\": 159963, \"tipo_doc_valido\": false, \"tipo_documento\": 0, \"caracter\": null}, \"sexo\": \"m\"}}, {\"fact_name\": \"NuevoBeneficio\", \"properties\": {\"nro_beneficio\": \"1\", \"nro_documento\": 369852147}}, {\"fact_name\": \"NuevaPersona\", \"properties\": {\"sexo_valido\": false, \"persona_valida\": false, \"tipo_documento\": 0, \"documento\": {\"copia_valida\": false, \"nro_documento\": 0, \"tipo_doc_valido\": true, \"tipo_documento\": 0, \"caracter\": null}, \"sexo\": null}}, {\"fact_name\": \"NuevoBeneficio\", \"properties\": {\"nro_beneficio\": \"1\", \"nro_documento\": 369852147}}], \"success\": true}", "id": "4363bc3a-40ef-11e5-ab76-c417fef93ab4"}
	```

* Obtener un escenario a travez de su id

	```
	Servicio: rulz/simulation/<id>

	METHOD: GET
	```

* Remover un escenario del sistema a partir de su id

	```
	Servicio: rulz/simulation/remove/<id>

	METHOD: POST
	```
	```json
	DATA: {}
	```

* Obtener el DRL generado a partir del escenario

	```
	Servicio: rulz/drl/simulation

	METHOD: POST
	```
	```json
	DATA: {"name": "testing","catalogs": [{"id": "2500725e-40f1-11e5-ab76-c417fef93ab4","name": "Persona con BeneficioCat"}],"description": "","version": "1.0","result": "{\"message\": \"DRL Ejecutado correctamente\", \"response\": [{\"fact_name\": \"NuevaPersona\", \"properties\": {\"sexo_valido\": false, \"persona_valida\": false, \"tipo_documento\": 0, \"documento\": {\"copia_valida\": false, \"nro_documento\": 369852147, \"tipo_doc_valido\": true, \"tipo_documento\": 0, \"caracter\": null}, \"sexo\": \"m\"}}, {\"fact_name\": \"NuevoBeneficio\", \"properties\": {\"nro_beneficio\": \"1\", \"nro_documento\": 369852147}}, {\"fact_name\": \"NuevaPersona\", \"properties\": {\"sexo_valido\": false, \"persona_valida\": false, \"tipo_documento\": 0, \"documento\": {\"copia_valida\": false, \"nro_documento\": 159963, \"tipo_doc_valido\": false, \"tipo_documento\": 0, \"caracter\": null}, \"sexo\": \"m\"}}, {\"fact_name\": \"NuevoBeneficio\", \"properties\": {\"nro_beneficio\": \"1\", \"nro_documento\": 369852147}}, {\"fact_name\": \"NuevaPersona\", \"properties\": {\"sexo_valido\": false, \"persona_valida\": false, \"tipo_documento\": 0, \"documento\": {\"copia_valida\": false, \"nro_documento\": 0, \"tipo_doc_valido\": true, \"tipo_documento\": 0, \"caracter\": null}, \"sexo\": null}}, {\"fact_name\": \"NuevoBeneficio\", \"properties\": {\"nro_beneficio\": \"1\", \"nro_documento\": 369852147}}], \"success\": true}","id": "4363bc3a-40ef-11e5-ab76-c417fef93ab4"}
	```

* Realizar la simulación del escenario

	```
	Servicio: rulz/simulate/<id>

	METHOD: GET
	```


<div id="id-service-security"/>
## 4.8. Seguridad

* Obtener configuración de inicio

	```
	Servicio: config/initial

	METHOD: GET
	```

* Obtener token

	```
	Servicio: security/token/create

	METHOD: POST
	```
	```json
	{
		"organization": {
			"organization_id": "luzia"
		}
    }
	```

* Obtener matriz de permisos

	```
	Servicio: security/matrix

	METHOD: GET
	```

* Obtener detalles del usuario

	```
	Security: security/user/get_roles

	METHOD: GET
	```
