#Rectificar acto de Preseleccion


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
  
  		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_ACTO_PRESELECCION':
			  			#print message['instance']['tasks'][tasks]['forms'][0]['data']['gr_aper']
			  			return True, message['instance']['tasks'][tasks]['forms'][0]['data']
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  
