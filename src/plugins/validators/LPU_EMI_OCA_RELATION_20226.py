##Apertura - Desierto 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 

		msg = [] 
		data = []

		try:
	  		if message['instance']['current_task']['forms'][0]['data']['gr_declarardes']['ch_declarardes'] == 'NO':
  				return False, 'El Acto de Apertura no fue declarado como Desierto'
			
			tot = 0
			for task in message['instance']['tasks']:
				if len(task['forms']) != 0 and task['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_SEGUNDO_LLAMADO':
					tot += 1

			if tot >= 2:
				return False, 'No se permite realizar mas de 2 segundos llamados '  


		except Exception, ex:
			#current_app.logger.debug(str(ex))
			return False, 'El Acto de Apertura no fue declarado como Desierto'

  		#############################################
		#current_app.logger.debug(msg)
		if len(msg) != 0:  
			return False ,msg 
		else:
			return True, data
