from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
  def execute(self,message): 
	try:
		#current_app.logger.debug(message['data']) 
		msg = []
		if 'gr_esptec' in message['data']: 
			if len(message['data']['gr_esptec']) == 0:
				msg.append('Debe cargar al menos 1 linea de especificacion tecnica.')
			else: # Control de numeracion de la grilla 
				error = False
				lineas = message['data']['gr_esptec']
				for x in range(0, (len(message['data']['gr_esptec']))-1): # for por cada linea 
					nroLin = lineas[x]['int_renglonesptec']
					for y in range(x+1, (len(message['data']['gr_esptec']))): # comparo nro de linea con todas las siguentes 
						if nroLin == lineas[y]['int_renglonesptec']:
							error = True
							break
					if error: # corto el recorrido en caso de que aya dos renglones con el mismo nro de linea
						break	
				if error: msg.append('Numeracion de los renglones de Especificaciones Tecnicas erronea')
		else:
			msg.append('Debe cargar al menos 1 linea de Especificaciones Tecnicas.')
		
		for lineas in message['data']['gr_esptec']:  # valido que no haya valores negativos en la especificacion
			if lineas['int_renglonesptec'] < 0:
				return False, 'Error: Numeracion de renglones negativa: ' + str(lineas['int_renglonesptec']) 
			if lineas['dec_cantesptec'] < 0:
				return False, 'Error: Cantidad  Negativos: ' + str(lineas['dec_cantesptec']) 


		try:	
			if 'cb_ofpar_ofpar' in message['data']['gr_ofpar']:	
				if message['data']['gr_ofpar']['cb_ofpar_ofpar']['id'] == "2" and (
					message['data']['gr_ofpar']['cb_ofpar_porcen'] > 35 or message['data']['gr_ofpar']['cb_ofpar_porcen'] < 20):
						msg.append("Porcentaje de 'Ofertas Parciales' fuera de Rango, porcentaje permitido entre 20 y 35%")
		except Exception, e:
			msg.append('Error al validar Ofertas Parciales, verifique los campos.')
	##---------------------------------------------
		


		if 'gr_lugfact' in message['data']:
			if 'txt_horainiciolugfact' in message['data']['gr_lugfact']:
				if 'txt_horafinlugfact' in message['data']['gr_lugfact']:
					if message['data']['gr_lugfact']['txt_horainiciolugfact'] != message['data']['gr_lugfact']['txt_horafinlugfact']:
						if int(message['data']['gr_lugfact']['txt_horainiciolugfact'][:2]) > int(message['data']['gr_lugfact']['txt_horafinlugfact'][:2]):
								return False, 'Error: Lungar de facturacion: Horario'
						elif int(message['data']['gr_lugfact']['txt_horainiciolugfact'][:2]) == int(message['data']['gr_lugfact']['txt_horafinlugfact'][:2]):
							if int(message['data']['gr_lugfact']['txt_horainiciolugfact'][3:]) > int(message['data']['gr_lugfact']['txt_horafinlugfact'][3:]):
								return False, 'Error: Lungar de facturacion: Horario'


		if len(msg) != 0:  
			return False ,msg 
		else:
			return True, 'Paso validacion'
	except Exception, e:
		return False, 'Se produjo error durante la validacion....'
