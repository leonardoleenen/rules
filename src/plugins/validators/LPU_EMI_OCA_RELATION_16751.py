# Apertura - Preseleccion
from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys 
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import toolbox 

class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message)
		data = {}
		gr_preseleccion = {}
		gr_preseleccion['tabla_preseleccion_preseleccion'] = {}

		try:
			try:
				if message['instance']['current_task']['forms'][0]['data']['gr_declarardes']['ch_declarardes'] == 'SI':
	  				return False, 'El Acto de Apertura fue declarado como Desierto.'	
			except Exception, e:
				print 'pepe'
	  		
			
			tabla_preseleccion_preseleccion1 = []
			for linea in  message['instance']['current_task']['forms'][0]['data']['gr_oferentes']:
				cb_fgoerente = []
				cb_monedagtiaoferente = []
				new_line = {}
				if 'cb_fgoerente' in linea:
						cb_fgoerente.append(toolbox.multiSelection_to_text(linea['cb_fgoerente']))
				if 'cb_monedagtiaoferente' in linea:
						cb_monedagtiaoferente.append(toolbox.multiSelection_to_text(linea['cb_monedagtiaoferente']))
				if 'txt_nombreoferente' in linea:
					new_line['0'] = str(linea['txt_nombreoferente'])
				if 'txt_cuitoferente' in linea:
					new_line['1'] = str(linea['txt_cuitoferente'])
				new_line['2'] = cb_fgoerente
				new_line['3'] = cb_monedagtiaoferente
				if 'dec_montogtiaoferente' in linea:
					new_line['4'] = str(linea['dec_montogtiaoferente'])	
				# new_line['5'] = None
				# new_line['6'] = None

				tabla_preseleccion_preseleccion1.append(new_line)
			gr_preseleccion['tabla_preseleccion_preseleccion'] = tabla_preseleccion_preseleccion1
			data['gr_preseleccion'] = gr_preseleccion
			print gr_preseleccion


			# data['gr_integrantes'] = {}
			# data['gr_integrantes']['tabla_integrantes_integrantes'] = {'1':None,'2':None,'3':None}
		
		except Exception, ex:
			current_app.logger.debug(str(ex))
			return False, 'Error durante la validacion:: ' + str(ex)
 
  
		return True, data

