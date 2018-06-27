
#  cuadro Comparativo - Dictamen Evaluacion

from yapsy.IPlugin import IPlugin 
from flask import current_app 
import json 
 
class PluginExample(IPlugin): 
	def execute(self,message): 
		# current_app.logger.debug(message['instance']['current_task'])
		msg = {}
		try:
			for tasks in range(0,(len(message['instance']['tasks']))):
	  			if len(message['instance']['tasks'][tasks]['forms']) != 0:
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_PLIEGO':
			  			pliego = message['instance']['tasks'][tasks]['forms'][0]['data']
			  		if message['instance']['tasks'][tasks]['forms'][0]['spec']['header']['code'] == 'LPU_EMI_OCA_DICTAMEN_PRESELECCION':
			  			dictamen = message['instance']['tasks'][tasks]['forms'][0]['data']

			cuadro = message['instance']['current_task']['forms'][0]['data']
							
			msg['gr_integrantes'] = {}
			msg['gr_integrantes']['tabla_integrantes_integrantes'] = dictamen['gr_integrantes']['tabla_integrantes_integrantes']
			print '2222222'
			print message['instance']['current_task']['forms'][0]['data']['gr_unicooferente']['ch_unicooferente_unicooferente']
			print '2222222'
			if message['instance']['current_task']['forms'][0]['data']['gr_unicooferente']['ch_unicooferente_unicooferente'] == 'NO':
				tabla_rendesiertos_rendesiertos = []
				tabla_preselecion_evaluacioneco = []
				print '2222222'
				for linea_pliego in pliego['gr_esptec']:
					print linea_pliego
					hay_ofertas = False
					for linea_cuadro in cuadro['gr_cuadrocomp']['tabla_cuadrocomp_cuadrocomp']:
						print linea_cuadro
						if linea_pliego['int_renglonesptec'] == linea_cuadro['2']:
							hay_ofertas = True 
							new_lime = {}
							new_lime ={
										'0':linea_cuadro['2'],
										'1':linea_cuadro['3'],
										'2':linea_cuadro['4'],
										'3':linea_cuadro['5'],
										'4':linea_cuadro['6'],
										'5':linea_cuadro['0'],
										'6':linea_cuadro['1'],
										'7':linea_cuadro['7'],
										'8':linea_cuadro['8'],
										'9':linea_cuadro['9'],
										'10':linea_cuadro['10'],
										'11':linea_cuadro['11'],
										'12':linea_cuadro['12'],
										'13':'',
										'14':'',
										'15':''
										}
							tabla_preselecion_evaluacioneco.append(new_lime)
					if not(hay_ofertas):
						new_lime = {}
						new_lime = {'0':linea_pliego['int_renglonesptec'], '1': ''}
						tabla_rendesiertos_rendesiertos.append(new_lime)

				msg['gr_rendesiertos'] = {}
				if tabla_rendesiertos_rendesiertos != []:
					msg['gr_rendesiertos']['tabla_rendesiertos_rendesiertos'] = tabla_rendesiertos_rendesiertos
				
				else:
					none = {}
					none = {'0':'', '1':'' }
					tabla_rendesiertos_rendesiertos.append(none)
					msg['gr_rendesiertos']['tabla_rendesiertos_rendesiertos'] = tabla_rendesiertos_rendesiertos 
				msg['gr_evaluacioneco'] = {}	
				if tabla_preselecion_evaluacioneco != []:
					msg['gr_evaluacioneco']['tabla_preselecion_evaluacioneco'] = tabla_preselecion_evaluacioneco
				else:
					msg['gr_evaluacioneco']['tabla_preselecion_evaluacioneco'] = {'0':'','1':'','2':'','3':'','4':'','5':'','6':'','7':'','8':'','9':'','10':'','11':'','12':'','13':'','14':'','15':'','16':''}
				# print msg
		except Exception, e:
			return False, 'Error durante la validacion: ' + str(e)
  

		# please, respect the SLA! 

		print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@########"
		print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@########"
		print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@########"
		print msg
		return True, msg 
