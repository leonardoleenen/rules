import os


def genGateway(folder_path="", conf_path=""):

    if folder_path == "":
        folder_path = raw_input("Ingrese el directorio donde se encuentran los archivos fuente de ARG [default: /opt/ansesarg2015/source/ARG2]: ")
    if folder_path == "":
        folder_path = "/opt/ansesarg2015/source/ARG2"

    if conf_path == "":
        conf_path = raw_input("Ingrese el directorio donde se almacenaran los archivos de configuracion [default: /opt/arg2_folder/conf]: ")
    if conf_path == "":
        conf_path = "/opt/arg2_folder/conf"

    log_url = raw_input("Ingrese la url del autenticador utilizado [default: http://labprueba3/garquitectura/aplicaciones/argQa.aspx]: ")
    if log_url == "":
        log_url = "http://labprueba3/garquitectura/aplicaciones/argQa.aspx"

    dirsoa = raw_input("Ingrese la url donde se realizara la conexion con el director [default: http://ansesarqdir01.anses.gov.ar:81/DirectorSOA/director.svc/soap11/retrieve]: ")
    if dirsoa == "":
        dirsoa = "http://ansesarqdir01.anses.gov.ar:81/DirectorSOA/director.svc/soap11/retrieve"

    ssurl = raw_input("Ingrese la url del soapserver [default: http://argwsQa.anses.gov.ar]: ")
    if ssurl == "":
        ssurl = "http://argwsQa.anses.gov.ar"

    credurl = raw_input("Ingrese la url del director de credenciales [default: http://director.anses.gov.ar]: ")
    if credurl == "":
        credurl = "http://director.anses.gov.ar"

    mrurl = raw_input("Ingrese la url de donde se obtendra la matriz de roles [default: http://ansesarqdir01.anses.gov.ar:81/DirectorSOA/GrantForSystemGroup.svc?wsdl]: ")
    if mrurl == "":
        mrurl = "http://ansesarqdir01.anses.gov.ar:81/DirectorSOA/GrantForSystemGroup.svc?wsdl"

    cert = raw_input("Ingresa el path al certificado de validacion [default:{0}/cert_anses.crt ]: ".format(conf_path))
    if cert == "":
        cert = "{0}/cert_anses.crt".format(conf_path)

    gateway_cfg = '''
# GENERAL CONFIGURATIONS
PORT=4500
APPLICATION="ARG2"
#KNOWN_STATICS=[".woff",".map",".ttf",".ico",".gif",".png",".js",".html",".css"]
HTML_FOLDER="{0}/html"
STANDALONE_HTML_FORBIDDEN="404.html"
STANDALONE_HTML_GENERIC="500.html"
TOKEN_ATTR_CN="nombre"
TOKEN_ATTR_ORGANIZATION_ID="oficina"
MAIL_ATTR="email"
FIXED_ORGANIZATION_ID="TEST"
EMPLOYEE_EXTRA_DATA_ENABLED=True
EMPLOYEE_EXTRA_DATA_METHOD="get_employee_office"
SECURE_SERVICES_PATH="security/token/create"
SECURE_SERVICES_ENABLED=True
INITIAL_CONFIGURATION_ENABLED=False
INITIAL_CONFIG_PATH="config"
DEV_MODE=False
DEV_MODE_USER={{"one_shoot":False, "uid":"dev_mode", "email":"dev_user@moorea.io", "organization_id": "test", "roles":["Administrador"], "cn":"dev_mode"}}
DEV_MODE_TOKEN={{"token":"UN_TOKEN", "sign":"UN_SIGN", "ACTION":"un_action"}}
WILDCARD="*"

# SERVER SOAP CONFIGURATION
#WSDL='http://argws.anses.gov.ar/soap/retrieve?wsdl'
#WSDL="http://ansesarg.anses.gov.ar:4501/soap/retrieve?wsdl"
LOGIN_URL="{2}"
LOCATION="{3}"
#LOCATION="http://argss.anses.gov.ar/soap/retrieve"
ACTION="{4}/"
NAMESPACE="{4}"
CREDENTIALS_XMLNS="{5}"
EXCEPTIONS=True
SOAP_NS='soapenv'
TRACE=True
NS="ans"
PROXY={{}}

# ROLES MATRIX SERVICE DATA
ANSES_ROLES_MATRIX_WSDL="{6}"
ANSES_ROLES_MATRIX_EXCEPTIONS=True
ANSES_ROLES_MATRIX_SOAP_NS="soapenv"
ANSES_ROLES_MATRIX_TRACE=True
ANSES_ROLES_MATRIX_NS="ans"
ANSES_ROLES_MATRIX_PROXY={{}}
ANSES_ROLES_MATRIX_PARSER=lambda matrix: list(set([menu["DTOServicioAction"]["accion"] for menu in matrix]))

# SECURITY CONFIGURATION
ANSES_TOKEN_VALIDATIONS_ENABLED = True
VALIDATION_SIGN_CERT_PATH="{1}"
VALIDATION_SIGN_MSG="La firma no es valida"
VALIDATION_IP_MSG="Su IP no esta habilitada para utilizar la aplicacion"
VALIDATION_EXPIRATION_MSG="Su token ha expirado"


# SERVICES MAPPING
SERVICES=[
    {{
        'pattern': 'rulz/count/*',
        'method': 'GET',
        'soap_method': 'RulzCountCollectionGet'
    }},
    {{
        'pattern': 'security/token/create',
        'method': 'POST',
        'soap_method': 'CreateSessionToken'
    }},
    {{
        'pattern': 'security/rxf/matrix',
        'method': 'GET',
        'soap_method': 'SecurityRxfMatrix'
    }},
    {{
        'pattern': 'security/user/get_roles',
        'method': 'GET',
        'soap_method': 'SecurityUserGetRoles'
    }},
    {{
        'pattern': 'anses/get_employee_office',
        'method': 'POST',
        'soap_method': 'get_employee_office'
    }},
    {{
        'pattern': 'anses/get_office_children',
        'method': 'POST',
        'soap_method': 'get_office_children'
    }},
    {{
        'pattern': 'config/as_dict',
        'method': 'GET',
        'soap_method': 'ConfigAsDictGet'
    }},
    {{
        'pattern': 'config/save/dict',
        'method': 'POST',
        'soap_method': 'ConfigSaveDictPost'
    }},
    {{
        'pattern': 'config/*',
        'method': 'GET',
        'soap_method': 'ConfigKeyGet'
    }},
    {{
        'pattern': 'rulz/rule',
        'method': 'POST',
        'soap_method': 'RulzRulePost'
    }},
    {{
        'pattern': 'rulz/count/*',
        'method': 'GET',
        'soap_method': 'RulzCountTypeGet'
    }},
    {{
        'pattern': 'rulz/entity',
        'method': 'POST',
        'soap_method': 'RulzEntityPost'
    }},
    {{
        'pattern': 'rulz/entity/rules_related',
        'method': 'POST',
        'soap_method': 'EntityRulesRelatedPost'
    }},
    {{
        'pattern': 'rulz/entity/in_catalogs',
        'method': 'POST',
        'soap_method': 'EntityInCatalogPost'
    }},
    {{
        'pattern': 'rulz/check/entity/attribute',
        'method': 'POST',
        'soap_method': 'EntityCheckAttrPost'
    }},
    {{
        'pattern': 'rulz/catalog',
        'method': 'POST',
        'soap_method': 'RulzCatalogPost'
    }},
    {{
        'pattern': 'rulz/table',
        'method': 'POST',
        'soap_method': 'RulzTablePost'
    }},
    {{
        'pattern': 'rulz/simulation',
        'method': 'POST',
        'soap_method': 'RulzSimulationPost'
    }},
    {{
        'pattern': 'rulz/simulation/model/get',
        'method': 'POST',
        'soap_method': 'RulzSimulationModelGetPost'
    }},
    {{
        'pattern': 'rulz/simulation/jsons',
        'method': 'POST',
        'soap_method': 'RulzSimulationJsonsPost'
    }},
    {{
        'pattern': 'rulz/list',
        'method': 'POST',
        'soap_method': 'RulzDataListsPost'
    }},
    {{
        'pattern': 'rulz/function',
        'method': 'POST',
        'soap_method': 'RulzFunctionPost'
    }},
    {{
        'pattern': 'rulz/function/test',
        'method': 'POST',
        'soap_method': 'RulzFunctionsTesting',

    }},
    {{
        'pattern': 'rulz/formula',
        'method': 'POST',
        'soap_method': 'RulzFormulaPost'
    }},
    {{
        'pattern': 'rulz/instrument',
        'method': 'POST',
        'soap_method': 'RulzInstrumentPost'
    }},
    {{
        'pattern': 'rulz/instrument/file/delete',
        'method': 'POST',
        'soap_method': 'RulzInstNormFileDelete'
    }},
    {{
        'pattern': 'rulz/simulate/*',
        'method': 'GET',
        'soap_method': 'RulzSimulateIdGet'
    }},
    {{
        'pattern': 'rulz/install/publication/*',
        'method': 'POST',
        'soap_method': 'RulzInstallPublicationPost'
    }},
    {{
        'pattern': 'rulz/uninstall/publication/*',
        'method': 'POST',
        'soap_method': 'RulzUninstallPublicationPost'
    }},
    {{
        'pattern': 'snapshot/get/all',
        'method': 'GET',
        'soap_method': 'SnapshotAllGet'
    }},
    {{
        'pattern': 'snapshot/export',
        'method': 'GET',
        'soap_method': 'SnapshotExportGet'
    }},
    {{
        'pattern': 'snapshot/export/*',
        'method': 'GET',
        'soap_method': 'SnapshotExportNameGet'
    }},
    {{
        'pattern': 'snapshot/import',
        'method': 'POST',
        'soap_method': 'SnapshotImportPost'
    }},
    {{
        'pattern': 'snapshot/create/*',
        'method': 'POST',
        'soap_method': 'SnapshotCreateNamePost'
    }},
    {{
        'pattern': 'snapshot/use',
        'method': 'POST',
        'soap_method': 'SnapshotUsePost'
    }},
    {{
        'pattern': 'snapshot/delete/*',
        'method': 'POST',
        'soap_method': 'SnapshotDeleteIdPost'
    }},
    {{
        'pattern': 'snapshot/edit/*',
        'method': 'POST',
        'soap_method': 'SnapshotEditIdPost'
    }},
    {{
        'pattern': 'rulz/test',
        'method': 'POST',
        'soap_method': 'RulzTestPost'
    }},
    {{
        'pattern': 'rulz/test/data',
        'method': 'POST',
        'soap_method': 'RulzTestDataPost'
    }},
    {{
        'pattern': 'rulz/test/install',
        'method': 'POST',
        'soap_method': 'RulzTestInstallPost'
    }},
    {{
        'pattern': 'rulz/test/uninstall',
        'method': 'POST',
        'soap_method': 'RulzTestUninstall'
    }},
    {{
        'pattern': 'rulz/test/list',
        'method': 'GET',
        'soap_method': 'RulzTestListGet'
    }},
    {{
        'pattern': 'rulz/install/*',
        'method': 'GET',
        'soap_method': 'RulzInstallIdGet'
    }},
    {{
        'pattern': 'rulz/uninstall/*',
        'method': 'GET',
        'soap_method': 'RulzUninstallIdGet'
    }},
    {{
        'pattern': 'rulz/drl/*',
        'method': 'POST',
        'soap_method': 'RulzDrlTypePost'
    }},
    {{
        'pattern': 'rulz/drls',
        'method': 'GET',
        'soap_method': 'RulzDrlsGet'
    }},
    {{
        'pattern': 'rulz/drls_new',
        'method': 'POST',
        'soap_method': 'RulzDrlsNewPost'
    }},
    {{
        'pattern': 'rulz/drls/*/*',
        'method': 'GET',
        'soap_method': 'RulzDrlsTypeIdGet'
    }},
    {{
        'pattern': 'rulz/files/*/*',
        'method': 'GET',
        'soap_method': 'RulzInstrumentFileGet'
    }},
    {{
        'pattern': 'rulz/*/all',
        'method': 'GET',
        'soap_method': 'RulzTypeAll'
    }},
    {{
        'pattern': 'rulz/*/remove',
        'method': 'POST',
        'soap_method': 'RulzTypeRemovePost'
    }},
    {{
        'pattern': 'rulz/*/notincatalog',
        'method': 'GET',
        'soap_method': 'RulzTypeNoincatalogGet'
    }},
    {{
        'pattern': 'rulz/*/*',
        'method': 'GET',
        'soap_method': 'RulzTypeIdGet'
    }},
    {{
        'pattern': 'auditory/registered_users',
        'method': 'GET',
        'soap_method': 'AuditRegUsersGet'
    }},
    {{
        'pattern': 'auditory/search',
        'method': 'POST',
        'soap_method': 'AuditSearchPost'
    }},
    {{
        'pattern': 'auditory/getdata/*',
        'method': 'GET',
        'soap_method': 'AuditGetDataIdGet'
    }},
    {{
        'pattern': 'auditory/getregistry/*',
        'method': 'GET',
        'soap_method': 'AuditGetRegistryIdGet'
    }},
    {{
        'pattern': 'api/register_key',
        'method': 'POST',
        'soap_method': 'ApiRegisterKeyPost'
    }},
    {{
        'pattern': 'api/all_keys',
        'method': 'GET',
        'soap_method': 'ApiAllKeysGet'
    }},
    {{
        'pattern': 'api/delete_key/*',
        'method': 'POST',
        'soap_method': 'ApiDeleteKeyPost'
    }}]
    '''.format(folder_path, cert, log_url, dirsoa, ssurl, credurl, mrurl)

    ensure_dir(conf_path)
    with open(conf_path + os.sep + "gateway.cfg", "w") as f:
        f.write(gateway_cfg)

    genSoapServercfg(ssurl, conf_path, folder_path)


