app.controller('DecisionTablesController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', "$location","dataService","$http", "$mdDialog",'i18nService',
                                    function($scope,   uiGridConstants,   $localStorage,   $mdToast,   $location,  dataService,  $http,   $mdDialog, i18nService) {

    $scope.desicionTables = [];

    cellTemplate = ''
        +'<a id="testBtn" md-ink-ripple type="button" class="btn btn-warning" ng-click="grid.appScope.getDRL($event, row.entity)"><md-tooltip>DRL</md-tooltip><i class="fa fa-terminal"></i></a>'
        +'<a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.decisionTable({table: row.entity.id})""><i class="fa fa-pencil"></i> <md-tooltip>Editar tabla</md-tooltip></a>'
        +'<a class="btn btn-primary" ng-click="grid.appScope.relatedEntities(row.entity)"><i class="fa fa-eye"></i><md-tooltip>Ver entidades que usa esta tabla</md-tooltip></a>'
        +'<a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></a>'

    i18nService.setCurrentLang('es');

    $scope.gridOptionsSimple = {
        rowHeight: 36,
        data: $scope.desicionTables,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableGridMenu: true,
        enableCellEdit: true, //this
        columnDefs: [
        	{field: 'name', displayName: 'Nombre'},
            {field: 'description', displayName: 'Descripcion'},
            {field: 'user_name', displayName: 'Creador'},
            {
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                name: 'Acciones',width: 170, displayName: 'Acciones', cellClass: "center", cellTemplate: cellTemplate
            }
        ]
    };

    $scope.relatedEntities = function(table){
        if(!table)
            return;

        setNames = {};

        for(var index in table.entities){
            var actual = table.entities[index];

            if(actual.entity && actual.entity.name)
                if(setNames[actual.entity.name] == undefined)
                    setNames[actual.entity.name] = [];

            for(endex in actual.conds){
                attr = actual.conds[endex].attribute.substring(actual.conds[endex].attribute.indexOf('.')+1);
                if(setNames[actual.entity.name].indexOf(attr)==-1)
                    setNames[actual.entity.name].push(attr);
            }

        }

        $mdDialog.show({
            template:
                '<md-dialog aria-label="List dialog" flex="30">' +
                '   <md-toolbar class="md-primary">'+
                '       <div class="md-toolbar-tools">'+
                '           <h2>'+
                '           <span>Entidades relacionadas a la tabla {{ruleName}}.</span>'+
                '           </h2>'+
                '       </div>'+
                '   </md-toolbar>'+
                '   <md-dialog-content>'+
                '       <div class="md-dialog-content">'+
                '          <ul class="list-group md-whiteframe-5dp">'+
                '               <li ng-repeat="(key, value) in data" class="list-group-item">{{key}}'+
                '                   <ul id="mainList">'+
                '                       <li ng-repeat="item in value">'+
                '                           <span class="propper-form blue">'+
                '                               <span class="ng-binding ng-scope">Atributo: {{item}}</span>'+
                '                           </span>' +
                '                       </li>'+
                '                   </ul>'+
                '                </li>'+
                '          <ul>'+
                '       </div>'+
                '   </md-dialog-content>' +
                '   <div class="md-actions">' +
                '       <md-button ng-click="accept()" class="md-primary">' +
                '       Cerrar' +
                '       </md-button>' +
                '   </div>' +
                '</md-dialog>',
                   locals: {
                     data: setNames,
                     ruleName: table.name
                   },
                   controller: DialogController
                });
        function DialogController($scope, $mdDialog, data, ruleName) {
            $scope.data = data;
            $scope.ruleName = ruleName;

            $scope.accept = function() {
                $mdDialog.hide();
            };
        }

    };

    $scope.delObj = function(obj){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta tabla?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeTable,
                headers: {"Authorization": $scope.token},
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Tabla borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdToast.show($mdToast.simple().content("La tabla no pudo ser borrada: "+data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }
            });
        })
    };

     $scope.getDRL = function($event,obj){

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
        $http({
            method: 'POST',
            url: dataService.commonUrl+'/'+dataService.getTableDRL,
            headers: {"Authorization": $scope.token},
            data: obj
        }).success(function(data,headers){
            $mdDialog.show({
                parent: parentEl,
                targetEvent: $event,
                templateUrl: "views/dialogs/drl-view.html",
                locals: {
                    result: data
                },
                controller: DialogController
            });
        });
    };

    $scope.basicExec = function(){
        if(dataService.useStorage){
            $scope.desicionTables = $localStorage.desicionTables;
        }else{
             $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.findTables,
                headers: {"Authorization": $scope.token}
              }).success(function(data,headers){
                if(data.success){
                    $scope.gridOptionsSimple.data = data.response;
                }
            });
        }
    };

    $scope.basicExec();

}]);
