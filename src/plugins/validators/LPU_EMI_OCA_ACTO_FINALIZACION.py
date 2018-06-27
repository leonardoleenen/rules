
# LPU_EMI_OCA_ACTO_FINALIZACION

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
		error = []
		if 'ch_declarardesierto' in message['data']['gr_finalizaciondelprocedimiento'] and message['data']['gr_finalizaciondelprocedimiento']['ch_declarardesierto'] == 'SI' :
			error.append('SI')
		if 'ch_declararfracasado' in message['data']['gr_finalizaciondelprocedimiento'] and message['data']['gr_finalizaciondelprocedimiento']['ch_declararfracasado'] == 'SI' :
			error.append('SI')
		if 'ch_declararsinefecto' in message['data']['gr_finalizaciondelprocedimiento'] and message['data']['gr_finalizaciondelprocedimiento']['ch_declararsinefecto'] == 'SI' :
			error.append('SI')

		if len(error) > 1:
			return False, "Seleccione una unica opcion en el grupo 'Finalizacion del procedimiento'"
		# please, respect the SLA! 
		return True,'Este es el mensaje de retorno' 
