# Traer datos de ultima convocatoria 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['instance']['current_task']['forms'][0]['data']['gr_esptec']) 
		# gr 6 - 7 vista y limite de vista 
		# gr 8 - 9 lim vista patron   
		# gr 10 - 11 pres muestra y lim pres muestra 
		try:
			gr_visita = False
			gr_vista_patron = False
			gr_presmues = False

			for linea in message['instance']['current_task']['forms'][0]['data']['gr_esptec']:
				if 'ch_presmuesesptec' in linea and linea['ch_realizarvisesptec'] == 'SI':
					gr_visita = True
				if 'ch_realizarvisesptec' in linea and linea['ch_vermuestraesptec'] == 'SI':
					gr_vista_patron = True
				if 'ch_realizarvisesptec' in linea and linea['ch_presmuesesptec'] == 'SI':
					gr_presmues = True

			for task in message['spec']['tasks']:
				if len(task['forms']) != 0 and task['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
					for grupo in task['forms'][0]['spec']['payload']:
						if 'gr_visita' in grupo:
							grupo['gr_visita']['properties']['showby'] = False
							if gr_visita:
								grupo['gr_visita']['properties']['showby'] = True
						if 'gr_limvisita' in grupo:
							grupo['gr_limvisita']['properties']['showby']	= False
							if gr_visita:
								grupo['gr_limvisita']['properties']['showby']	= True
						if 'gr_vista_patron' in grupo:
							grupo['gr_vista_patron']['properties']['showby'] = False
							if gr_vista_patron:
								grupo['gr_vista_patron']['properties']['showby'] = True
						if 'gr_limvista_patron' in grupo:
							grupo['gr_limvista_patron']['properties']['showby']	= False				
							if gr_vista_patron:
								grupo['gr_limvista_patron']['properties']['showby']	= True				
						if 'gr_presmues' in grupo:
							grupo['gr_presmues']['properties']['showby'] = False
							if gr_presmues:
								grupo['gr_presmues']['properties']['showby'] = True
						if 'gr_limpresmues' in grupo:
							grupo['gr_limpresmues']['properties']['showby']	= False				
							if gr_presmues:
								grupo['gr_limpresmues']['properties']['showby'] = True				
			
			repo_client = repo.get_instance("workflow")
			repo_client.update("instances", message['id'], message)

		except Exception, e:
			return False, 'Se produjo error durante la validacion de grupos' + str(e)

  		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
						data = message['instance']['tasks'][tasks]['forms'][0]['data']
			return True, data
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  







