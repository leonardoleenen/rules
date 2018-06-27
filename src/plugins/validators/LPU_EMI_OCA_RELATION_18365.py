# Preseleccion - Aper. Economico

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
		#data = message['instance']['current_task']
		# please, respect the SLA! 
		return True,'ok' 


