from flask import current_app
import json
from yapsy.PluginManager import PluginManager
import logging


def execute(route, plugin, payload):


    
    logging.basicConfig()

    # Build the manager
    simplePluginManager = PluginManager()
    # Tell it the default place(s) where to find plugins
    print route
    simplePluginManager.setPluginPlaces(route)
    # Load all plugins
    simplePluginManager.collectPlugins()



    
    # Activate all loaded plugins
    for pluginInfo in simplePluginManager.getAllPlugins():
        simplePluginManager.activatePluginByName(pluginInfo.name)

    # for pluginInfo in simplePluginManager.getAllPlugins():
    #    var1,var2 = pluginInfo.plugin_object.execute()
    simplePluginManager.activatePluginByName(plugin)
    pluginInfo = simplePluginManager.getPluginByName(plugin)

    if pluginInfo is None:
        current_app.logger.error("Lo sentimos pero no se ha podido cargar el plugin o el mismo no se ha encontrado")
        raise Exception("No se ha podido cargar el plugin")
    return  pluginInfo.plugin_object.execute(payload)

   



