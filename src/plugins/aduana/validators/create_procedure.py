from yapsy.IPlugin import IPlugin
from flask import current_app
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/lr')
from services import workflow_engine as wf
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo


class PluginEngine(IPlugin):
	def execute(self,message):
		current_app.logger.debug(message)
		if (message['data'] != {}) and message['data']['gr_datos_procedimiento']['cb_tipo_de_procedimiento']['id'] == '1':
			FLOW_ID = 'ANB-IMP-REGLA-PRODUCCION'

		# elif(message['data'] != {}) and message['data']['gr_datos_procedimiento']['cb_tipo_de_procedimiento']['id'] == '2':
		# 	FLOW_ID = ''
		
		# elif(message['data'] != {}) and message['data']['gr_datos_procedimiento']['cb_tipo_de_procedimiento']['id'] == '3':
		# 	FLOW_ID = ''
		
		# elif(message['data'] != {}) and message['data']['gr_datos_procedimiento']['cb_tipo_de_procedimiento']['id'] == '4':
		# 	FLOW_ID = ''

		else:
			return False,"No hay un flujo definido para la configuracion especificada."	

########################################
		current_app.logger.debug(FLOW_ID)

		# message['data']['organismo'] = wf.get_sub_organization_data(message['suborganization'])['data']['organismo']  
		
		MSG={
			"header": {
				"name": message['data']['gr_datos_procedimiento']['txt_nombre'].upper(),
				"context_organization": current_app.config['ORGANIZATION_CONTEXT_ID'],
				"suborganization":message['suborganization'],
				"owner":message['user'],
				"is_subprocess" : "false",
				"is_template" : "false",
				"flow": {
					"id": FLOW_ID,
					"service_id": 'specs',
					"idPadre": '0',
					"text": FLOW_ID
				},
				"data_header" : message['data']
			}
		}

		success, msg = wf.create_instance_back(FLOW_ID,MSG)

		if success:
			return True, "Exito al crear el procedimiento"
		else:
			return False, "No se encontro el flujo para el procedimiento seleccionado"
 





