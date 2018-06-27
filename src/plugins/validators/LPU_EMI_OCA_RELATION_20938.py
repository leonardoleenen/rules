from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message['instance']['current_task']['forms'][0]['data']['gr_esptec']) 
		# please, respect the SLA! 
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
					#print 'gr_visita = True'
				if 'ch_realizarvisesptec' in linea and linea['ch_vermuestraesptec'] == 'SI':
					gr_vista_patron = True
					#print 'gr_vista_patron = True'
				if 'ch_realizarvisesptec' in linea and linea['ch_presmuesesptec'] == 'SI':
					gr_presmues = True
					#print 'gr_presmues = True'

			#print '---------------------------------------------------------------------'
			#print '---------------------------------------------------------------------'
			#print '---------------------------------------------------------------------'
			#print '---------------------------------------------------------------------'
			for task in message['spec']['tasks']:
				if len(task['forms']) != 0 and task['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
					#print 'LPU_EMI_OCA_CONVOCATORIA'
					for grupo in task['forms'][0]['spec']['payload']:
						if 'gr_visita' in grupo:
							#print 'gr_visita false '
							grupo['gr_visita']['properties']['showby'] = False
							if gr_visita:
								#print 'gr_visita true'
								grupo['gr_visita']['properties']['showby'] = True
						if 'gr_limvisita' in grupo:
							#print 'gr_limvisita false'
							grupo['gr_limvisita']['properties']['showby']	= False
							if gr_visita:
								#print 'gr_limvisita true'
								grupo['gr_limvisita']['properties']['showby']	= True
						if 'gr_vista_patron' in grupo:
							#print 'gr_vista_patron false'
							grupo['gr_vista_patron']['properties']['showby'] = False
							if gr_vista_patron:
								#print 'gr_vista_patron true'
								grupo['gr_vista_patron']['properties']['showby'] = True
						if 'gr_limvista_patron' in grupo:
							grupo['gr_limvista_patron']['properties']['showby']	= False				
							#print 'gr_limvista_patron false'
							if gr_vista_patron:
								#print 'gr_limvista_patron false'
								grupo['gr_limvista_patron']['properties']['showby']	= True				
						if 'gr_presmues' in grupo:
							grupo['gr_presmues']['properties']['showby'] = False
							#print 'gr_presmues false' 
							if gr_presmues:
								#print 'gr_presmues true' 
								grupo['gr_presmues']['properties']['showby'] = True
						if 'gr_limpresmues' in grupo:
							grupo['gr_limpresmues']['properties']['showby']	= False				
							#print 'gr_limpresmues false'
							if gr_presmues:
								#print 'gr_limpresmues true'
								grupo['gr_limpresmues']['properties']['showby'] = True				
			
			repo_client = repo.get_instance("workflow")
			repo_client.update("instances", message['id'], message)
			return True, 'OK'
		except Exception, e:
			return False, 'Se produjo error durante la validacion de grupos' + str(e)
