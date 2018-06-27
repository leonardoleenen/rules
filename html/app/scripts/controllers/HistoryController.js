app.controller('HistoryController', ['$scope', 'dataService', 'uiGridConstants', '$localStorage', '$mdToast', "$location", '$http', '$mdDialog','i18nService',
                             function($scope,   dataService,   uiGridConstants,   $localStorage,   $mdToast,   $location,   $http,   $mdDialog,i18nService) {

    i18nService.setCurrentLang('es');

    $scope.snapshots = [];

    $scope.gridOptionsSimple = {
        rowHeight: 36,
        data: $scope.snapshots,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableCellEdit: true, //this
        enableGridMenu: true,
        columnDefs: [
            {field: 'name', displayName: 'Nombre'},
            {field: 'description', displayName: 'Descripcion'},
            {field: 'date', displayName: 'Fecha'},
            {field: 'user', displayName: 'Usuario'},
            {field: 'size', displayName: 'Tamaño'},
            {
                cellClass: "center",
                exporterSuppressExport: true,
                enableSorting: false,//this
                enableFiltering: false,//this
                name: 'Acciones',width: 150, displayName: 'Acciones', cellTemplate: '<div class="btn-group">'
                + '<a id="downloadButton" type="button" class="btn btn-primary" ng-click="grid.appScope.downloadSnapshot(row.entity)"><i class="fa fa-download"></i><md-tooltip md-direction="left">Descargar</md-tooltip></a>'
                + '<a ng-if="grid.appScope.showldShowButton(row.entity.user)" id="editbutton" type="button" class="btn btn-primary" ng-click="grid.appScope.editDescription(row.entity)"><i class="fa fa-pencil"></i><md-tooltip md-direction="top">Editar</md-tooltip></a>'
                + '<a class="btn btn-danger" ng-click="grid.appScope.useSnapshot(row.entity)"><i class="fa fa-refresh"></i><md-tooltip md-direction="top">Usar</md-tooltip></a>'
                + '<a ng-if="grid.appScope.showldShowButton(row.entity.user)" class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><md-tooltip md-direction="right">Borrar</md-tooltip><i class="fa fa-trash"></a></div>'
            }
        ]
    };
    $scope.gridOptionsSimple.onRegisterApi = function (gridApi){
      $scope.gridApi = gridApi;
    }
    $scope.delObj = function(obj){
         var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea eliminar este snapshot? Una vez realizada esta accion no podra desacerse')
            .ok('Eliminar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl + '/' + dataService.deleteSnapshot + '/' + obj.id,
                headers: {
                    "Authorization": $scope.token
                }
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.loadSnapshots();
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

    $scope.useSnapshot = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de Uso')
            .content('¿Esta seguro que desea utilizar este snapshot? El estado actual de la plataforma se almacenara antes de realizar el proceso de restauracion')
            .ok('Usar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.useSnapshot,
                headers: {"Authorization": $scope.token},
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.loadSnapshots();
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

    $scope.newSnapshot = function($event){

        var parentEl = angular.element(document.body);
        $mdDialog.show({
        parent: parentEl,
        targetEvent: $event,
        template:
          '<md-dialog aria-label="List dialog">' +
          '  <md-dialog-content>'+
          '<div class="md-dialog-content">'+
          '<md-input-container>'+
          '<h4>Generar snapshot</h4>'+
          '<label>Nombre</label>'+
          '<input type="text" ng-model="snapshotName">'+
          '</md-input-container>'+
          '<md-input-container>'+
          '<label>Descripcion</label>'+
          '<textarea cols="30" ng-model="snapshotDescription"></textarea>'+
          '</md-input-container>'+
          '</div>'+
          '  </md-dialog-content>' +
          '  <div class="md-actions">' +
          '    <md-button ng-click="generateSnapshot()" class="md-primary">' +
          '      Generar' +
          '    </md-button>' +
          '    <md-button ng-click="closeDialog()" class="md-primary">' +
          '      Cerrar' +
          '    </md-button>' +
          '  </div>' +
          '</md-dialog>',
        locals: {
          loadSS: $scope.loadSnapshots,
          token: $scope.token
        },
        controller: DialogController
      });
      function DialogController($scope, $mdDialog, loadSS, token) {
        $scope.snapshotName = "";
        $scope.snapshotDescription = "";

        $scope.generateSnapshot = function(){
            if(!$scope.snapshotName){
                $mdToast.show($mdToast.simple().content("Debe ingresar un nombre para el snapshot").position("top right").hideDelay(3000) )
                return;
            }

            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.newSnapshot+'/'+$scope.snapshotName,
                headers: {
                    "Authorization": token
                },
                data: $scope.snapshotDescription
              }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Se ha creado un nuevo snapshot de la plataforma con el nombre " + data.response).position("top right").hideDelay(3000) );
                    loadSS();
                }else{
                    dataService.showAlert("", data.message);
                    /*$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );*/
                }
                $mdDialog.hide();
              });
        }

        $scope.closeDialog = function() {
          $mdDialog.hide();
        }
      }
    }


    $scope.editDescription = function(obj, $event){

        var parentEl = angular.element(document.body);
        $mdDialog.show({
        parent: parentEl,
        targetEvent: $event,
        template:
          '<md-dialog aria-label="List dialog">' +
          '  <md-dialog-content>'+
          '<div class="md-dialog-content">'+
          ' <md-input-container>'+
          ' <label>Descripcion</label>'+
          ' <textarea rows="5" cols="30" ng-model="snapshotDescription"></textarea>'+
          ' </md-input-container>'+
          '   </md-dialog-content>' +
          '   <div class="md-actions">' +
          '      <md-button ng-click="doEdit()" class="md-primary">' +
          '        Aceptar' +
          '      </md-button>' +
          '     <md-button ng-click="closeDialog()" class="md-primary">' +
          '        Cerrar' +
          '      </md-button>' +
          '    </div>' +
          '  </div>' +
          '</md-dialog>',
        locals: {
          loadSS: $scope.loadSnapshots,
          token: $scope.token,
          snp: obj
        },
        controller: DialogController
      });
      function DialogController($scope, $mdDialog, loadSS, token, snp) {
        $scope.snapshotDescription = snp.description;

        $scope.doEdit = function(){

            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.editSnapshot+'/'+snp.id,
                headers: {
                    "Authorization": token
                },
                data: {
                    "description": $scope.snapshotDescription
                }
              }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    loadSS();
                }else{
                    dataService.showAlert("", data.message);
                    /*$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );*/
                }
                $mdDialog.hide();
              });
        }

        $scope.closeDialog = function() {
          $mdDialog.hide();
        }
      }
    }

    $scope.basicExec = function(){
        $scope.loadSnapshots();
    }

    $scope.loadSnapshots = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findSnapshots,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){
                $scope.snapshots = data.response;
                $scope.gridOptionsSimple.data = $scope.snapshots;
            }
          });
      };

      var b64toBlob = function(b64Data, contentType, sliceSize) {
        contentType = contentType || '';
        sliceSize = sliceSize || 512;

        var byteCharacters = atob(b64Data);
        var byteArrays = [];

        for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
            var slice = byteCharacters.slice(offset, offset + sliceSize);

            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }

            var byteArray = new Uint8Array(byteNumbers);

            byteArrays.push(byteArray);
        }

        var blob = new Blob(byteArrays, {type: contentType});
        return blob;
      }

      $scope.makeExport = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.exportSnapShot,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){
                bb =b64toBlob(data.response.b64, data.response.filetype);
                /*window.open(URL.createObjectURL(bb));*/
                url = URL.createObjectURL(bb)
                var a = document.createElement("a");
                document.body.appendChild(a);
                a.style = "display: none";
                a.href = url
                a.download = data.response.name
                a.click();
                /*window.URL.revokeObjectURL(url);*/
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
      };

      $scope.downloadSnapshot = function(obj){
        if(obj == undefined || obj.name == undefined)
            return;

        $http({
            method: 'GET',
            url: dataService.commonUrl + '/' + dataService.exportSnapShot + '/' + obj.name,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){
                bb =b64toBlob(data.response.b64, data.response.filetype);
                /*window.open(URL.createObjectURL(bb));*/
                url = URL.createObjectURL(bb)
                var a = document.createElement("a");
                document.body.appendChild(a);
                a.style = "display: none";
                a.href = url
                a.download = data.response.name
                a.click();
                /*window.URL.revokeObjectURL(url);*/
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
      }

      $scope.import = function(){
        if($scope.fileImport == undefined || $scope.fileImport.filename.substr($scope.fileImport.filename.lastIndexOf(".")) != ".json"){
            $mdToast.show($mdToast.simple().content("Debe ingresar un archivo json para realizar la importacion de estado").position("top right").hideDelay(3000) );
            $scope.fileImport = undefined;
            return;
        }
        $http({
            method: 'POST',
            url: dataService.commonUrl+'/'+dataService.importSnapshot,
            headers: {
                "Authorization": $scope.token
            },
            data: $scope.fileImport
          }).success(function(data,headers){
            if(data.success){
                $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
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

            $scope.loadSnapshots();

          });
      };

      $scope.showldShowButton = function(user){
        return ($scope.userName == user || $scope.securityMatrix.indexOf("DELETE_SNAPSHOT") != -1)
      }



    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Historial y Snapshots"
            },
            controller: DialogController
        });
        function DialogController($scope, $mdDialog, faqs, name) {
            $scope.faqs = faqs;
            $scope.name = name;
            $scope.closeDialog = function() {
                $mdDialog.hide();
            }
        }
    };

    var faqs = [
        {
            "name": "¿Cual es el objetivo de esta pantalla?",
            "description": "Esta pantalla se encarga de la administración de historial, ademas la pantalla permite la generacion y recuperación de distintos snapshots de la plataforma"
        },
        {
            "name": "¿Que son los snapshots?",
            "description": "Los snapshots son una copia espejo de la plataforma completa al momento de realizar la operación de generación del mismo, esto sirve para poder guardar copias de respaldo o volver el sistema a un punto anterior."
        },
    ];
    $scope.basicExec();

}]);
