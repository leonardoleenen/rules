from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
import datetime
from datetime import date, timedelta
sys.path.append(current_app.config["APP_PATH"]+ '/src/lr')
from services import workflow_engine as wf 
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo
from utils import toolbox 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
		try:
			#################################################################################3
	  		msg = []
			suborganization = message['suborganization']
			#################################################################################3
			# lim pres muestra 
			if 'gr_limpresmues' in message['data']:
				date_fechalimpresmuestra = datetime.datetime.strptime(message['data']['gr_limpresmues']['date_fechalimpresmues'][:10].replace('-', ''), '%Y%m%d').date() 
			else:
				date_fechalimpresmuestra = None
			# lim de retiro pliego
			date_fechalimretadvis = datetime.datetime.strptime(message['data']['gr_limretadvis']['date_fechalimretadvis'][:10].replace('-', ''), '%Y%m%d').date() 
			# lim de pres oferta 
			date_fechalimpresofer = datetime.datetime.strptime(message['data']['gr_limpresofer']['date_fechalimpresofer'][:10].replace('-', ''), '%Y%m%d').date() 
			# Acto de Apertura	
			date_fechaaper = datetime.datetime.strptime(message['data']['gr_aper']['date_fechaaper'][:10].replace('-', ''), '%Y%m%d').date()		  				
			# 1* dia  publicacion
			date_primerdiapbo = datetime.datetime.strptime(message['data']['gr_pbo']['date_primerdiapbo'][:10].replace('-', ''), '%Y%m%d').date()					
			# 2* dia publicacion
			date_segundodiapbo = datetime.datetime.strptime(message['data']['gr_pbo']['date_segundodiapbo'][:10].replace('-', ''), '%Y%m%d').date()				
			


			##################################################################################3
			if len(message['data']['prov_manual']) < 5:
				return False, 'Debe cargar al menos 5 Proveedores.'
			#################################################################################3
			for linea in message['data']['prov_manual']:
				if not toolbox.valida_cuit(str(linea['prov_cuit'])):
					return False, 'CUIT del Proveedor Erroneo'
			#################################################################################3
			if len(message['data']['gp_pliego_camara']) < 1:
				return False, 'Debe cargar al menos 1 Camara.'
			#################################################################################3
			date1 = message['data']['gr_pbo']['date_primerdiapbo']
			date1 = str(date1)[8:10] +  str(date1)[5:7] + str(date1)[:4]
			if datetime.datetime.strptime(date1.replace('-',''),'%d%m%Y').date() <= datetime.date.today() + timedelta(days=1):
				return False, 'Error: Primer dia de publicacion.'
			if not wf.events_workdays(date_primerdiapbo,suborganization):
				return False, 'Primer dia de Publicacion debe ser dia habil'
			#################################################################################3
			date2 = message['data']['gr_pbo']['date_segundodiapbo']
			date2 = str(date2)[8:10] +  str(date2)[5:7] + str(date2)[:4]
			if message['data']['gr_pbo']['date_primerdiapbo'] >= message['data']['gr_pbo']['date_segundodiapbo']:
				return False, 'Error: 2* dia de publicaciones debe ser primer dia habil imediato al 1* dia de publicacion.'
			if not wf.events_workdays(date_segundodiapbo,suborganization):
				return False, 'Segundo dia de Publicacion debe ser dia habil'
			##################################################################################3
			if message['data']['gr_aper']['date_fechaaper'] < message['data']['gr_limpresofer']['date_fechalimpresofer']:
				return False, "Error: Fecha 'Limite de presentacion' debe ser menor a fecha de 'Acto de Apertura' "
			if message['data']['gr_aper']['date_fechaaper'] < message['data']['gr_limretadvis']['date_fechalimretadvis']:
				return False, "Error: Fecha 'Limite de Retiro de Pliego' debe ser menor a fecha de 'Acto de Apertura' "
			if message['data']['gr_aper']['date_fechaaper'] < message['data']['gr_limpresofer']['date_fechalimpresofer']:
				return False, "Error: Fecha 'Limite de presentacion' debe ser menor a fecha de 'Acto de Apertura' "
			#################################################################################3
			if not wf.events_workdays(date_fechalimpresofer,suborganization):
				return False, 'Fecha de Limite de Presentacion de Muestra debe ser dia habil'
			if not wf.events_workdays(date_fechalimretadvis,suborganization):
				return False, 'Fecha de Limite de Retiro de Pliego debe ser dia habil'
			if not wf.events_workdays(date_fechalimpresofer,suborganization):
				return False, 'Fecha de Limite de Presentacion de Oferta debe ser dia habil'
			if not wf.events_workdays(date_fechaaper,suborganization):
				return False, 'Fecha de Apertura debe ser dia habil'

			# if date_fechaaper <= (date_primerdiapbo + timedelta(days=40)):
			# 	return False, "Fecha de apertura debe superar 40 dias corridos desde la fecha de publicacion"


			"""
				Plazo minimo de publicacion 40 dias corridos hasta el evento que ocurra primero a considerar entre:
				- Fecha limite de presentacion de muestras.
				- Fecha limite de retiro de pliego.
				- Fecha limite de presentacion de ofertas.
				Si el primero de estos coincide con la fecha de apertura, entonces se debe sumar un dia.
			"""
			# las 3 fechas relevantes
			
			fechas = [date_fechalimretadvis, date_fechalimpresofer]
			# if date_fechalimpresmuestra != None:
			# 	fechas.append(date_fechalimpresmuestra)

			print fechas
			# ordenadas 
			fechas.sort()

			print fechas

			if fechas[0] == date_segundodiapbo: # Si el primero de estos coincide con la fecha de apertura, entonces se debe sumar un dia
				delta_dias = 41
			else:
				delta_dias = 40

			if (date_segundodiapbo + timedelta(days=delta_dias)) >= fechas[0]: # si segundo dia de publicacion + delta_dias es >= a primer fecha relevante = ERROR
				return False, "Error no se cumplen plazos legales en una de las fechas 'Muestra, Pliego, Oferta'"  



			#################################################################################3
			# actualiso el numero de instancia 
			if 'gr_numero_proc' in message['data'] and 'num' in message['data']['gr_numero_proc']:
				repo_client = repo.get_instance("workflow")
				instance = repo_client.get_by_id("instances", message['instance_id'])
				instance['header']['data_header']['datos_procedimientoA']['num_numero'] = message['data']['gr_numero_proc']['num']
				repo_client.update("instances", message['instance_id'], instance)
			#################################################################################3
		except Exception, e:
			return False, 'Error Desconocido durante la Validacion. ' + str(e)
			current_app.logger.debug('Error Desconocido durante la Validacion. ' + str(e))

		return True, 'Exito'


