app.controller('PublicationsController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location",'dataService','$http', '$mdDialog','i18nService','$state', function($scope,    iGridConstants,   $localStorage,   $mdToast,   $location,  dataService,  $http,   $mdDialog,i18nService, $state) {

    $scope.publications = [];
    //$scope.runtimeBaseUrl = dataService.runtimeBaseUrl;
    var cellTemplate = ""

    if($scope.securityMatrix.indexOf('BTN_PUBLICAR_ESCENARIO')>-1){
        cellTemplate = cellTemplate +'<a href="" class="btn btn-danger" style="margin-right: 5px;" ng-hide="row.entity.installed" ng-click="grid.appScope.publish($event, row.entity)"><md-tooltip>Publicar</md-tooltip><i class="fa fa-power-off"></i></a>'
    +'<a href="" class="btn btn-success" style="margin-right: 5px;" ng-show="row.entity.installed" ng-click="grid.appScope.unPublish($event, row.entity)"><md-tooltip>Despublicar</md-tooltip><i class="fa fa-power-off"></i></a>'
    }
    cellTemplate = cellTemplate
    +'<div class="btn-group">'
        +'<a id="testBtn" md-ink-ripple type="button" class="btn btn-primary" ng-click="grid.appScope.getDRL($event, row.entity)"><md-tooltip>DRL</md-tooltip><i class="fa fa-terminal"></i>'
        +'<a id="testBtn" md-ink-ripple type="button" class="btn" ng-click="grid.appScope.copyUrl($event, row.entity)" ng-class="{disabled : !row.entity.installed, \'btn-primary\' : row.entity.installed, \'btn-default\' : !row.entity.installed}"><md-tooltip>Ver SLA del servicio</md-tooltip><i class="fa fa-link"></i>'
        +'<a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><md-tooltip>Borrar</md-tooltip><i class="fa fa-trash"></a>'
    +'</div>';

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
            {field: 'version', displayName: 'Versión'},
            {field: 'date', displayName: 'Fecha'},
            {field: 'snapshot', displayName: 'Snapshot Asociado'},
            {field: 'user_name', displayName: 'Creador'},
            {
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                name: 'Acciones',width: 160,displayName: 'Acciones', cellTemplate: cellTemplate
            }
        ]
    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta publicacion?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removePublications,
                headers: {
                    "Authorization": $scope.token
                },
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Publicacion borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdDialog.show(
                     $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .title('')
                        .content("La publicacion no pudo ser borrada: " + data.message)
                        .ariaLabel('Alert Dialog Demo')
                        .ok('Ok..')
                    );
                    $scope.basicExec();
                }
            });
        });
    };

    $scope.getDRL = function($event, obj){

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

        data = {message: "DRL publicado", response: obj.drl, success: true}

        $mdDialog.show({
            parent: parentEl,
            targetEvent: $event,
            templateUrl: "views/dialogs/drl-view.html",
            locals: {
                result: data
            },
            controller: DialogController
        });

    };
    $scope.copyUrl = function($event, obj){
        var parentEl = angular.element(document.body);
        var sla = obj;
        $mdDialog.show({
            parent: parentEl,
            targetEvent: $event,
            templateUrl: "views/dialogs/publications-sla.html",
            locals: {
                item: sla,
            },
            controller: DialogController
      });

      function DialogController($scope, $mdDialog, item) {
        $scope.obj = item;
        $scope.closeDialog = function() {
          $mdDialog.hide();
        }
        $scope.date = new Date();
        $scope.getGenericUrl = function(url){
            // console.log(url)
            var split = url.split("/");
            return split.slice(0, split.length - 1).join("/");
        }
      }

    };

    $scope.basicExec = function(){
        if($scope.securityMatrix.indexOf('MENU_PUBLICACION') == -1)
            $state.go('404');

        if(dataService.useStorage){
            $scope.publications = $localStorage.publications;
        }else{
             $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.findPublications,
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

    $scope.publish = function($event, publication){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de publicación')
            .content('¿Esta seguro que desea republicar el servicio seleccionado?')
            .ok('Publicar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.publicationInstall+'/'+publication.id,
                headers: {"Authorization": $scope.token},
            }).success(function(data,headers){
                if(data.success){
                    publication.installed = true;
                    $scope.basicExec();
                    $mdToast.show($mdToast.simple().content("El servicio se publicó correctamente").position("top right").hideDelay(3000) );
                }else{
                    $mdDialog.show(
                         $mdDialog.alert()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .clickOutsideToClose(true)
                            .title('')
                            .content(data.message)
                            .ariaLabel('Alert Dialog Demo')
                            .ok('Ok..')
                        );
                }
            });
        });
    }

    $scope.unPublish = function($event, publication){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de despublicación')
            .content('¿Esta seguro que desea despublicar el servicio seleccionado?')
            .ok('Despublicar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.publicationUninstall+'/'+publication.id,
                headers: {
                    "Authorization": $scope.token
                },
            }).success(function(data,headers){
                if(data.success){
                    publication.installed = false;
                    $scope.basicExec();
                    $mdToast.show($mdToast.simple().content("Se despublicó correctamente el servicio.").position("top right").hideDelay(3000) );
                }else{
                    $mdDialog.show(
                        $mdDialog.alert()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .clickOutsideToClose(true)
                            .title('')
                            .content(data.message)
                            .ariaLabel('Alert Dialog Demo')
                            .ok('Ok..')
                        );
                }
            });
        })

    }

    $scope.basicExec();

}]);
