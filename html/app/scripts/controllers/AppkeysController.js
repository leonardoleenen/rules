app.controller('AppkeysController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location",'dataService','$http', '$mdDialog','i18nService','$state', function($scope,    iGridConstants,   $localStorage,   $mdToast,   $location,  dataService,  $http,   $mdDialog,i18nService, $state) {

    $scope.publications = [];

    var cellTemplate = "";

    cellTemplate = cellTemplate
        +'<a id="testBtn" md-ink-ripple type="button" class="btn btn-primary" ng-click="grid.appScope.nextStep($event, row.entity)"><md-tooltip>Editar</md-tooltip><i class="fa fa-pencil"></i>'
        +'<a id="testBtn" md-ink-ripple type="button" class="btn btn-default" ng-click="grid.appScope.showKey($event, row.entity)"><md-tooltip>Ver APP-Key</md-tooltip><i class="fa fa-link"></i>'
        +'<a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><md-tooltip>Borrar</md-tooltip><i class="fa fa-trash"></a>';
    i18nService.setCurrentLang('es');

    $scope.gridOptionsSimple = {
        rowHeight: 36,
        data: $scope.publications,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        enableGridMenu: true,
        paginationPageSize: 10, //this
        enableCellEdit: true, //this
        columnDefs: [
            {field: 'name', displayName: 'Nombre'},
            {field: 'description', displayName: 'Descripcion'},
            {field: 'created_at', displayName: 'Fecha de Creación', type:'date', cellFilter:'date:\'dd/MM/yyyy\''},
            {field: 'edited_at', displayName: 'Fecha de Modificación', type:'date', cellFilter:'date:\'dd/MM/yyyy\''},
            {
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                name: 'Acciones',width: 120,displayName: 'Acciones', cellTemplate: cellTemplate
            }
        ]
    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta app key?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl + '/' + dataService.apiRemoveKey + '/' + obj.id,
                headers: {
                    "Authorization": $scope.token
                },
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdDialog.show(
                     $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .title('')
                        .content("La app key no pudo ser borrada: " + data.message)
                        .ariaLabel('Alert Dialog Demo')
                        .ok('Ok..')
                    );
                    $scope.basicExec();
                }
            });
        });
    };


    $scope.nextStep = function($event, obj){
        var parentEl = angular.element(document.body);
        /*var url = $scope.runtimeBaseUrl+'/selectividad/rest/rule_engine/execute/'+obj.name.replace(/ /, "_")+'/'+obj.version;*/
        var appkey = obj;
        $mdDialog.show({
         parent: parentEl,
         targetEvent: $event,
         templateUrl: "views/dialogs/new-app-key.html",
         locals: {
           item: appkey,
         },
         controller: AppKeyController
      }).then(function(){
        $scope.basicExec();
      });
    };

    $scope.basicExec = function(){
        // if($scope.securityMatrix.indexOf('MENU_PUBLICACION') == -1)
        //     $state.go('404');

        if(dataService.useStorage){
            $scope.publications = $localStorage.publications;
        }else{
             $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.apiAllKeys,
                headers: {
                    "Authorization": $scope.token
                }
              }).success(function(data,headers){
                if(data.success){
                    $scope.gridOptionsSimple.data = data.response;
                }
            });
        }
    }

    $scope.showKey = function($event, obj){
        var show = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('APP KEY')
            .content(obj.id)
            .ok('Aceptar')
        $mdDialog.show(show);
    };


    $scope.basicExec();

}]);
