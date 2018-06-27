app.controller('ListsController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location", "dataService", "$http", '$mdDialog','i18nService',
                           function($scope,   uiGridConstants,   $localStorage,   $mdToast,   $location,   dataService,   $http,   $mdDialog,i18nService) {

    $scope.lists = [];

    i18nService.setCurrentLang('es');

    $scope.gridOptionsSimple = {
        rowHeight: 36,
        data: $scope.lists,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableGridMenu: true,
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
                name: 'Acciones',width: 100, displayName: 'Acciones', cellTemplate: '<a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.list({list: row.entity.id})""><i class="fa fa-pencil"> </i></a> <a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></a>'
            }
        ]
    };

    $scope.basicExec = function(){
        if(dataService.useStorage){
            //$scope.lists = $localStorage.lists;
        }else{
            $scope.loadLists();
        }
    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar la lista?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeList,
                headers: {
                    "Authorization": $scope.token
                },
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Lista borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }
            });
        });
    };

    $scope.loadLists = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findLists,
            headers:{
                "Authorization": $scope.token
            }
        }).success(function(data,headers){
            if(data.success){
                $scope.lists = data.response;
                $scope.gridOptionsSimple.data = $scope.lists;
            }
        });
    };
    $scope.basicExec();
}]);
