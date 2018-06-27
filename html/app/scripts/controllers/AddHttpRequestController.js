app.controller('AddHttpRequestController', ['$mdDialog', 'parentScope', 'obj', 'models', '$mdToast',
    function($mdDialog, parentScope, obj, models, $mdToast) {

        var m = this;
        if(obj){
            m.request = angular.copy(obj);
            m.editing=true
        }else{
            m.request = {
                "url": "",//fqdn
                "entityId":"",
            }
            m.editing=false    
        }
        m.entities = parentScope.entities;

        m.save = function(){
            if(m.request.url == "" || m.request.url == undefined){
                $mdToast.show($mdToast.simple().content("Debe escribir una URL para el servicio.") .position("top right") .hideDelay(3000) );
                return;
            }
            if(m.request.entityId == "" || m.request.entityId == undefined){
                $mdToast.show($mdToast.simple().content("Debe seleccionar una ENTIDAD para el servicio.") .position("top right") .hideDelay(3000) );
                return;
            }
            if(m.editing){
                obj.url = m.request.url;
                obj.entityId = m.request.entityId;
            }else{
                parentScope.simulation.sources.services.push(m.request)
            }
            $mdDialog.hide();
        }
        m.cancel = function(){
            $mdDialog.hide(); //Closing dialog gracefully, watch out if you are using promises in the main controller.
        }
        m.changedEntity = function(){
            var model = {};
            for(var i in m.entities){
                var entity = m.entities[i];
                if(entity.id == m.request.entityId){
                    model = models[entity.name];
                }
           }
           m.model = {
                success: true,
                response: [model]
           }

        }
        if(m.editing){
            m.changedEntity();
        }
}]);
