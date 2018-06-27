# Convocatoria a vigente

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		current_app.logger.debug(message['instance']['current_task']['forms'][0]['data']) 
  		data = message['instance']['current_task']['forms'][0]['data']
		# please, respect the SLA! 
		return True,'TD::: Condiciones de la publicacion de formularios. ' 
