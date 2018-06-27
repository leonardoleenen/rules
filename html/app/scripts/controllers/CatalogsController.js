app.controller('CatalogsController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location", "dataService", "$http", '$mdDialog', 'i18nService',
                            function(  $scope,   uiGridConstants,   $localStorage,   $mdToast,   $location,   dataService,   $http,   $mdDialog ,  i18nService) {

    $scope.catalogs = [];
    i18nService.setCurrentLang('es');
    $scope.gridOptionsSimple = {
        enableGridMenu: true,
        rowHeight: 36,
        enableFiltering: true,//this
        data: $scope.catalogs,
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableCellEdit: true, //this
        columnDefs:[
            {field: 'name', displayName: 'Nombre'},
            {field: 'description', displayName: 'Descripcion'},
            {field: 'user_name', displayName: 'Creador'},
            {
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                cellClass: "center",
                name: 'Acciones',width: 100, displayName: 'Acciones', cellTemplate: '<a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.catalog({catalog: row.entity.id})""><i class="fa fa-pencil"></i></a> <a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></a>'}
        ]
    };

    $scope.basicExec = function(){
        if(dataService.useStorage){
            $scope.catalogs = $localStorage.catalogs;
        }else{
            $scope.loadCatalogs();
        }
    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar este dominio?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeCatalog,
                headers: {
                    "Authorization": $scope.token
                },
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Dominio borrado correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }
            });
        });
    };

    $scope.loadCatalogs = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findCatalogs,
            headers:{
                "Authorization": $scope.token
            }
        }).success(function(data,headers){
            if(data.success){
                $scope.catalogs = data.response;
                $scope.gridOptionsSimple.data = $scope.catalogs;
            }
        });
    };
    $scope.basicExec();
}]);
