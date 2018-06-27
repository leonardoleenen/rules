app.controller('AuditoryController', ['$scope', 'dataService', 'uiGridConstants', '$localStorage', '$mdToast', "$location", '$http', '$mdDialog','i18nService', '$state',
                             function($scope,   dataService,   uiGridConstants,   $localStorage,   $mdToast,   $location,   $http,   $mdDialog, i18nService, $state) {

    i18nService.setCurrentLang('es');

    $scope.auditoryUsers = [];
    $scope.auditoryTypes = ["reglas","entidades", "tablas", "catalogos", "formulas", "funciones", "Instrumentos Normativos", "constantes"];
    $scope.auditoryMethods = ["Creacion", "Modificacion", "Eliminacion"];

    var audit_views = {
        "rules": ['views/dialogs/audit-rule-view.html', AuditRuleController],
        "tables": ['views/dialogs/audit-table-view.html', AuditTableController],
        "entitys": ['views/dialogs/audit-entity-view.html', AuditEntityController],
        "catalogs": ['views/dialogs/audit-catalog-view.html', AuditCatalogController],
        "formulas": ['views/dialogs/audit-formula-view.html', AuditFormulaController],
        "functions": ['views/dialogs/audit-function-view.html', AuditFunctionController],
        "lists": ['views/dialogs/audit-list-view.html', AuditListController],
        "instruments": ['views/dialogs/audit-instrument-view.html', AuditInstrumentController]
    }
    $scope.auditsNames={
        "rules": "Reglas" ,
        "tables": "Tablas" ,
        "entitys": "Entidades" ,
        "catalogs": "Dominios" ,
        "formulas": "Formulas" ,
        "functions": "Funciones" ,
        "lists": "Listas" ,
        "instruments":"Instrumentos Normativos"
    }
    $scope.searchQuery ={
      user: "",
      method: "",
      type: "",
      objName: ""
    };

    $scope.gridOptionsSimple = {
        rowHeight: 36,
        data: [],
        enableFiltering: true,
        paginationPageSizes: [10, 20, 40],
        paginationPageSize: 10,
        enableCellEdit: true,
        enableGridMenu: true,
        columnDefs: [
            {field: 'name', displayName: 'Nombre'},
            {field: 'description', displayName: 'Descripcion'},
            {field: 'metod', displayName: 'Metodo'},
            {field: 'user', displayName: 'Usuario'},
            {
                cellTemplate: '<div class="ui-grid-cell-contents">{{row.entity.date | date: "dd/MM/yyyy H:m:s"}}</div>',
                name: 'Fecha',
                displayName: 'Fecha'
            },{
                cellTemplate: '<div class="ui-grid-cell-contents">{{grid.appScope.auditsNames[row.entity.type] | date: "dd/MM/yyyy H:m:s"}}</div>',
                name: 'Tipo',
                displayName: 'Tipo'
            },
            //{field: 'type', displayName: 'Tipo'},
            {
                cellClass: "center",
                exporterSuppressExport: true,
                enableSorting: false,
                enableFiltering: false,
                name: 'Acciones',width: 90, displayName: 'Acciones', cellTemplate: '<div class="btn-group">'
                + '<a ng-if="row.entity.type!=\'simulations\'" id="downloadButton" type="button" class="btn btn-success" ng-click="grid.appScope.visualizeData(row.entity)"><i class="fa fa-eye"></i><md-tooltip md-direction="left">Visualizar Datos</md-tooltip></a>'
                + '<a id="editbutton" type="button" class="btn btn-primary" ng-click="grid.appScope.visualizeRegistry(row.entity)"><i class="fa fa-eye"></i><md-tooltip md-direction="top">Visualizar Registro</md-tooltip></a></div>'
            }
        ]
    };

    $scope.visualizeRegistry = function(obj){
            $http({
                method: 'GET',
                url: dataService.commonUrl + '/' + dataService.getAuditoryRegistry + '/' + obj.this_id,
                headers: {
                    "Authorization": $scope.token
                }
            }).success(function(data,headers){
                if(data.success){
                    var parentEl = angular.element(document.body);
                    $mdDialog.show({
                        parent: parentEl,
                        templateUrl: 'views/dialogs/audit-registry-view.html',
                        locals: {
                            objData: data.response,
                        },
                        controller: AuditRegistryController
                  });
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

      var getUsers = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findAditoryUsers,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){
              $scope.auditoryUsers = data.response;
            }else{
              console.log(data.message)
              $scope.auditoryUsers = [];
            }

          });
      };

      $scope.searchData = function($event){
        $http({
            method: 'POST',
            url: dataService.commonUrl+'/'+dataService.searchAuditoryData,
            headers: {
                "Authorization": $scope.token
            },
            data: $scope.searchQuery
        }).success(function(data,headers){
            if(data.success){
                $scope.gridOptionsSimple.data = data.response;
                $scope.searchQuery ={
                    user: "",
                    method: "",
                    type: "",
                    objName: ""
                };
                $mdToast.show($mdToast.simple().content("Se han cargado los datos solicitados").position("top right").hideDelay(3000) );
            }else{
                dataService.showAlert("", data.message);
            }
        });
    }

    $scope.visualizeData = function(obj){
        $http({
            method: 'GET',
            url: dataService.commonUrl + '/' + dataService.getAuditoryData + '/' + obj.this_id,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){

                var parentEl = angular.element(document.body);
                $mdDialog.show({
                    parent: parentEl,
                    templateUrl: audit_views[data.response.tabla][0],
                    locals: {
                        objData: data.response.data,
                        ace: ace
                    },
                    controller: audit_views[data.response.tabla][1]
                });
            }else{
            }
          });
      }

    $scope.clearData = function(){
        $scope.gridOptionsSimple.data = []
    }

    var basicExec = function(){
        if($scope.securityMatrix.indexOf('AUDIT_MENU') == -1)
            $state.go('404');
    }


    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de escenarios"
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
            "description": "Esta pantalla se encarga de la administración de auditorias"
        },
        {
            "name": "¿Cual es la utilidad de las auditorias?",
            "description": "Se podra ver las acciones individuales de cada usuario operando con cada objeto de la plataforma desde el comienzo de la plataforma hasta el dia de la fecha."
        }
    ];
    basicExec();

    getUsers();

}]);
