from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo 


class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message)
		try:
			message['spec']['tasks'][3]['forms'][0]['spec']['payload'][4]['gr_vista_patron']['properties']['showby'] = False
			message['spec']['tasks'][3]['forms'][0]['spec']['payload'][5]['gr_limvista_patron']['properties']['showby']	= False
			message['spec']['tasks'][3]['forms'][0]['spec']['payload'][2]['gr_visita']['properties']['showby'] = False
			message['spec']['tasks'][3]['forms'][0]['spec']['payload'][3]['gr_limvisita']['properties']['showby']	= False				
			gr_tecnica = message['instance']['current_task']['forms'][0]['data']['gr_esptec']
			#current_app.logger.debug(gr_tecnica)		
			for linea in gr_tecnica:
				if 'ch_presmuesesptec' in linea and linea['ch_presmuesesptec'] == 'SI':
					message['spec']['tasks'][3]['forms'][0]['spec']['payload'][4]['gr_vista_patron']['properties']['showby'] = True
					message['spec']['tasks'][3]['forms'][0]['spec']['payload'][5]['gr_limvista_patron']['properties']['showby']	= True
				if 'ch_realizarvisesptec' in linea and linea['ch_realizarvisesptec'] == 'SI':
					message['spec']['tasks'][3]['forms'][0]['spec']['payload'][2]['gr_visita']['properties']['showby'] = True
					message['spec']['tasks'][3]['forms'][0]['spec']['payload'][3]['gr_limvisita']['properties']['showby']	= True				

			repo_client = repo.get_instance("workflow")
			repo_client.update("instances", message['id'], message)

			return False, 'EXITO' 


		except Exception, e:
			return False, 'Se produjo error durante la validacion ' + str(e)


