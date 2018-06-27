app.controller('DRLsController', ['$scope', 'dataService', 'uiGridConstants', '$localStorage', '$mdToast', "$location", '$http', '$mdDialog','i18nService',
                               function($scope,   dataService,   uiGridConstants,   $localStorage,   $mdToast,   $location,   $http,   $mdDialog, i18nService) {
    //$localStorage.entities = undefined;

    i18nService.setCurrentLang('es');

    $scope.delObj = function(obj){
        if(obj.type != 'drl')
            return;

        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta este DRL?')
            .ok('Borrar')
            .cancel('Cancelar');

        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeDRL,
                headers: {"Authorization": $scope.token},
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("DRL borrado correctamente").position("top right").hideDelay(3000) );
                    $scope.loadDRLs();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                }
            });
        });

    };

    $scope.basicExec = function(){
        $scope.functions = [];
        if(dataService.useStorage){
            $scope.functions = $localStorage.functions;
        }else{
            $scope.loadDRLs();
        }

        $scope.gridOptionsSimple = {
            rowHeight: 36,
            enableGridMenu: true,
            data: $scope.functions,
            enableFiltering: true,//this
            paginationPageSizes: [10, 20, 40], //this
            paginationPageSize: 10, //this
            enableCellEdit: true, //this
            columnDefs: [
                {field: 'name', displayName: 'Nombre'},
                {field: 'description', displayName: 'Descripcion'},
                {field: 'type', displayName: 'Tipo'},
                {field: 'user_name', displayName: 'Creador'},
                {
                    enableSorting: false,//this
                    enableFiltering: false,//this
                    cellClass: "center",
                    name: 'Acciones',width: 120, displayName: 'Acciones', cellTemplate: '<a id="showDRLBtn" md-ink-ripple type="button" class="btn btn-warning" ng-click="grid.appScope.showDRL($event, row.entity)"><md-tooltip>DRL</md-tooltip><i class="fa fa-terminal"></i> <a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.test({id: row.entity.id, type: row.entity.type})""><i class="fa fa-pencil"> </i></a> <a ng-if="row.entity.type==\'drl\'" class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></a>'
                }
            ]
        };
    };

    $scope.showDRL = function($event,obj){

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

        $mdDialog.show({
            parent: parentEl,
            targetEvent: $event,
            templateUrl: "views/dialogs/drl-view.html",
            locals: {
                result: {"success": true, "response": obj.drl, "message": "DRL de " + obj.name}
            },
            controller: DialogController
        });
    };

    $scope.loadDRLs = function(){
     $http({
        method: 'GET',
        url: dataService.commonUrl+'/'+dataService.getAllDRLs,
        headers: {"Authorization": $scope.token}
      }).success(function(data,headers){
        if(data.success)
            $scope.gridOptionsSimple.data = data.response;
      });
    };

    $scope.basicExec();
}]);
