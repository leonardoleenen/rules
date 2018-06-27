

# Pliego - Convocatoria


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
import time
import datetime


class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message['instance']['tasks']) 
  		# solo se debe poder avanzar cuando fecha de apertura sea <= a fecha de hoy 
  		try:
	  		
	  		data={}
	  		data['gr_fechaapertec'] = {}
	  		for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_CONVOCATORIA':
						convocatoria = message['instance']['tasks'][tasks]['forms'][0]['data']			  			


			if convocatoria['gr_aper']['date_fechaaper'] <= str(datetime.datetime.now()):
	  			data['gr_fechaapertec']['date_fechaapertec'] = convocatoria['gr_aper']['date_fechaaper']
	  			data['gr_fechaapertec']['time_horaapertec'] = convocatoria['gr_aper']['time_horaaper']
				return True, data  
			else:
				###   para pruebas !!!! 
	  			data['gr_fechaapertec']['date_fechaapertec'] = convocatoria['gr_aper']['date_fechaaper']
	  			data['gr_fechaapertec']['time_horaapertec'] = convocatoria['gr_aper']['time_horaaper']
				return True, data
				### Fin pruebas   
				#return False, 'Fecha de apertura programada para ' + convocatoria['gr_aper']['date_fechaaper'][:10]


  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  
