# Solo valido los CUIL
from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import toolbox  
class PluginExample(IPlugin): 
	def execute(self,message): 
		current_app.logger.debug(message['data']['gr_oferentes']) 
  
		if 'gr_declarardes' in message['data']:
			if 'ch_declarardes' in message['data']['gr_declarardes']: 
				if message['data']['gr_declarardes']['ch_declarardes'] == 'SI':
					return True, 'Se declarar decierto hacer circular '


		if not (len(message['data']['gr_oferentes']) != 0):			
			return False, 'Debe Cargar al menos 1 Oferente'
		else:
			for linea in message['data']['gr_oferentes']:
				if not toolbox.valida_cuit(str(linea['txt_cuitoferente'])):
					return False, 'CUIT del Oferente erroneo.'
				if linea['dec_montogtiaoferente'] < 0:
					return False, 'Error: Monto de Garantia Negativo :  ' + str(linea['dec_montogtiaoferente']) 

			error = False
			lineas = message['data']['gr_oferentes']

			for x in range(0,(len(message['data']['gr_oferentes']))-1):
				cuil = message['data']['gr_oferentes'][x]['txt_cuitoferente']
				for y in range(x+1,(len(message['data']['gr_oferentes']))):
					if cuil == lineas[y]['txt_cuitoferente']:
						error = True
						break
				if error:		
					return False , 'Se repite CUIT del Oferente'
		
		if len(message['data']['gr_presacto']) == 0:
			return False, "Debe cargar al menos un 'Presentes en el acto'"			

		# please, respect the SLA! 
		return True,'Este es el mensaje de retorno' 
