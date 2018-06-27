from flask import Blueprint, Flask, current_app, jsonify, render_template, \
    request, url_for, redirect, flash, session
from flask_cors import cross_origin
import json
from yapsy.PluginManager import PluginManager
from yapsy.IPlugin import IPlugin 
from logic import validator
import os
from utils import toolbox

import logging
import glob
import StringIO 
import ConfigParser


def remove(name):
	os.remove(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".yapsy-plugin")
	os.remove(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".py")

def get(name):

	'''
	pluginManager = PluginManager()
	pluginManager.setPluginPlaces([ current_app.config["PLUGINS_PATH"] + os.sep + "validators"])
	pluginManager.collectPlugins()

	result = {"plugins":[]}

	for pluginInfo in pluginManager.getAllPlugins():
		if pluginInfo.name == name:
			pluginManager.activatePluginByName(pluginInfo.name)
    		result = {"author":pluginInfo.author, "name": pluginInfo.name, "version":  str(pluginInfo.version)}

	plugin_info_file = open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".yapsy-plugin", "r")
	plugin_file = open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".py", "r")
	result["file_info"] = str(plugin_info_file.read())
	result["data"] = str(plugin_file.read())
	
	return result
	

	'''
	config = ConfigParser.RawConfigParser()
	config.read(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".yapsy-plugin")

	result={}
	result["author"]= config.get("Documentation","Author")
	result["name"]=config.get("Core","Name")
	result["version"]=config.get("Documentation","Version")
	

	f= open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".py")
	result["data"]=f.read()
	f.close()
	f= open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + name.replace(" ", "") + ".yapsy-plugin")
	result["file_info"] = f.read()
	f.close()
	return result
	


def get_all():
	
	result = {"plugins":[]}
	files=glob.glob(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + "*.yapsy-plugin")



	config = ConfigParser.RawConfigParser()

	for f in files:
		config.read(f)
		result["plugins"].append({"author":config.get("Documentation","Author"), 
			"name": config.get("Core","Name"), 
			"version":  config.get("Documentation","Version"), 
			"description": config.get("Documentation","Description")})

	return toolbox.json_decoder(result)





def save(message):
	pluginManager = PluginManager()
	pluginManager.setPluginPlaces([ current_app.config["PLUGINS_PATH"] + os.sep + "validators"])
	pluginManager.collectPlugins()

	for pluginInfo in pluginManager.getAllPlugins():
		pluginManager.activatePluginByName(pluginInfo.name)

	pluginInfo = pluginManager.getPluginByName(message['name'])

	plugin_info_file = open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + str(message["name"]).replace(" ", "") + ".yapsy-plugin", "w")
	plugin_file = open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + str(message["name"]).replace(" ", "") + ".py", "w")
	plugin_info_file.write(str(message["file_info"]).decode("base64", errors="strict"))
	plugin_file.write(str(message["data"]).decode("base64"))

	plugin_info_file.close()
	plugin_file.close()


def create(message):
	pluginManager = PluginManager()
	pluginManager.setPluginPlaces([ current_app.config["PLUGINS_PATH"] + os.sep + "validators"])
	pluginManager.collectPlugins()

	for pluginInfo in pluginManager.getAllPlugins():
		pluginManager.activatePluginByName(pluginInfo.name)

	pluginInfo = pluginManager.getPluginByName(message['name'])

	if pluginInfo != None:
		raise "Lo sentimos pero el nombre del plugin que ya esta siendo utilizado"

	plugin_info_file = open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + str(message["name"]) + ".yapsy-plugin", "w")
	plugin_file = open(current_app.config["PLUGINS_PATH"] + os.sep + "validators" + os.sep + str(message["name"]) + ".py", "w")
	plugin_info_file.write(str(message["file_info"]).decode("base64", errors="strict")) 
	plugin_file.write(str(message["data"]).decode("base64")) 
	plugin_info_file.write(str('Organization = ' + current_app.config['ORGANIZATION_CONTEXT_ID'] + ' - ' + current_app.config['ORGANIZATION_CONTEXT_DESC']))
	plugin_info_file.close()
	plugin_file.close() 


def validate(msg):
	result, msg = validator.execute([current_app.config["PLUGINS_PATH"] + os.sep + "validators"], msg["name"], msg["payload"])
       
def execute(plugin_name,msg):
	result, msg = validator.execute([current_app.config["PLUGINS_PATH"] + os.sep + "validators"], plugin_name, msg)
	return result,msg

def validate_python_code(source):
	pass
