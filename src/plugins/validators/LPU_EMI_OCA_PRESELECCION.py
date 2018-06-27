# Acto de PRESELECCION
from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import toolbox 
  
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message) 
  		try:
			if len(message['data']['gr_integrantes']['tabla_integrantes_integrantes']) < 3:
				return False, 'Deben ser minimo 3 Integrantes de la Comision Evaluadora.'
			else:
				cont = 0
				for linea in message['data']['gr_integrantes']['tabla_integrantes_integrantes']:
					if not('0' in linea) and cont < 3:
						return False, 'Deben ser minimo 3 Integrantes de la Comision Evaluadora.'
					else:
						cont += 1
					if len(linea) != 0:
						try:
							if not(linea['0'] != None and linea['0'] != ''):
								next
							elif not('1' in linea):
								return False, "Las unicas opciones validas para el  campo Caracter son 'Titular' o 'Suplente'"
							elif linea['1'].strip().upper() != 'TITULAR'.strip().upper() and linea['1'].strip().upper() != 'SUPLENTE'.strip().upper():
								return False, "Las unicas opciones validas para el  campo Caracter son 'Titular' o 'Suplente'" +  str(linea['1'])

						except Exception, e:
							return False," Las unicas opciones validas para el  campo Caracter son 'Titular' o 'Suplente' . " +  str(linea['1'])


			if len(message['data']['gr_preseleccion']['tabla_preseleccion_preseleccion']) < 2:
				return False, '-Deben cargar al menos 1 Oferente.'
			else:
				cont = 0
				for linea in message['data']['gr_preseleccion']['tabla_preseleccion_preseleccion']:
					if linea['1'] != '' and linea['1'] != None:
						cont = cont +1
						if not toolbox.valida_cuit(str(linea['1'])):
							return False, 'CUIT erroneo: ' + str(linea['1'])		
						
						if linea['1'] != None:
							try:
								if linea['5'].strip().upper() != 'DESESTIMAR': # or 
									if linea['5'].strip().upper() != 'ADMITIR':
										return False, "Las unicas opciones validas para el  campo Recoemdaciones son 'Desestimar' o 'Admitir'.. " + linea['5'] 
							except Exception, e:
								return False,"Las unicas opciones validas para el  campo Recoemdaciones son 'Desestimar' o 'Admitir'" 	
				if cont == 0:
					return False, 'Deben cargar al menos 1 Oferente.'

		except Exception, e:
			return False, 'Error durante la validacion: Complete todos los datos dentro del Cuadro Preseleccion: ' + str(e) 



		# please, respect the SLA! 
		return True,'Este es el mensaje de retorno' 
