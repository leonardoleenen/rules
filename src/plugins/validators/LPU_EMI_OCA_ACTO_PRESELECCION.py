



#### obsoleto *** el que se usa es LPU-EMI-OCA-ACTO-PRESELECT.PY


from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		try:	
			#current_app.logger.debug(message['data']) 
	  		
	  		for linea in message['data']['gr_oferente']['tab_oferentes']:
	  			if linea[3].strip().upper() != 'DESESTIMAR' or linea[3].strip().upper() != 'ADMITIR':
	  				msg.append("Para la columna Decision los unicos valores permitidos son 'DESESTIMAR' y 'ADMITIR'")
		except Exception, e:
			msg.append('Error Desconocido durante la Validacion. ' + str(e))

		# please, respect the SLA! 
		if len(msg) != 0:
			return False,msg 
		else:
			return True, 'Exito'