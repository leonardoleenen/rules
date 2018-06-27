app.controller('NormativesController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location", "dataService", "$http", '$mdDialog',
                                function($scope,   uiGridConstants,   $localStorage,   $mdToast,   $location,   dataService,   $http,   $mdDialog) {

    $scope.normatives = [];

    $scope.gridOptionsSimple = {
        rowHeight: 36,
        data: $scope.normatives,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableCellEdit: true, //this
        enableGridMenu: true, //this
        columnDefs:[
            {field: 'name', displayName: 'Nombre'},
            {
                cellTemplate: '<div class="ui-grid-cell-contents">{{row.entity.vigency_date | date: "dd/MM/yyyy"}}</div>',
                name: 'Fecha de Vigencia',
                displayName: 'Fecha de Vigencia'
            },
            {
                cellTemplate: '<div class="ui-grid-cell-contents">{{row.entity.ending_date | date: "dd/MM/yyyy"}}</div>',
                name: 'Fecha de Finalización',
                displayName: 'Fecha de Finalización'
            },
            {
                cellTemplate: '<div class="ui-grid-cell-contents">{{row.entity.signature_date | date: "dd/MM/yyyy"}}</div>',
                name: 'Fecha de Firma',
                displayName: 'Fecha de Firma'
            },
            {
                cellTemplate: '<div class="ui-grid-cell-contents">{{row.entity.application_date | date: "dd/MM/yyyy"}}</div>',
                name: 'Fecha de Aplicación',
                displayName: 'Fecha de Aplicación'
            },
            {field: 'user_name', displayName: 'Creador'},
            {
                name: 'Acciones',
                width: 100,
                displayName: 'Editar',
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                cellClass: "center",
                cellTemplate: '<a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.normative({normative: row.entity.id})""><i class="fa fa-pencil"> </i></a> <a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></a>'}
        ]
    };

    $scope.basicExec = function(){
        if(dataService.useStorage){
            $scope.normatives = $localStorage.normatives;
        }else{
            $scope.loadNormatives();
        }
    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar este instrumento normativo?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeNormative,
                headers: {
                    "Authorization": $scope.token
                },
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Instrumento Normativo borrado correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }
            });
        });
    };

    $scope.loadNormatives = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findNormatives,
            headers:{
                "Authorization": $scope.token
            }
        }).success(function(data,headers){
            if(data.success){
                $scope.normatives = data.response;
                $scope.gridOptionsSimple.data = $scope.normatives;
            }
        });
    };
    $scope.basicExec();
}]);
