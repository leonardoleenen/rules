from yapsy.IPlugin import IPlugin
from flask import current_app
import json 
import sys
sys.path.append(current_app.config["APP_PATH"]+ '/src/lr')
from services import workflow_engine as wf
from services import trigger_rules as tr
sys.path.append(current_app.config["APP_PATH"]+ '/src/utils')
from utils import repo


class PluginEngine(IPlugin):
	def execute(self,message):
		#current_app.logger.debug(message)
		trigger_name = message['header']['data_header']['gr_datos_disparador']['txt_disparador_de_regla']
		trigger_major = message['header']['data_header']['gr_datos_disparador']['int_major']
		trigger_minor = message['header']['data_header']['gr_datos_disparador']['int_minor']
		trigger_release = message['header']['data_header']['gr_datos_disparador']['int_release']
		trigger = tr.get_by_name_and_version(trigger_name, trigger_major, trigger_minor, trigger_release)
		if trigger is None:
			return False, "Lo sentimos pero no se encontro un trigger con el nombre especificado"	
		tr.publish(trigger['id'])
		return True, "Exito al publicar el Disparador" 