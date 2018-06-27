from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 

class PluginExample(IPlugin): 
	def execute(self,message): 
		try:	
			#current_app.logger.debug(message['data']) 
			for linea in message['data']['gr_oferente']['tab_oferentes']:
			  if len(linea) !=0:
				if linea['1'] != None and linea['1'] != '':
					if linea['2'] == None or linea['2'] == '':
						return False, "Para la columna Decision los unicos valores permitidos son 'DESESTIMAR' y 'ADMITIR'"
					elif linea['2'].strip().upper() == 'DESESTIMAR':
						print "DESESTIMAR"
					elif linea['2'].strip().upper() == 'ADMITIR':
						print 'ADMITIR'
					else:
						return False, "Para la columna Decision los unicos valores permitidos son 'DESESTIMAR' y 'ADMITIR'"
					
					result, msg = validaCuit(str(linea['1']))
					if not result:
						return result, 'Grupo Oferente: ' + msg 

			if 'gr_impugnacion' in message['data'] and 'ch_impugnacion' in message['data']['gr_impugnacion'] and message['data']['gr_impugnacion']['ch_impugnacion'] == 'SI':
				for linea in message['data']['gr_impugnantes']['tab_impugnantes']:
				  if len(linea) !=0:
					if linea['1'] != None and linea['1'] != '':
						if linea['4'] == None or linea['4'] == '':
							return False, "Para la columna Decision los unicos valores permitidos son 'DESESTIMAR' y 'ADMITIR'"
						elif linea['4'].strip().upper() == 'DESESTIMAR':
							print "DESESTIMAR"
						elif linea['4'].strip().upper() == 'ADMITIR':
							print 'ADMITIR'
						else:
							return False, "Para la columna Decision los unicos valores permitidos son 'DESESTIMAR' y 'ADMITIR'"
					
						result, msg = validaCuit(str(linea['1']))
						if not result:
							return result, 'Grupo Impugnates: '+ msg 

			if 'gr_finalizaciondelprocedimiento' in message['data']:
				if 'ch_declararfracasado' in message['data']['gr_finalizaciondelprocedimiento']: 
					if 'ch_declararsinefecto' in message['data']['gr_finalizaciondelprocedimiento']: 
						if message['data']['gr_finalizaciondelprocedimiento']['ch_declararfracasado'] == 'SI':
							if message['data']['gr_finalizaciondelprocedimiento']['ch_declararsinefecto'] == 'SI':
								return False, 'Error: seleccione una unica opcion en Finalizacion del procedimiento'

		except Exception, e:
			return False, 'Error Desconocido durante la Validacion. ' + str(e)

		return True, 'Exito'


def validaCuit(cuit):				
	# cuit = str(linea['1'])
	if len(cuit) != 11:
		return False, 'CUIT Erroneo'
	else:
		base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
		aux = 0
		for i in xrange(10):
			aux += int(cuit[i]) * base[i]
		aux = 11 - (aux - (int(aux / 11) * 11))
		if aux == 11:
			aux = 0
		if aux == 10:
			aux = 9
		if aux != int(cuit[10]):
			return False, 'CUIT  Erroneo'
	return True, 'OK'		