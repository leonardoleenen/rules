


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message) 
  		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'SP_OCA_ORDEN_DE_COMPRA':
			  			data = message['instance']['tasks'][tasks]['forms'][0]['data']
			result = {}
			result['gr_proveedor'] = {}
			result['gr_proveedor']['cuit'] = data['datos_prov']['cuit']
			result['gr_proveedor']['razon'] = data['datos_prov']['prov_razon']
			return True, result 
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  
