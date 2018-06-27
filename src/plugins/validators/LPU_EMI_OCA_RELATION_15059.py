
## Dictamen de Evaluacion  -- Acto de Finalizacion

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		#current_app.logger.debug(message) 
  		#print message['instance']['current_task']['forms'][0]['data']['gr_evaluacioneco']['tabla_preselecion_evaluacioneco']
  		try:
	   		msg = {}
	  		msg['gr_renglonadjudicado'] = {}
	  		tabla_renglonadjudicado_renglonadjudicado = []
	  		for line in message['instance']['current_task']['forms'][0]['data']['gr_evaluacioneco']['tabla_preselecion_evaluacioneco']:
	  			if line['0'] != None and  str(line['13']) == '1' :			
	  				new_line = []
	  				new_line.append(line['0'])
	  				new_line.append(line['6'])
	  				new_line.append(line['5'])
	  				new_line.append(line['7'])
	  				new_line.append(line['8'])
	  				new_line.append(line['9'])
	  				new_line.append(line['11'])
	  				new_line.append(None)
	  				tabla_renglonadjudicado_renglonadjudicado.append(new_line)
	  		msg['gr_renglonadjudicado']['tabla_renglonadjudicado_renglonadjudicado'] = tabla_renglonadjudicado_renglonadjudicado
  			
  			if len(msg['gr_renglonadjudicado']['tabla_renglonadjudicado_renglonadjudicado']) == 0:
				return False, 'No se adjudicado ningun renglon' 
	  			#msg['gr_renglonadjudicado']['tabla_renglonadjudicado_renglonadjudicado'] = [None,None,None,None,None,None,None,None]

  			msg['gr_renglondfse'] = {}
  			tabla_renglondfse_renglondfse = []
			
			for line in message['instance']['current_task']['forms'][0]['data']['gr_rendesiertos']['tabla_rendesiertos_rendesiertos']:
				if line['0'] != None:
					new_line = []
					new_line.append(line['0'])
					new_line.append(line['1'])
					new_line.append('Desierto')	
					tabla_renglondfse_renglondfse.append(new_line)

			for line in message['instance']['current_task']['forms'][0]['data']['gr_renfracasado']['tabla_renfracasado_renfracasado']:
				if line['0'] != None:
					new_line = []
					new_line.append(line['0'])
					new_line.append(line['1'])
					new_line.append('Fracasado')	
					tabla_renglondfse_renglondfse.append(new_line)
			
			if len(tabla_renglondfse_renglondfse) == 0:
				new_line = [None, None, None]		
				tabla_renglondfse_renglondfse.append(new_line)
			
			msg['gr_renglondfse']['tabla_renglondfse_renglondfse'] = tabla_renglondfse_renglondfse 			

			msg['gr_ofertadesestimadas'] = {}
			msg['gr_ofertadesestimadas']['tabla_ofertadesestimadas_ofertadesestimadas'] = message['instance']['current_task']['forms'][0]['data']['gr_Ofertasdesestimadas']['sin_titulo15']


  		except Exception, e:
  			return False, 'Error durante la validacion: ' + str(e)


		# please, respect the SLA! 
		return True,msg 
