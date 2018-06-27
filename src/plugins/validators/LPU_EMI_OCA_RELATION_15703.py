
# Acto de Preseleccion - Finalizar 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message) 

		if 'gr_finalizaciondelprocedimiento' in message['instance']['current_task']['forms'][0]['data']:
				if 'ch_declararsinefecto' in message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']: 
					if message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']['ch_declararsinefecto'] == 'SI':
						return True, 'OK'
		# please, respect the SLA! 
		return False,"El acto no fue declarado como 'sin efecto'" 
