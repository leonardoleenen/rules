app.controller('EntitiesController', ['$scope', 'dataService', 'uiGridConstants', '$localStorage', '$mdToast', "$location", '$http', '$mdDialog','i18nService',
                             function($scope,    dataService,   uiGridConstants,   $localStorage,   $mdToast,   $location,   $http,   $mdDialog,i18nService) {
    //$localStorage.entities = undefined;

    i18nService.setCurrentLang('es');

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta entidad?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeEntity,
                headers: {"Authorization": $scope.token},
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Entidad borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.loadEntities();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                }
            });
        });
    }
    $scope.basicExec = function(){
        $scope.entities = [];
        if(dataService.useStorage){
            $scope.entities = $localStorage.entities;
        }else{
            $scope.loadEntities();
        }
        console.log(typeof $scope.entities);
        if(typeof $scope.entities != 'object'){
            $mdToast.show($mdToast.simple().content("Se cargaron datos de ejemplo").position("top right").hideDelay(3000) );
            $localStorage.entities = [{
                name: "entidad1",
                id : "123oi12p3o12i4",
                description: "primera descripcion"
                },{
                name: "entidad2",
                id : "123oi12p3o12i4",
                description: "primera descripcion"
            }];
        }
        //var entities = $localStorage.entities;
        $scope.gridOptionsSimple = {
            rowHeight: 36,
            data: $scope.entities,
            enableFiltering: true,//this
            paginationPageSizes: [10, 20, 40], //this
            paginationPageSize: 10, //this
            enableCellEdit: true, //this
            enableGridMenu: true,
            columnDefs: [
                {field: 'name', displayName: 'Nombre', alignment: 'center'},
                {field: 'description', displayName: 'Descripcion'},
                {field: 'user_name', displayName: 'Creador'},
                {
                    cellClass: "center",
                    exporterSuppressExport: true,
                    enableSorting: false,//this
                    enableFiltering: false,//this
                    name: 'Acciones',width: 120, displayName: 'Acciones', cellTemplate: '<a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.entity({entity: row.entity.id})""><i class="fa fa-pencil"></i></a> <a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></i></a>'
                }
            ]
        };
    }
    $scope.loadEntities = function(){
     $http({
        method: 'GET',
        url: dataService.commonUrl+'/'+dataService.findTypes,
        headers: {"Authorization": $scope.token}
      }).success(function(data,headers){
        if(data.success)
        $scope.gridOptionsSimple.data = data.response;
      });
    }
    $scope.basicExec();
}]);
