## Modificatorai Fechas - Vigente 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
  

		## PUBLICAR !!! 


		# please, respect the SLA! 
		return True,'Este es el mensaje de retorno' 
