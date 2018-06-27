
## Rectificar Pros. Suspendido

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['instance']['tasks'][len(message['instance']['tasks'])-1]['component_id']) 
		try:
			if message['instance']['tasks'][len(message['instance']['tasks'])-1]['component_id']== 'grupo_17972':
				return True, 'OK'
			else:
				return False,'No cumple con las condicionde para ejecutar esta accion.' 

		except Exception, e:
			return False,'No cumple con las condicionde para ejecutar esta accion.' 

  	# 	if message['instance']['tasks'][len(message['instance']['tasks'])-2]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
			# return True, 'ok'

		# please, respect the SLA! 
