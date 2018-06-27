# preseleccion a Acto-preseleccion 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message['instance']['current_task']['forms'][0]['data']['gr_preseleccion']['tabla_preseleccion_preseleccion']) 
		try:			
			data = {}

			tab_oferentes = []
			for linea in message['instance']['current_task']['forms'][0]['data']['gr_preseleccion']['tabla_preseleccion_preseleccion']:
				if len(linea) !=0:
					new_linea = {}
					new_linea = {'0':str(linea['0']),'1':str(linea['1']),'2':'','3':''}
					tab_oferentes.append(new_linea)
			
			data['gr_oferente'] = {}				
			#print tab_oferentes
			data['gr_oferente']['tab_oferentes'] = tab_oferentes
			data['gr_tipo_acto'] = {}
			data['gr_integrantes'] = {}
			data['gr_integrantes']['tabla_integrantes_integrantes'] = {'1':None,'2':None,'3':None}

			#print data 
			# if data['gr_oferente']['tab_oferentes'] 

			return True, data
		except Exception, e:
			return False,'Error durante, la validacion:: ' + str(e) 

		# please, respect the SLA! 
