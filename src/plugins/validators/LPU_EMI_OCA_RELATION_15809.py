
# Acto Finalizacio - 2* Lamado

# Trae datos del Ultimo Pliego 
# valida que acto no este declarado como decierto
# valida que no haya mas de 2 "Segundo LLamado"


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message) 
  		try:
			tot = 0	
			data =''
			finalizar = False
			if 'gr_finalizaciondelprocedimiento' in message['instance']['current_task']['forms'][0]['data']:
	  			if 'ch_declararfracasado' in message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']:
	  				if message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']['ch_declararfracasado'] == 'SI':
	  					pass
	  				else:
		  				return False, 'Error: El acto no fue Declarodo como Fracasado 1'		  		
	  			
	  		else:
  				return False, 'Error: El acto no fue Declarodo como Fracasado'		

	  		if message['instance']['current_task']['forms'][0]['data']['gr_finalizaciondelprocedimiento']['ch_declararfracasado'] == 'SI':
		  		for tasks in range(0,(len(message['instance']['tasks']))):
		  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
				  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
				  			data = message['instance']['tasks'][tasks]['forms'][0]['data']

						if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_SEGUNDO_LLAMADO':
							tot += 1
				print tot
				if tot >= 2:
					return False, 'No se permite realizar mas de 2 segundos llamados '  

				
				return True, data 
  			else:
  				return False, 'Error: El acto no fue Declarodo como Fracasado o Dessierto'
  		except Exception, e:
			return False,'Error en la validacion:: ' + str(e)  
