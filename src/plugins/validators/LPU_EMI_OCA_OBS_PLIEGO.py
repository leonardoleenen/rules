from yapsy.IPlugin import IPlugin 
from flask import current_app 
import datetime
from datetime import date, timedelta
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/lr')
from services import workflow_engine as wf 



class PluginExample(IPlugin): 
	def execute(self,message):
		try:
			msg = [] 
			current_app.logger.debug(message)
			if not ( message["data"]["gp_lim_presenta_obs"]["time_hora_lim"] > message["data"]["gp_presenta_obs"]["timei_horainicio"] or 
						message["data"]["gp_lim_presenta_obs"]["time_hora_lim"] < message["data"]["gp_presenta_obs"]["time_horafin"]):
				msg.append("Hora de 'Limite de presentacion' fuera de rango")
			print msg 
			# fecha limite de observacion >= 10 apartir del primer dia habil posterior a publicacion
			Fecha = message["data"]["gp_lim_presenta_obs"]["date_fecha"] 
			FechaLimite = str(Fecha)[8:10] +  str(Fecha)[5:7] + str(Fecha)[:4]
			
			# Fecha = str(datetime.datetime.now())[8:10] +  str(datetime.datetime.now())[5:7] + str(datetime.datetime.now())[:4]
			# FechaPermitida = (wf.events_nexworkdays(Fecha))
			# FechaPermitida = str(FechaPermitida)[8:10] +  str(FechaPermitida)[5:7] + str(FechaPermitida)[:4]
			
			FechaPermitida = str(datetime.datetime.now())[8:10] +  str(datetime.datetime.now())[5:7] + str(datetime.datetime.now())[:4]
			# FechaPermitida = (wf.events_nexworkdays(Fecha))
			# FechaPermitida = str(FechaPermitida)[8:10] +  str(FechaPermitida)[5:7] + str(FechaPermitida)[:4]


			if datetime.datetime.strptime(FechaPermitida.replace('-',''),'%d%m%Y').date() + timedelta(days=10) >= datetime.datetime.strptime(FechaLimite.replace('-',''),'%d%m%Y').date():
				msg.append('Fecha limite de presentacion de observaciones debe ser mayor o igual a 10 dias corridos. ')  		
		except Exception, ex:
			current_app.logger.debug(str(ex))
			return False, 'Error durante la validacion:: ' + str(ex)
				


  		#############################################
		current_app.logger.debug(msg)
		if len(msg) != 0:  
			return False ,msg 
		else:
  			### antes del return se debe publicar esto !!!
			return True, 'Paso validacion'

