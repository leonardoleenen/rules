# -*- coding: utf-8; -*-

from flask import request
from utils import repo
from logging import getLogger
import datetime
import json
import uuid

'''
    Nombre de fantasía asignado al sistema que generó la grabación
2
ClavePrincipal
varchar – not null
25
Dato que permita identificar los registros (Nro. de beneficio, Nro. de CUIL, Nro. expediente, etc.)
3
IpOrigen
varchar – not null
15
Nro. de IP desde la cual se generó la acción.
En caso batch: vacío
4
CUITOrganismoAutenticador
numeric – not null
￼
11
CUIT del Organismo que autenticó
En caso batch: vacío
5
CUITOrganismoUsuario
numeric – not null
￼
11
CUIT del Organismo al que pertenece el usuario.
En caso batch: vacío
6
Dependencia
varchar – not null
￼
11
Dependencia a la que pertenece el usuario.
￼6/8
￼￼Ministerio de Trabajo, Empleo y Seguridad Social
Especificaciones vinculadas a Logs de Auditoria
￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼￼En caso batch: vacío
￼￼￼￼7
￼￼Autenticador
￼￼varchar – not null
￼￼￼￼5
￼￼￼Método de autenticación del Organismo que autenticó. En caso batch: vacío
￼￼￼￼8
CódigoUsuario
￼varchar – not null
￼￼11
￼Identificador del Usuario que ejecutó la acción
En caso batch: vacío
￼￼￼￼9
￼￼￼Tabla
￼￼￼￼varchar – not null
￼￼￼￼￼￼40
￼￼￼￼￼Tabla asociada a la acción
￼￼￼￼10
￼￼TipoAcción
￼￼char – not null
￼￼￼￼1
￼￼￼(I) – Insert; (D) - Delete; (U) – Update, tanto para el registro anterior como el posterior al update, (C) - Consulta.
￼￼￼￼11
￼￼EntornoEjecucion
￼￼char – not null
￼￼￼￼1
￼￼￼Identifica el entorno desde donde se realizan las actualizaciones.
(B) Batch
(O) Online
￼￼￼￼12
￼￼NombreServicio
￼￼varchar – not null
￼￼￼￼40
￼￼￼Nombre de servicio Web al que pertenece el método que se ejecuta
En caso batch: nombre del proceso a través del cual se efectuó la grabación.
￼￼￼￼13
￼￼￼NombreMetodo
￼￼Varchar – not null
￼￼￼￼40
￼￼￼￼Nombre del Método
En caso batch: Nro. asignado por la Gerencia Informática e Innovación Tecnológica a la nota a través de la cual se requirió el proceso. El formato será: <Nro. Nota>(AAAANNNNNN, donde AAAA equivale al año en que se emitió la nota y NNNNN al Nro.
￼￼￼7/8
￼￼Ministerio de Trabajo, Empleo y Seguridad Social Especificaciones vinculadas a Logs de Auditoria
￼
de nota asignado, completando con ceros a la izquierda, en caso de corresponder.
De no existir nota de solicitud, indicar origen de la grabación (Ejemplo: proceso mensual)
14
FechaHora
datetime – not null
￼23
Fecha y hora del servidor
15
Datos
nvarchar – not null
1200
￼
Datos correspondientes a la tabla asociada a la acción:
- Los campos numéricos y Date deben ser desempaquetados.
- Se deben sacar los espacios a la derecha, asegurando la buena utilización del varchar.
Campos que se toman del token de autenticación:
￼
Campo
￼￼
￼
Se toma de
￼
NombreFantasia
Elemento <login>, atributo <system>
IPOrigen
Elemento <login>, Subelemento <info>, atributo <name> con valor “ip”, atributo <value>
CUITOrganismoAutentticador
Elemento <login>, atributo <entity>
CUITOrganismoUsuario
Elemento <login>, Subelemento <info>, atributo <name> con valor “empresa”, atributo <value>
Dependencia
Elemento <login>, Subelemento <info>, atributo <name> con valor “oficina”, atributo <value>
Autenticador
Elemento <login>, atributo <authmethod>.
CódigoUsuario
Elemento <login>, atributo <uid>


    ANSES
    <?xml version="1.0"?>
<sso xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <id src="cn=LDAPServer,ou=GSYT,o=ANSES,c=AR" dst="cn=AuthServer,ou=GSYT,o=ANSES,c=AR" unique_id="562F7464632-0-551A" gen_time="1445946964" exp_time="1445950564" />
  <operation type="login">
    <login system="bandeja" entity="33637617449" uid="20367163764" username="20367163764" authmethod="LDAP">
      <info name="nombre" value="PEGA CARLOS AUGUSTO" />
      <info name="email" value="ega@gmail.com" />
      <info name="oficina" value="99999974" />
      <info name="oficinadesc" value="Tramites Web CVSS" />
      <info name="ip" value="10.86.39.19" />
      <info name="nivel" value="3" />
      <groups>
        <group name="internet" />
      </groups>
    </login>
  </operation>
</sso>


    {
    "cn": "PEGA CARLOS AUGUSTO",
    "dependencia_cod": "",
    "dependencia_desc": "USUARIO NO ASOCIADO A UNA DEPENDENCIA",
    "email": "capega@anses.gov.ar",
    "extra_data": null,
    "office_desc": " Coordinacion Investigacion Desarrollo Te",
    "office_id": "H108600000",
    "one_shoot": false,
    "organization": {
      "organization_description": "bandeja",
      "organization_id": "bandeja"
    },
    "ou": "H108600000 Coordinacion Investigacion Desarrollo Te,H108000000 Dir Tecnologia y Arquitectura de TI,H100000000 Dir Gral Informatica e Innov Tecnologica,H000000000 Sd Ej de Administracion,A000000000 Direccion Ejecutiva",
    "payload": {
      "organization": {
        "organization_description": "bandeja",
        "organization_id": "bandeja"
      }
    },
    "roles": [
      {
        "rol_description": "Intranet - Agente",
        "rol_id": "INTRANET-AGENTE"
      }
    ],
    "system": "bandeja",
    "token_and_sign": {
      "sign": "DpW8eGr8XMFrJ62h/RgmjU0MBCWGaiVcg1QhGZYt+oAsJkJ0UsYaCCAQthHt1DVhtPelpMhHmjzXudWDDqIucmtPsjYZMCIa9A/RXC25ED+qkcBF28ZmLK/BzMw/cIItE+vp6+IT7dtJF4nnixXyVpeCvuoWXYrkcZo0Z7aSwRs=",
      "token": "PD94bWwgdmVyc2lvbj0iMS4wIj8+DQo8c3NvIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhtbG5zOnhzZD0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEiPg0KICA8aWQgc3JjPSJjbj1BdXRoU2VydmVyLG91PUdTWVQsbz1BTlNFUyxjPUFSIiBkc3Q9ImNuPUFwbGljYWNpb25lcyxvdT1HU1lULG89QU5TRVMsYz1BUiIgdW5pcXVlX2lkPSI1NjJFODRGOTg3NS0xLTc5M0MiIGdlbl90aW1lPSIxNDQ1ODg1NjczIiBleHBfdGltZT0iMTQ0NTg4OTI3MyIgLz4NCiAgPG9wZXJhdGlvbiB0eXBlPSJsb2dpbiI+DQogICAgPGxvZ2luIHN5c3RlbT0iYmFuZGVqYSIgZW50aXR5PSIzMzYzNzYxNzQ0OSIgdWlkPSJFNzE2Mzc2IiB1c2VybmFtZT0iRTcxNjM3NiIgYXV0aG1ldGhvZD0iTlRMTSI+DQogICAgICA8aW5mbyBuYW1lPSJub21icmUiIHZhbHVlPSJQRUdBIENBUkxPUyBBVUdVU1RPIiAvPg0KICAgICAgPGluZm8gbmFtZT0iZW1haWwiIHZhbHVlPSJjYXBlZ2FAYW5zZXMuZ292LmFyIiAvPg0KICAgICAgPGluZm8gbmFtZT0ib2ZpY2luYSIgdmFsdWU9IiIgLz4NCiAgICAgIDxpbmZvIG5hbWU9Im9maWNpbmFkZXNjIiB2YWx1ZT0iVVNVQVJJTyBOTyBBU09DSUFETyBBIFVOQSBERVBFTkRFTkNJQSIgLz4NCiAgICAgIDxpbmZvIG5hbWU9ImlwIiB2YWx1ZT0iMTAuODYuMzkuMTkiIC8+DQogICAgICA8aW5mbyBuYW1lPSJkZXBhcnRtZW50IiB2YWx1ZT0iIiAvPg0KICAgICAgPGluZm8gbmFtZT0ib3UiIHZhbHVlPSJIMTA4NjAwMDAwIENvb3JkaW5hY2lvbiBJbnZlc3RpZ2FjaW9uIERlc2Fycm9sbG8gVGUsSDEwODAwMDAwMCBEaXIgVGVjbm9sb2dpYSB5IEFycXVpdGVjdHVyYSBkZSBUSSxIMTAwMDAwMDAwIERpciBHcmFsIEluZm9ybWF0aWNhIGUgSW5ub3YgVGVjbm9sb2dpY2EsSDAwMDAwMDAwMCBTZCBFaiBkZSBBZG1pbmlzdHJhY2lvbixBMDAwMDAwMDAwIERpcmVjY2lvbiBFamVjdXRpdmEiIC8+DQogICAgICA8Z3JvdXBzPg0KICAgICAgICA8Z3JvdXAgbmFtZT0iQWRtaW5pc3RyYWRvciIgLz4NCiAgICAgIDwvZ3JvdXBzPg0KICAgIDwvbG9naW4+DQogIDwvb3BlcmF0aW9uPg0KPC9zc28+"
    },
    "uid": "E716376",
    "user_profiles": [
      {
        "profile_description": "Administrador",
        "profile_id": "Administrador"
      }
    ]
  }

'''

