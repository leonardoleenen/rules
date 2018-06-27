from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
		msg = [] 
		try:
		
			data = message['instance']['tasks'][2]['forms'][0]['data']

		except Exception, ex:

			current_app.logger.debug(str(ex))
			return False, 'Error durante la validacion:: ' + str(ex)
				


  		#############################################
		#current_app.logger.debug(msg)
		if len(msg) != 0:  
			return False ,msg 
		else:
  			### antes del return se debe publicar esto !!!
			return True, data
