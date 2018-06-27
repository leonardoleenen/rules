# VIGENTE-ACLARATORIA Pliego 

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import time
import datetime
from datetime import date, timedelta


class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['instance']['tasks']) 
  		# solo se debe poder avanzar cuando fecha de apertura sea <= a fecha de hoy 
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


		return True,'Este es el mensaje de retorno' 