action_type = {'I': '(I): Insert', 'U': '(U): Update', 'D': '(D): Delete'}


def requestData():
    data = {}
    try:
        data['remote_addr'] = str(request.remote_addr)
        data['method'] = str(request.method)
        data['url'] = str(request.url)
    except Exception:
        return data
    return data


def save(object_to_audit, token, object_id, collection_name, tp='I'):

    reqData = requestData()

    message = {
        "this_id": str(uuid.uuid1()),
        "nombre_fantasia": token.get('system'),
        "clave_principal": str(object_id),
        "iporigen": reqData.get('remote_addr'),
        "autenticador": token.get('authmethod'),
        "dependencia": token.get('dependencia_desc'),
        "cuit_organismo_autenticador": token.get('cuit_organismo_autenticador'),
        "cuit_organismo_usuario": token.get('cuit_organismo_usuario'),
        "codigo_usuario": token.get('uid'),
        "nombre_usuario": token.get('cn'),
        "roles": token.get('roles'),
        "tabla": collection_name,
        "data": object_to_audit,
        "tipo_accion": action_type[tp],
        "entorno_ejecucion": 'ONLINE',
        "tipo_metodo": reqData.get('method'),
        "url_metodo": reqData.get('url'),
        "fecha_hora": str(datetime.datetime.now().isoformat())
    }

    getLogger('arg_audit').info(json.dumps(message))

    repo_client = repo.get_instance("auditoria_arg2")
    repo_client.save_audit('audit', message)
