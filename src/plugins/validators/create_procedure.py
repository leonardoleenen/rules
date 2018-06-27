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
		#current_app.logger.debug(message['data'])
		if (message['data'] != {}) and ( message['data']['datos_procedimientoA']['cb_tipo_procedimiento']['id'] == '10' 
										and message['data']['datos_procedimientoA']['cb_clase']['id'] == '22' 
										and message['data']['datos_procedimientoA']['cb_causal']['id'] == '100' 
										and message['data']['datos_procedimientoA']['cb_modalidad']['id'] == '150'
										):
			FLOW_ID = 'LPU-EMI-OCA'

		elif(message['data'] != {}) and ( message['data']['datos_procedimientoA']['cb_tipo_procedimiento']['id'] == '' 
										and message['data']['datos_procedimientoA']['cb_clase']['id'] == '' 
										and message['data']['datos_procedimientoA']['cb_causal']['id'] == '' 
										and message['data']['datos_procedimientoA']['cb_modalidad']['id'] == ''
										):
			FLOW_ID = 'FLUJO_ID'
			return False, "Esto es un Ejemplo de nuevo flujo"
						
		else:
			return False,"No hay un flujo definido para la configuracion especificada."	

########################################
		# current_app.logger.debug(FLOW_ID)
		
		# message['data']['organismo'] = wf.get_sub_organization_data(message['suborganization'])['data']['organismo']  

		message['data']['organismo'] = message['suborganization']

		MSG={
			  "header": {
			    "name": message['data']['datos_procedimientoA']['txt_exp_objeto'].upper(),
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

		id_ardifusion = wf.create_instance_back(FLOW_ID,MSG)

		repo_client = repo.get_instance("workflow")
		instance = repo_client.get_by_id("instances", id_ardifusion[1])
		# instance['header']['data_header']['datos_expA']['id_ardifusion'] = id_ardifusion[1]
		repo_client.update("instances", id_ardifusion[1], instance)

		return True, id_ardifusion
		# bug pendiente, si no existe el flujo no tira ningun erro ... 




