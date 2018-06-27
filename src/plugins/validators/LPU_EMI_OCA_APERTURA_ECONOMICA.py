
# LPU_EMI_OCA_APERTURA_ECONOMICA

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import toolbox 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['data']) 
		if 'gr_oferentes' in message['data']:
			if len(message['data']['gr_oferentes']) == 0:
				return False, 'Debe cargar al menos 1 oferente'
			#################################################################################3
			for linea in message['data']['gr_oferentes']:
				if not toolbox.valida_cuit(str(linea['txt_cuitoferente'])):
					return False, 'CUIT del Oferente erroneo.'
				if linea['dec_montototaloferente'] < 0:
					return False, 'Error: Monto de oferta negativo ' + str(linea['dec_montototaloferente'])
			#################################################################################3
		else: # este mensaje es por si no existe el grupo 
			return False, 'Debe cargar al menos 1 oferente'

		if 'gr_presacto' in message['data']:
			if len(message['data']['gr_presacto']) == 0:
				return False, 'Debe cargar al menos 1 Presente'
		else:
			return False, 'Debe cargar al menos 1 Presente'



		return True,'Este es el mensaje de retorno' 
