app.controller('FunctionsController', ['$scope', 'dataService', 'uiGridConstants', '$localStorage', '$mdToast', "$location", '$http', '$mdDialog','i18nService',
                               function($scope,   dataService,   uiGridConstants,   $localStorage,   $mdToast,   $location,   $http,   $mdDialog, i18nService) {
    //$localStorage.entities = undefined;

    i18nService.setCurrentLang('es');

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta función?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeFunction,
                headers: {"Authorization": $scope.token},
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Funcion borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.loadFunctions();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                }
            });
        });

    }
    $scope.basicExec = function(){
        $scope.functions = [];
        if(dataService.useStorage){
            $scope.functions = $localStorage.functions;
        }else{
            $scope.loadFunctions();
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
                {field: 'user_name', displayName: 'Creador'},
                {
                    enableSorting: false,//this
                    enableFiltering: false,//this
                    cellClass: "center",
                    name: 'Acciones',width: 120, displayName: 'Acciones', cellTemplate: '<a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.function({function: row.entity.id})""><i class="fa fa-pencil"> </i></a> <a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></a>'
                }
            ]
        };
    }
    $scope.loadFunctions = function(){
     $http({
        method: 'GET',
        url: dataService.commonUrl+'/'+dataService.findFunctions,
        headers: {"Authorization": $scope.token}
      }).success(function(data,headers){
        if(data.success)
        $scope.gridOptionsSimple.data = data.response;
      });
    }
    $scope.basicExec();
}]);
