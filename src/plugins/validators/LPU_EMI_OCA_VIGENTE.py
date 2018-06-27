
# Vigente - Pliego 


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo 

import time
import datetime
from datetime import date, timedelta

 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['instance']['current_task']['forms']) 
		# gr 6 - 7 vista y limite de vista 
		# gr 8 - 9 lim vista patron   
		# gr 10 - 11 pres muestra y lim pres muestra 
  		
  		try:
	  		
	  		fecha = []
	  		# data['gr_fechaapertec'] = {}
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
						convocatoria = message['instance']['tasks'][tasks]['forms'][0]['data']			  			

			if 'date_fechalimpresofer' in convocatoria['gr_limpresofer']: 
				# lim pres muestra 	date_fechalimpresofer = 
				fecha.append(datetime.datetime.strptime(convocatoria['gr_limpresofer']['date_fechalimpresofer'][:10].replace('-', ''), '%Y%m%d').date() )
			if 'date_fechalimretadvis' in convocatoria['gr_limretadvis']:
				# lim de retiro pliego  date_fechalimretadvis = 
				fecha.append(datetime.datetime.strptime(convocatoria['gr_limretadvis']['date_fechalimretadvis'][:10].replace('-', ''), '%Y%m%d').date() )
			if 'date_fechalimpresofer' in convocatoria['gr_limpresofer']: 
				# lim de pres oferta  date_fechalimpresofer =
				fecha.append(datetime.datetime.strptime(convocatoria['gr_limpresofer']['date_fechalimpresofer'][:10].replace('-', ''), '%Y%m%d').date() )
			# Acto de Apertura	date_fechaaper = 
			fecha.append(datetime.datetime.strptime(convocatoria['gr_aper']['date_fechaaper'][:10].replace('-', ''), '%Y%m%d').date())		  				
 	
 			fecha.sort()

 			if fecha[0] < (datetime.datetime.now().date() + timedelta(days=1)):
 				return False, 'Fecha limite permitida para realizar esta accion: ' + fecha[0].strftime("%Y-%m-%d")


  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  



  		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
			  			pliego = message['instance']['tasks'][tasks]['forms'][0]['data']
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  

		try:
			gr_visita = False
			gr_vista_patron = False
			gr_presmues = False

			for linea in pliego:
				if 'ch_presmuesesptec' in linea and linea['ch_realizarvisesptec'] == 'SI':
					gr_visita = True
					# print 'gr_visita = True'
				if 'ch_realizarvisesptec' in linea and linea['ch_vermuestraesptec'] == 'SI':
					gr_vista_patron = True
					# print 'gr_vista_patron = True'
				if 'ch_realizarvisesptec' in linea and linea['ch_presmuesesptec'] == 'SI':
					gr_presmues = True
					# print 'gr_presmues = True'

			# print '---------------------------------------------------------------------'
			# print '---------------------------------------------------------------------'
			# print '---------------------------------------------------------------------'
			# print '---------------------------------------------------------------------'
			for task in message['spec']['tasks']:
				if len(task['forms']) != 0 and task['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
					# print 'LPU_EMI_OCA_CONVOCATORIA'
					for grupo in task['forms'][0]['spec']['payload']:
						if 'gr_visita' in grupo:
							# print 'gr_visita false '
							grupo['gr_visita']['properties']['showby'] = False
							if gr_visita:
								# print 'gr_visita true'
								grupo['gr_visita']['properties']['showby'] = True
						if 'gr_limvisita' in grupo:
							# print 'gr_limvisita false'
							grupo['gr_limvisita']['properties']['showby']	= False
							if gr_visita:
								# print 'gr_limvisita true'
								grupo['gr_limvisita']['properties']['showby']	= True
						if 'gr_vista_patron' in grupo:
							# print 'gr_vista_patron false'
							grupo['gr_vista_patron']['properties']['showby'] = False
							if gr_vista_patron:
								# print 'gr_vista_patron true'
								grupo['gr_vista_patron']['properties']['showby'] = True
						if 'gr_limvista_patron' in grupo:
							grupo['gr_limvista_patron']['properties']['showby']	= False				
							# print 'gr_limvista_patron false'
							if gr_vista_patron:
								# print 'gr_limvista_patron false'
								grupo['gr_limvista_patron']['properties']['showby']	= True				
						if 'gr_presmues' in grupo:
							grupo['gr_presmues']['properties']['showby'] = False
							# print 'gr_presmues false' 
							if gr_presmues:
								# print 'gr_presmues true' 
								grupo['gr_presmues']['properties']['showby'] = True
						if 'gr_limpresmues' in grupo:
							grupo['gr_limpresmues']['properties']['showby']	= False				
							# print 'gr_limpresmues false'
							if gr_presmues:
								# print 'gr_limpresmues true'
								grupo['gr_limpresmues']['properties']['showby'] = True				
			
			repo_client = repo.get_instance("workflow")
			repo_client.update("instances", message['id'], message)

		except Exception, e:
			return False, 'Se produjo error durante la validacion de grupos - ' + str(e)

  		try:
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
			  			# print message['instance']['tasks'][tasks]['forms'][0]['data']['gr_aper']
						data = message['instance']['tasks'][tasks]['forms'][0]['data']
			return True, data
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  




