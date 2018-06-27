
# Acto Finalizacion -- OCA

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
import datetime
import time
from datetime import date, timedelta
sys.path.append(current_app.config["APP_PATH"]+ '/src/lr')
from services import workflow_engine as wf 
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo as repo
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message)
		reload(sys)
		sys.setdefaultencoding("utf-8")		
		try:
			dictamen = []
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_DICTAMEN_ECONOMICO':
			  			if 'gr_evaluacioneco' in message['instance']['tasks'][tasks]['forms'][0]['data']:
			  				dictamen = message['instance']['tasks'][tasks]['forms'][0]['data']['gr_evaluacioneco']['tabla_preselecion_evaluacioneco']
					if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
				  		pliego = message['instance']['tasks'][tasks]['forms'][0]['data']
			if dictamen == []:
				return False, 'No es posible Generar Ordenes de compra por falta de datos en Evaluacion economicas'

		except Exception, e:
			return False, 'Error: No en instancias anteriores no se completaron los siguentes datos: ' + str(e)
 		
 		unique_values= list(set(map(lambda x: x['2'], message['instance']['current_task']['forms'][0]['data']['gr_renglonadjudicado']['tabla_renglonadjudicado_renglonadjudicado'])))
 		unique_values.remove(None)

 		for cuit in unique_values:
			msg = {}
			msg['datos_prov'] = {}
			msg['gr_detalle'] = {}
			msg['gr_datosejecu'] = {}
			msg['gr_datosOC'] = {}
			msg['gr_datosOC']['OC_numero'] = int(str(time.time()).replace('.',''))
			msg['gr_totaladju'] = {}
			tabla_detalle = []
			total = 0 
 			for line in message['instance']['current_task']['forms'][0]['data']['gr_renglonadjudicado']['tabla_renglonadjudicado_renglonadjudicado']:
 				if cuit == line['2']:
 					for line_dictamen in dictamen:
 						if line['0'] == line_dictamen['0']:
 							renglon_dictamen = line_dictamen
 					msg['datos_prov']['cuit'] = int(line['2'])
 					msg['datos_prov']['prov_razon'] = line['1']
 					new_line = []
 					new_line.append(line['0']) # renglon 
 					new_line.append(line['4']) # cantidad 
 					new_line.append(renglon_dictamen['2'])
 					new_line.append(line['2']) # unidad de medida 
 					new_line.append(line['3']) # codigo sibis 
 					new_line.append(line['7']) # moneda ?  										
 					new_line.append(line['5']) # precio unitario 7
 					new_line.append(renglon_dictamen['10']) # iva  8
 					new_line.append(line['6']) # precio total 9
#####################################33 					
 					total += float(line[6].replace(',','.'))
 					tabla_detalle.append(new_line)
	 		msg['gr_detalle']['tabla_detalle'] = tabla_detalle
	 		msg['gr_totaladju']['sin_titulo21'] = total
			msg['gr_totaladju']['txt_totalenletras'] = total
			## ????????????????????/
			# agregar validacion de que si no existe lugar de entrega para los renglones 
			if 'gr_lugarentrepres' in pliego:
				if len(pliego['gr_lugarentrepres']) > 0:
					msg['gr_datosejecu']['txt_entrega'] = pliego['gr_lugarentrepres'][0]['cb_paislugarentrepres']['text']+ ', '+ pliego['gr_lugarentrepres'][0]['cb_provincialugarentrepres']['text'] + ', ' + pliego['gr_lugarentrepres'][0]['cb_partidolugarentrepres']['text'] + ', ' + pliego['gr_lugarentrepres'][0]['cb_localidadlugarentrepres']['text'] + ', ' + pliego['gr_lugarentrepres'][0]['txt_domiciliolugarentrepres']
			##  _??????????????????
			if pliego['gr_datosejec']['cb_entrega_datosejec']['id'] == '3': 
				msg['gr_datosejecu']['txt_plazo'] = str(pliego['gr_plazoentrepres'][0]['int_plazoplazoentrepres'])+' '+ str(pliego['gr_plazoentrepres'][0]['cb_tiempoplazoentrepres']['text']) 
			elif pliego['gr_datosejec']['cb_entrega_datosejec']['id'] == '2':
				msg['gr_datosejecu']['txt_plazo'] = str(pliego['gr_plazoentrepres'][0]['int_plazoplazoentrepres'])+' '+ str(pliego['gr_plazoentrepres'][0]['cb_tiempoplazoentrepres']['text'])+' '+ str(pliego['gr_plazoentrepres'][0]['txt_comiezoplazoentrepres']) 
			elif pliego['gr_datosejec']['cb_entrega_datosejec']['id'] == '1':
				msg['gr_datosejecu']['txt_plazo'] = 'No se ha especificado 1'
 			else:	
				msg['gr_datosejecu']['txt_plazo'] = 'No se ha especificado'
			header = {}
			header['header'] = {}
			header['header']["name"] = 'OC-' + msg['datos_prov']['prov_razon'] +' - ' + message['header']['name']
			header['header']["owner"] = 'SISTEM'
			header['header']["flow"] = {}
			header['header']["flow"]['id'] = "SP_OCA"
			header['header']["flow"]['idPadre'] = "0"
			header['header']["flow"]['service_id'] = "specs"
			header['header']["flow"]['text'] = "SP_OCA"
			header['header']["is_subprocess"] = True
			header['header']["main_process_id"] = message['id']
			header['header']["main_process_header"] = message['header']
			try:
				new_instance =  wf.create_instance_back('SP_OCA', header)				
				repo_client = repo.get_instance("workflow")
				instance = repo_client.get_by_id("instances", new_instance[1])		
				instance['instance']['current_task']['forms'][0]['data'] = msg
				repo_client.update("instances", instance['id'], instance)				
			except Exception, ex:
				return False, 'Error durante la generacion de SP, consulte con el administrador :: ' + str(ex)

		# please, respect the SLA! 
		return True, 'Este es el mensaje de retorno' 
