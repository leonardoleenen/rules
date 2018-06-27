app.controller('TestController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog', '$state',function($scope, $http, dataService, $stateParams, $mdToast,$localStorage, $rootScope, $mdDialog, $state) {

    $scope.test={
        drl: "",
        facts: "",
    };

    $scope.drlData = {};

    $scope.editors = {};

    $scope.final= {};

    $scope.step = 1;

    $scope.error = {
        error: false,
        message: []
    };

    $scope.errorSim = {
        error: false,
        message: []
    };

    $scope.successSim = {
        success: false,
        message: []
    };

  $scope.validate = function(){
    $scope.step = 1;
    $scope.errorSim.error = false;
    $scope.error.error = false;
    $scope.successSim.success = false;
    $scope.errorSim.message = "";
    $scope.error.message = "";
    $scope.successSim.message = "";

    $scope.test.drl = $scope.editors.drl.getValue();

    $http({
      method: "POST",
      url: dataService.commonUrl + "/" + dataService.drlTest,
      data: $scope.test.drl,
      headers: {
        Authorization: $scope.token
      }
    }).success(function(data){
      if(data.success){
        $scope.error.error = false;
        $scope.error.message = "";
        $scope.step = 2;
        $scope.final.drl = data.response;

        $scope.editors.facts = ace.edit("editor2");
        $scope.editors.facts.setTheme("ace/theme/eclipse");
        $scope.editors.facts.getSession().setMode("ace/mode/json");
        $scope.editors.facts.setOptions({"minLines":30,"maxLines": 50});
        $scope.editors.drl.$blockScrolling = Infinity;
        $scope.editors.facts.setValue(
                                      '[\n\t'+
                                      '{\n\t\t'+
                                      '"fact_name":"",\n\t\t'+
                                      '"properties":{\n\n\t\t}'+
                                      '\n\t}\n]');

        $mdToast.show($mdToast.simple().content("DRL VALIDO").position("top right").hideDelay(3000));
      }else{
        $scope.error.error = true;
        $scope.error.message = data.response;
        $scope.step = 1;
        $mdToast.show($mdToast.simple().content("Hubo un error: "+data.message).position("top right").hideDelay(3000));
      }
    });
  };

  $scope.validateJson = function(){
    try{
      $scope.editors.facts.setValue(JSON.stringify(JSON.parse($scope.editors.facts.getValue()),null,"\t"));
    }catch(e){
      $mdToast.show($mdToast.simple().content("JSON no valido: "+e).position("top right").hideDelay(3000));
    }
  };

  $scope.simulate = function(){
    $scope.test.facts = $scope.editors.facts.getValue();
    try{
      $http({
        method: "POST",
        url: dataService.commonUrl + "/" + dataService.drlSimulate,
        data: {
          facts: angular.fromJson($scope.test.facts),
          drl: $scope.final.drl
        },
        headers: {
          Authorization: $scope.token
        }
      }).success(function(data){
        if(data.success){
          $scope.errorSim.error = false;
          $scope.errorSim.message = "";
          $scope.successSim.success = true;
          $scope.successSim.message = data.message;
          $scope.successSim.response = data.response;
          $mdToast.show($mdToast.simple().content("Simulacion disparada con exito").position("top right").hideDelay(3000));
          $scope.test.results = data;

          if($scope.securityMatrix.indexOf('MENU_PUBLICACION') != -1)
            $scope.step = 3;

        }else{
          $scope.errorSim.error = true;
          $scope.successSim.success= false;
          $scope.errorSim.message = data.message;
          $scope.errorSim.response = data.response;
          $mdToast.show($mdToast.simple().content("Hubo un error: "+data.message).position("top right").hideDelay(3000));
        }
      });
    }
    catch(err){
      $mdToast.show($mdToast.simple().content("Error en JSON: "+err).position("top right").hideDelay(3000));
    }
   };

  $scope.install = function($event, force){
    if($scope.securityMatrix.indexOf('BTN_PUBLICAR_ESCENARIO') == -1)
      return;

    var isForced = "";

    if(force){
      isForced="?force=true";
    }

    if($scope.final.name === undefined || $scope.final.name.trim() === ""){
      $mdDialog.show(
                     $mdDialog.alert()
                     .parent(angular.element(document.querySelector('#popupContainer')))
                     .clickOutsideToClose(true)
                     .title('')
                     .content("Debe ingresar un nombre para la publicacion")
                     .ok('Entendido')
       );
      return;
    }

    if($scope.final.version === undefined || $scope.final.version <= 0){
      $mdDialog.show(
                     $mdDialog.alert()
                     .parent(angular.element(document.querySelector('#popupContainer')))
                     .clickOutsideToClose(true)
                     .title('')
                     .content("Debe ingresar una version mayor a 0 para la publicacion")
                     .ok('Entendido')
       );
      return;
    }

    $http({
      method: "POST",
      url: dataService.commonUrl + "/" + dataService.drlInstall+isForced,
      data: $scope.final,
      headers: {
        Authorization: $scope.token
      }
    }).success(function(data,headers){
      if(data.success){

        $scope.step = 4;
        $mdToast.show($mdToast.simple().content("Publicado con exito").position("top right").hideDelay(3000));

      }else{
        if(data.retry){
            $mdDialog.show({
              template:
                '<md-dialog aria-label="List dialog" flex="30">' +
                '   <md-toolbar class="md-accent">'+
                '      <div class="md-toolbar-tools">'+
                '        <h2>'+
                '          <span>Se necesitan acciones adicionales.</span>'+
                '        </h2>'+
                '      </div>'+
                '    </md-toolbar>'+
                     '  <md-dialog-content>'+
                     '      <div class="md-dialog-content">'+
                     '          <p class="text-danger"><b>Ya hay publicado un servicio con el mismo nombre y versión, por lo que la publicación se sobreescribirá si desea continuar. </b></p>'+
                     '      </div>'+
                     '  </md-dialog-content>' +
                     '  <div class="md-actions">' +
                     '    <md-button ng-click="accept()" class="md-primary">' +
                     '      Continuar y reemplazar' +
                     '    </md-button>' +
                     '    <md-button ng-click="cancel()" class="md-primary">' +
                     '      Cancelar' +
                     '    </md-button>' +
                     '  </div>' +
                     '</md-dialog>',
                   locals: {
                     data: data,
                     parentScope: $scope
                   },
                   controller: DialogController
                });
                function DialogController($scope, $mdDialog, data, parentScope) {
                  $scope.data = data;
                  $scope.accept = function() {
                    $mdDialog.hide();
                    parentScope.install(undefined, true);
                  }
                  $scope.cancel = function() {
                    $mdDialog.hide();
                  }
                }
              }else{
                $mdDialog.show(
                               $mdDialog.alert()
                               .parent(angular.element(document.querySelector('#popupContainer')))
                               .clickOutsideToClose(true)
                               .title('')
                               .content(data.message)
                               .ariaLabel('dialogo de error de guardado')
                               .ok('Ok..')
                );
             }
        }
      });
  };


  $scope.refresh = function(){
    basicExec();
  };

  var splitOnLast = function(obj,string){
    a = obj.split(string);
    e = [];
    if(a.length!=1){

      e[0] = a[0];
      for(i=1;i<a.length-1;i++){
        e[0] = e[0] + string + a[i];
      }
      e[1]=a[a.length-1];

    }else{
      e.push(a[0]);
    }
    return e;

  };

    $scope.saveThis = function(){
        if($scope.final.name === undefined || $scope.final.name.trim() == ""){
            $mdDialog.show(
                $mdDialog.alert()
                .parent(angular.element(document.querySelector('#popupContainer')))
                .clickOutsideToClose(true)
                .title('')
                .content("Debe ingresar un nombre")
                .ok('Entendido')
            );
            return;
        }

        data = {};

        if($scope.drlData.type == 'drl' && $scope.drlData.id !== undefined)
          data.id = $scope.drlData.id;

        data.name = $scope.final.name;
        data.description = $scope.final.version;
        data.drl = $scope.test.drl;
        data.type = 'drl';

        $http({
            method: "POST",
            url: dataService.commonUrl + "/" + dataService.saveDRL,
            data: data,
            headers: {
                Authorization: $scope.token
            }
        }).success(function(data,headers){
            if(data.success){
                $mdToast.show($mdToast.simple().content("Guardado con exito.").position("top right").hideDelay(3000));
                $state.go('app.test', {id: data.response.id, type: 'drl'},{reload:true});
            }else
                $mdDialog.show(
                               $mdDialog.alert()
                               .parent(angular.element(document.querySelector('#popupContainer')))
                               .clickOutsideToClose(true)
                               .title('')
                               .content(data.message)
                               .ariaLabel('dialogo de error de guardado')
                               .ok('Ok..')
                );
        });
    };


    var basicExec = function(){

        $scope.step = 1;
        $scope.errorSim.error = false;
        $scope.error.error = false;
        $scope.errorSim.message = "";
        $scope.error.message = "";

        $scope.successSim.success = false;
        $scope.successSim.message = "";

        $scope.editors.drl = ace.edit("editor");
        $scope.editors.drl.setTheme("ace/theme/chrome");
        $scope.editors.drl.getSession().setMode("ace/mode/java");
        $scope.editors.drl.$blockScrolling = Infinity;

        if(!$stateParams.id || !$stateParams.type){

            $scope.editors.drl.setValue('package com.leafnoise.pathfinder.analyzer.service\n\n'+
                                          'import java.util.*;\n\n'+
                                          'dialect "mvel"\n\n'+
                                          '/*Logger por defecto del analizador (necesario para poder realizar simulaciones y/o ejecuciones)*/\n'+
                                          'global org.apache.log4j.Logger log;\n\n'+
                                          '/*Lista String utilizada para el almacenamiento de mensajes*/\n'+
                                          'global java.util.List messages;\n\n'+
                                          '/*Objeto contenedor de constantes del workspace*/\n'+
                                          'global com.leafnoise.pathfinder.analyzer.utils.Constants rulzConstant;\n\n'+
                                          '/*Objecto de control que puede ser utilizado para chequeos, este declare puede ser editado a gusto pero no debe ser borrado*/\n'+
                                          'declare SystemControl\n'+
                                          '\trules: List = new LinkedList()\n'+
                                          'end\n\n'+
                                          '/*Regla que se dispara al comienzo para generar objetos necesarios para las demas reglas (Constantes, Listas de valores, etc)*/\n'+
                                          'rule "init"\n'+
                                          'salience 10000\n'+
                                          'when\n'+
                                          '\tnot SystemControl()\n'+
                                          'then\n'+
                                          '\tinsert(new SystemControl())\n'+
                                          'end\n\n');
        }else{
            $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.getAllDRLs + '/' + $stateParams.type + '/' + $stateParams.id,
                headers: {"Authorization": $scope.token}
              }).success(function(data,headers){
                if(data.success)
                    $scope.drlData = data.response;
                    $scope.editors.drl.setValue(data.response.drl);

                    if($scope.drlData.type == 'drl')
                        $scope.final.name = $scope.drlData.name;

              });
        }

    };

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de DRL"
            },
            controller: DialogController
        });
        function DialogController($scope, $mdDialog, faqs, name) {
            $scope.faqs = faqs;
            $scope.name = name;
            $scope.closeDialog = function() {
                $mdDialog.hide();
            };
        }
    };

    var faqs = [
        {
            "name": "¿Cual es el objetivo de esta pantalla?",
            "description": "Esta pantalla se encarga de la creación reglas avanzadas directamente en lenguaje MVEL/DRL que no estan soportadas por el editor de tablas de decisiones ni el editor de reglas avanzadas."
        },
        {
            "name": "¿Como comienzo a utilizar el editor?",
            "description": "Se comienza escribiendo el código dentro del editor DRL, el cual permite realizar una validación en-linea inmediata, la cual indica si tiene algun error de sintaxis o no."
        },
        {
            "name": "¿Como simulo usando esta pantalla?",
            "description": "Una vez validado el codigo DRL, tendrá el espacio para incluir las objetos de datos o instancias en formato JSON."
        },
        {
            "name": "¿Como publico la regla?",
            "description": "La regla una vez que está validada y simulada correctamente permite ser publicada con un nombre de servicio y versión, luego se mostrará en la pantalla de publicaciones para ver la forma en la cual puede consumir los servicios de reglas."
        }
    ];




  basicExec();

}]);