def genSoapServercfg(ssurl="", conf_path="", folder_path=""):

    if conf_path == "":
        conf_path = raw_input("Ingrese el directorio donde se almacenaran los archivos de configuracion [default: /opt/arg2_folder/config]: ")
    if conf_path == "":
        conf_path = "/opt/arg2_folder/config"

    if ssurl == "":
        ssurl = raw_input("Ingrese la url donde se encuentra el Soap Server [default: http://argwsQa.anses.gov.ar]: ")
    if ssurl == "":
        ssurl = "http://argwsQa.anses.gov.ar"

    sscontext = raw_input("Ingrese el contexto de las acciones del soap server [default: /soap/retrieve]: ")
    if sscontext == "":
        sscontext = "/soap/retrieve"

    wsdlurl = raw_input("Ingrese la url del wsdl que se utilizara [default: http://ansesnegodesapp/BUSS/Anses.BUSS.EmpleadosUnidadOrganica.Servicio/EmpleadoUnidadOrganicaWS.asmx?wsdl]: ")
    if wsdlurl == "":
        wsdlurl = "http://ansesnegodesapp/BUSS/Anses.BUSS.EmpleadosUnidadOrganica.Servicio/EmpleadoUnidadOrganicaWS.asmx?wsdl"

    arghost = raw_input("Ingrese la url donde se encuentra corriendo ARG [default: http://localhost:5000]: ")
    if arghost == "":
        arghost = "http://localhost:6000"

    ssconf = '''
# Keys that will be inserted on template. Strings must have double quotes ("'example'") the others just one.
NAMESPACE="'{0}'"
SERVICE_LOCATION="'{1}'"
VALIDATOR="None"
SERVICES=[
    {{
        "location": "'{3}/'",
        "function": "RulzCountCollectionGet"
    }},
    {{
        "location": "'{3}/'",
        "function": "CreateSessionToken"
    }},
    {{
        "location": "'{3}/'",
        'function': 'SecurityRxfMatrix'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SecurityUserGetRoles'
    }},
    {{
        "location": "'{3}/'",
        'function': 'ConfigAsDictGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'ConfigSaveDictPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'ConfigKeyGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzRulePost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzCountTypeGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzEntityPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'EntityRulesRelatedPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'EntityInCatalogPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'EntityCheckAttrPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzCatalogPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzDataListsPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTablePost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzSimulationPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzSimulationModelGetPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzSimulationJsonsPost'
    }},
    {{
        "location": "'{3}/'",
        "function": 'RulzFunctionPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzFunctionsTesting'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzFormulaPost'
    }},
    {{
        "location": "'{3}/'",
        "function": 'RulzInstrumentPost'
    }},
    {{
        "location": "'{3}/'",
        "function": 'RulzInstNormFileDelete'
    }},
    {{
        "location": "'{3}/'",
        "function": 'RulzSimulateIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzInstallPublicationPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzUninstallPublicationPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotAllGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotExportGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotExportNameGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotImportPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotCreateNamePost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotUsePost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotDeleteIdPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'SnapshotEditIdPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTestPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTestDataPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTestInstallPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTestUninstall'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTestListGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzInstallIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzUninstallIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzDrlTypePost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzDrlsGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzDrlsNewPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzDrlsTypeIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzInstrumentFileGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTypeAll'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTypeRemovePost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTypeNoincatalogGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'RulzTypeIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'AuditRegUsersGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'AuditSearchPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'AuditGetDataIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'AuditGetRegistryIdGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'ApiRegisterKeyPost'
    }},
    {{
        "location": "'{3}/'",
        'function': 'ApiAllKeysGet'
    }},
    {{
        "location": "'{3}/'",
        'function': 'ApiDeleteKeyPost'
    }}
    ]

# App configuration
PORT=4501

EXTERNAL_SERVICES=[{{
                "function":"get_employee_office",
                "namespace":"'{0}'",
                "wsdl":"'{2}'",
                "soap_ns":"'soapenv'",
                "trace":"True",
                "ns":"''",
                "exceptions":"True",
                "soap_attributes":"legajo=data.get('legajo')",
                "soap_method":"obtenerEmpleadoLegajo",
                "response_parser":"lambda response: (response != None and response.get('obtenerEmpleadoLegajoResult') != None and {{'txt_personal_superior': response.get('obtenerEmpleadoLegajoResult')['PersonalSuperior'], 'txt_nivel_superior': response.get('obtenerEmpleadoLegajoResult')['NivelSuperior'], 'txt_nivel_unidad': response.get('obtenerEmpleadoLegajoResult')['NivelUnidad']}}) or {{}}"
}}]
'''.format(ssurl, sscontext, wsdlurl, arghost)

    ensure_dir(conf_path)
    with open(conf_path + os.sep + "soapserver.cfg.arg2", "w") as f:
        f.write(ssconf)

    with open(folder_path + os.sep + "wsdl_content.xml", "r") as f:
        wsd_cont = f.read()

    with open(conf_path + os.sep + "retrieve.wsdl", "w") as f:
        f.write(wsd_cont.format(ssurl, sscontext))


def ensure_dir(folder):
    d = os.path.dirname(folder + os.sep)
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno == 13:
                raise Exception("No se poseen permisos para crear los directorios en el sistema")

if __name__ == '__main__':
    genGateway()
