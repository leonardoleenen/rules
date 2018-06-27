# Apertura Economica - - Cuadro Comparativo
from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(len(message['instance']['current_task']['forms'][0]['data']['gr_oferentes'])) 
		msg = {}
		msg['gr_unicooferente'] = {}
		msg['gr_unicooferente']['ch_unicooferente_unicooferente'] = 'NO'
		try:			
			for task in message['spec']['tasks']:
				if len(task['forms']) != 0 and task['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CUADRO_COMPARATIVO':
					for grupo in task['forms'][0]['spec']['payload']:
						if 'gr_unicooferente' in grupo: 
							grupo['gr_unicooferente']['properties']['showby'] = False	
							if len(message['instance']['current_task']['forms'][0]['data']['gr_oferentes']) == 1:						
								grupo['gr_unicooferente']['properties']['showby'] = True
			repo_client = repo.get_instance("workflow")
			repo_client.update("instances", message['id'], message)
		except Exception, e:
			return False, 'ERROR desconocido 1* !!!! ' + str(e)

		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
			  			pliego = message['instance']['tasks'][tasks]['forms'][0]['data']
  		
			apertura = message['instance']['current_task']['forms'][0]['data']

			msg['gr_cuadrocomp'] = {}
			msg['gr_datosoferta'] = {}
			tabla_cuadrocomp_cuadrocomp = []
			tabla_datosoferta_datosoferta = []
			for linea_apertura in apertura['gr_oferentes']:
				new_line = {}
				new_line = {
							'0':linea_apertura['txt_cuitoferente'],
							'1':linea_apertura['txt_nombreoferente'],
							'2':'',
							'3':'',
							'4':'',
							'5':'',
							'6':''
							}
				tabla_datosoferta_datosoferta.append(new_line)
				
				for linea_pliego in pliego['gr_esptec']:
					new_line = {}

					new_line['0'] = linea_apertura['txt_cuitoferente']
					new_line['1'] = linea_apertura['txt_nombreoferente']
					
					if 'int_renglonesptec' in linea_pliego:
						new_line['2'] = linea_pliego['int_renglonesptec']
					else: 
						new_line['2'] = ''	
					if 'dec_cantesptec' in linea_pliego:
						new_line['3'] =linea_pliego['dec_cantesptec']
					else: 
						new_line['3'] = ''	
					if 'cb_unidadmedesptec' in linea_pliego:	
						new_line['4'] = linea_pliego['cb_unidadmedesptec']['text']
					else: 
						new_line['4'] = ''	
					if 'cb_sibysesptec' in linea_pliego:
						new_line['5'] = linea_pliego['cb_sibysesptec']['text']
					else: 
						new_line['5'] = ''	
					if 'txt_detalleesptec' in linea_pliego:
						new_line['6'] = linea_pliego['txt_detalleesptec']
					else: 
						new_line['6'] = ''
					new_line['7'] = '' 
					new_line['8'] = '' 
					new_line['9'] = '' 
					new_line['10'] = '' 
					new_line['11'] = '' 
					new_line['12'] = '' 
					tabla_cuadrocomp_cuadrocomp.append(new_line)					
			msg['gr_datosoferta']['tabla_datosoferta_datosoferta'] = tabla_datosoferta_datosoferta
			msg['gr_cuadrocomp']['tabla_cuadrocomp_cuadrocomp'] = tabla_cuadrocomp_cuadrocomp

		except Exception, e:
				return False, 'ERROR desconocido 2* !!!! ' + str(e)
		

		# please, respect the SLA! 
		return True,msg 
