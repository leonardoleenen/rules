app.controller('FunctionController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$state', '$mdDialog',
  function(  $scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $state,   $mdDialog) {
    $scope.funct = {
      id : null,
      params : []
    };

    $scope.temp={};

    $scope.isAddingParam = false;

    $scope.types = [
      {
        type: "void",
        readableType: "Vacío (void)"
      },
      {
          type: "Object",
          readableType: "Objeto (Object)"
      },
      {
          type: "String",
          readableType: "Texto (String)"
      },
      {
          type: "Integer",
          readableType: "Numero entero (Integer)"
      },
      {
          type: "Float",
          readableType: "Numero decimal (Float)"
      },
      {
          type: "Boolean",
          readableType: "Booleano (Boolean)"
      },
      {
          type: "Date",
          readableType: "Fecha (Date)"
      },
      {
          type: "String[]",
          readableType: "Arreglo de textos (String[])"
      },
      {
          type: "Integer[]",
          readableType: "Arreglo de Numeros enteros (Integer[])"
      },
      {
          type: "Float[]",
          readableType: "Arreglo de Numeros decimales (Float[])"
      },
      {
          type: "Boolean[]",
          readableType: "Arreglo de Booleanos (Boolean[])"
      },
      {
          type: "Date[]",
          readableType: "Arreglo de fechas (Date[])"
      },
      {
          type: "List",
          readableType: "Lista (List)"
      }
    ];

    $scope.addParam = function(){
      if($scope.temp.name === "" || $scope.temp.type === "" || $scope.temp.name === undefined || $scope.temp.type === undefined){
        $mdToast.show($mdToast.simple().content("No se puede continuar, verifique los campos.").position("top right").hideDelay(5000));
        return;
      }

      $scope.funct.params.push({
        type: $scope.temp.type,
        name: $scope.temp.name
      });

      $scope.isAddingParam = false;
    };

    $scope.deleteParam = function(index){
      $scope.funct.params.splice(index, 1);
    };

    $scope.save = function(type){
      if($scope.funct.name === undefined || $scope.funct.name.trim() === ""){
        $mdToast.show($mdToast.simple().content("El nombre de la funcion no puede estar vacío").position("top right").hideDelay(3000));
        return;
      }

      if($scope.funct.returnType === undefined){
          $mdToast.show($mdToast.simple().content("El tipo de retorno no puede estar vacío").position("top right").hideDelay(3000) );
          return;
      }
      $scope.funct.body = $scope.editor.getValue();

      $http({
        method: 'POST',
        url: dataService.commonUrl+'/'+dataService.saveFunction,
        data: $scope.funct,
        headers: {
          "Authorization": $scope.token
        }
      }).success(function(data,headers){
        if(data.success){
          $mdToast.show($mdToast.simple().content("Guardado con exito.").position("top right").hideDelay(3000));
          if(type=="goBack"){
            $state.go('app.functions');
          }else{
            $state.go('app.function', {function: data.response.id});
          }
        }else{
          $mdDialog.show(
            $mdDialog.alert()
              .parent(angular.element(document.body))
              .title('Hubo un error')
              .content('Motivo: '+data.response)
              .ariaLabel('Dialog Alerta error')
              .ok('Corregir!')
          );
        }
        return;
      });

    };

    $scope.simulate = function(){
      if($scope.funct.name === undefined || $scope.funct.name === ""){
        $mdToast.show($mdToast.simple().content("El nombre de la funcion no puede estar vacío").position("top right").hideDelay(3000));
        return;
      }

      if($scope.funct.returnType === undefined || $scope.funct.returnType === ""){
        $mdToast.show($mdToast.simple().content("El tipo de retorno no puede estar vacío").position("top right").hideDelay(3000));
        return;
      }

      $scope.funct.body = $scope.editor.getValue();

      if($scope.funct.body === undefined || $scope.funct.body === ""){
        $mdToast.show($mdToast.simple().content("El cuerpo de la función no puede estar vacío").position("top right").hideDelay(3000));
        return;
      }

      $http({
        method: 'POST',
        url: dataService.commonUrl+'/'+dataService.simulateFunction,
        data: $scope.funct,
        headers: {"Authorization": $scope.token}
      }).success(function(data,headers){
        if(data.success){
          $mdDialog.show(
            $mdDialog.alert()
              .parent(angular.element(document.body))
              .title('Sin errores')
              .ariaLabel('Dialog Alerta success')
              .ok('Continuar')
          );
        }else{
          $mdDialog.show(
            $mdDialog.alert()
              .parent(angular.element(document.body))
              .title('Hubo un error')
              .content('Motivo: '+data.response)
              .ariaLabel('Dialog Alerta error')
              .ok('Corregir')
          );
        }
        return;
      });

    };

    var basicExec = function(){
        $scope.editor = ace.edit("editor");
        $scope.editor.setTheme("ace/theme/chrome");
        $scope.editor.getSession().setMode("ace/mode/java");

        if(dataService.useStorage){
            //TODO: modo demo/localstorage.
        }else{
            if($stateParams.function){
                $http({
                    method: 'GET',
                    url: dataService.commonUrl+'/'+dataService.findFunction+'/'+$stateParams.function,
                    headers: {"Authorization": $scope.token}
                }).success(function(data,headers){
                    if(data.success){
                        $scope.funct = data.response;
                        $scope.editor.setValue($scope.funct.body);
                    }
                });
            }
        }
    };

    $scope.goBack = function(){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Los cambios no guardados se perderán')
            .content('¿Esta seguro que desea volver?')
            .ok('Volver')
            .cancel('Cancelar');

        $mdDialog.show(confirm).then(function() {
            $state.go("app.functions");
        });
    };

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de Funciones"
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
            "description": "Esta pantalla se encarga de la creación/modificación de funciones java para poder ser usadas posteriormente en las reglas"
        },
        {
            "name": "¿Por qué el nombre de la función no puede estar vacio?",
            "description": "Esto se debe a que es necesario un nombre para poder declararla y de esta manera usarla o identificarla en las reglas/tablas"
        },
        {
           "name": "¿Es necesario elegir un tipo de retorno?",
            "description": "Si, toda función java es declarada con un tipo de retorno, de no retornar ningun valor, se deberá usar \"void\""
        }
    ];

    basicExec();

}]);
