#   Rectificar Apertura Economica 


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
  
  		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_APERTURA_ECONOMICA':
						data = message['instance']['tasks'][tasks]['forms'][0]['data']
			return True, data 
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  

