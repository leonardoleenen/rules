app.controller('SimulationsController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location",'dataService','$http', '$mdDialog','i18nService',
                                 function($scope,    iGridConstants,   $localStorage,   $mdToast,   $location,  dataService,  $http,   $mdDialog,i18nService) {

    $scope.simulations = [];
    $scope.runtimeBaseUrl = dataService.runtimeBaseUrl;
    var cellTemplate = ''
      + '<a id="testBtn" md-ink-ripple type="button" class="btn btn-warning" ng-click="grid.appScope.getDRL($event, row.entity)"><md-tooltip>DRL</md-tooltip><i class="fa fa-terminal"></i>'
      + '<a id="testBtn" md-ink-ripple type="button" class="btn" ng-click="grid.appScope.testSim($event, row.entity)" ng-class="{disabled : row.entity.disabled, \'btn-primary\' : !row.entity.disabled, \'btn-default\' : row.entity.disabled}"><md-tooltip>Simular</md-tooltip><i class="fa fa-play"></i></a>'
      + '<a id="editBtn" md-ink-ripple type="button" class="btn btn-primary" ui-sref="app.simulation({simulation: row.entity.id})"><md-tooltip>Editar</md-tooltip><i class="fa fa-pencil"></i></a>'
      + '<a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><md-tooltip>Borrar</md-tooltip><i class="fa fa-trash"></a>';

    i18nService.setCurrentLang('es');

	$scope.gridOptionsSimple = {
        rowHeight: 36,
        data: $scope.simulations,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        enableGridMenu: true,
        paginationPageSize: 10, //this
        enableCellEdit: true, //this
        columnDefs: [
        	{field: 'name', displayName: 'Nombre'},
            {field: 'version', displayName: 'Versión'},
            {field: 'description', displayName: 'Descripción'},
            {field: 'user_name', displayName: 'Creador'},
        	{
                cellClass: "center",
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                name: 'Acciones',width: 175,displayName: 'Acciones', cellTemplate: cellTemplate
            }
        ]
    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar este escenario?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeSimulation,
                headers: {"Authorization": $scope.token},
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Simulacion borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdToast.show($mdToast.simple().content("La simulacion no pudo ser borrada: "+data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }
            });
        });
    };

    $scope.getDRL = function($event,obj){

        function DialogController($scope, $mdDialog, result) {
            $scope.data = result;
            $scope.closeDialog = function() {
                $mdDialog.hide();
            }
            $scope.saveAccion = function(){
                $mdDialog.hide();
            }
        }
        var parentEl = angular.element(document.body);
        $http({
            method: 'POST',
            url: dataService.commonUrl+'/'+dataService.getSimulationDRL,
            headers: {"Authorization": $scope.token},
            data: obj
        }).success(function(data,headers){
            $mdDialog.show({
                parent: parentEl,
                targetEvent: $event,
                templateUrl: "views/dialogs/drl-view.html",
                locals: {
                    result: data
                },
                controller: DialogController
            });
        });
    };

    $scope.testSim = function($event,obj){
      // if(obj.instances === null || obj.instances === undefined || obj.instances.length === 0){
      //   $mdToast.show($mdToast.simple().content("Es necesario al menos un fact para realizar la simulacion del escenario.").position("top right").hideDelay(3000));
      //   return;
      // }
      function DialogController($scope, $mdDialog, result) {
        $scope.data = result;
        $scope.closeDialog = function() {
          $mdDialog.hide();
        };
        $scope.saveAccion = function(){
          $mdDialog.hide();
        };
      }
      var parentEl = angular.element(document.body);
      $http({
        method: 'GET',
        url: dataService.commonUrl + '/' + dataService.testSimulation + '/' + obj.id,
        headers: {
          "Authorization": $scope.token
        }
      }).success(function(data,headers){
        $mdDialog.show({
          parent: parentEl,
          targetEvent: $event,
          templateUrl: "views/dialogs/simulation-result.html",
          locals: {
            result: data
          },
          controller: DialogController
        });
      });
    };
    $scope.basicExec = function(){
        if(dataService.useStorage){
            $scope.simulations = $localStorage.simulations;
        }else{
             $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.findSimulations,
                headers: {"Authorization": $scope.token}
              }).success(function(data,headers){
                if(data.success){
                    $scope.gridOptionsSimple.data = data.response;
                }
            });
        }
    }
    $scope.publish = function($event, simulation){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.publish+'/'+simulation.id,
            headers: {"Authorization": $scope.token},
        }).success(function(data,headers){
            if(data.success){
                simulation.installed = true;
                $mdToast.show($mdToast.simple().content("El escenario se publico correctamente.").position("top right").hideDelay(3000) );
            }else{
                $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
            }
        });
    }
    $scope.unPublish = function($event, simulation){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.unPublish+'/'+simulation.id,
            headers: {"Authorization": $scope.token},
        }).success(function(data,headers){
            if(data.success){
                simulation.installed = false;
                 $mdToast.show($mdToast.simple().content("El escenario se despublico correctamente.").position("top right").hideDelay(3000) );
            }else{
                $mdToast.show($mdToast.simple().content("No se pudo despublicar.").position("top right").hideDelay(3000) );
            }
        });
    }
    $scope.basicExec();
}]);
