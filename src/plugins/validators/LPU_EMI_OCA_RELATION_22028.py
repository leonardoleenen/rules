
# Acto Preseleccion  -- Pliego 

# Trae pliego 
# Valida que no haya mas de 2 segundos llamados 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message) 
		try:
			tot = 0

			for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
			  			data = message['instance']['tasks'][tasks]['forms'][0]['data']

					if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_SEGUNDO_LLAMADO':
						tot = tot + 1
			if tot >= 2:
				return False, 'No se permite realizar mas de 2 segundos llamados '  


			'''
			valido que se haya declarado gracasado: 
				- que exista el grupo
				- que exista el combo
				- si combo  = si 
			'''
			
			if 'gr_finalizaciondelprocedimiento' in message['instance']['current_task']['forms'][0]['data']:
				if 'ch_declararfracasado' in message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']: 
					if message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']['ch_declararfracasado'] == 'SI':
						return True, data
					
			return False,"El acto no fue declarado como 'Fracasado'" 


		except Exception, e:
			return False, 'Error durante la validacion ' + str(e)