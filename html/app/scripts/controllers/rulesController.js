app.controller('rulesController', ['$scope', 'uiGridConstants', '$localStorage', '$mdToast', 'dataService', '$http', '$mdDialog','i18nService',
                          function( $scope,   uiGridConstants,   $localStorage,   $mdToast,   dataService,   $http,   $mdDialog, i18nService ) {
	var rules = [];

    i18nService.setCurrentLang('es');
    cellTemplate = ''
        +'<a id="testBtn" md-ink-ripple type="button" class="btn btn-warning" ng-click="grid.appScope.getDRL($event, row.entity)"><md-tooltip>DRL</md-tooltip><i class="fa fa-terminal"></i>'
        +'</a> <a id="editBtn" type="button" class="btn btn-primary" ui-sref="app.rulesEditor({rule: row.entity.id})""><i class="fa fa-pencil"></i><md-tooltip>Editar regla</md-tooltip></a>'
        +'<a class="btn btn-primary" ng-click="grid.appScope.relatedEntities(row.entity)"><i class="fa fa-eye"></i><md-tooltip>Ver entidades que usa esta regla</md-tooltip></a>'
        +'<a class="btn btn-danger" ng-click="grid.appScope.delObj(row.entity)"><i class="fa fa-trash"></i></a>';


	$scope.gridOptionsSimple = {
        rowHeight: 36,
        data: rules,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableCellEdit: true, //this
        enableGridMenu: true,
        cellClass: "center",
        columnDefs: [
        	{field: 'name', displayName: 'Nombre'},
            {field: 'description', displayName: 'Descripcion'},
            {field: 'catalog.name', displayName: 'Dominio'},
            {field: 'user_name', displayName: 'Creador'},
            {
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                name: 'Acciones',width: 170, displayName: 'Acciones', cellTemplate: cellTemplate
            }
        ]
    };

    $scope.relatedEntities = function(rule){
        if(!rule)
            return;

        setNames = {};
        for(index in rule.rules){
            actual = rule.rules[index];

            if(actual.parentesis)
                continue;

            if(actual.type)
                if(setNames[actual.type] == undefined)
                    setNames[actual.type] = [];

            for(endex in actual.conds){
                if(actual.conds[endex].attr && setNames[actual.type].indexOf(actual.conds[endex].attr.name) == -1)
                    setNames[actual.type].push(actual.conds[endex].attr.name);
            }

        }

        $mdDialog.show({
            template:
                '<md-dialog aria-label="List dialog" flex="30">' +
                '   <md-toolbar class="md-primary">'+
                '       <div class="md-toolbar-tools">'+
                '           <h2>'+
                '           <span>Entidades relacionadas a la regla {{ruleName}}.</span>'+
                '           </h2>'+
                '       </div>'+
                '   </md-toolbar>'+
                '   <md-dialog-content>'+
                '       <div class="md-dialog-content">'+
                '          <ul class="list-group md-whiteframe-5dp">'+
                '             <li ng-repeat="(key, value) in data" class="list-group-item">{{key}}'+
                '               <ul id="mainList">'+
                '                   <li ng-repeat="item in value">'+
                '                       <span class="propper-form blue">'+
                '                           <span class="ng-binding ng-scope">Atributo: {{item}}</span>'+
                '                       </span>' +
                '                   </li>'+
                '               </ul>'+
                '             </li>'+
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
                     ruleName: rule.name
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
            .content('¿Esta seguro que desea borrar la regla?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.removeRule,
                headers: {
                    "Authorization": $scope.token
                },
                data: obj
            }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Regla borrada correctamente").position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }else{
                    $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
                    $scope.basicExec();
                }
            });
        });
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
            url: dataService.commonUrl+'/'+dataService.getRuleDRL,
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
            if(typeof rules != 'object'){
                $mdToast.show($mdToast.simple().content("Se cargaron datos de ejemplo").position("top right").hideDelay(3000));
                $localStorage.rules = [{
                    "name": "Regla de ejemplo",
                    "rules": [
                        {
                            "type": "entidad1",
                            "conds": [
                                {
                                    "attr": {
                                        "name": "titular",
                                        "type": "string"
                                    },
                                    "value": "",
                                    "operator": "en",
                                    "binding": "",
                                    "used": false,
                                    "connector": "&&",
                                    "memberOf": "lielist"
                                }
                            ],
                            "binding": "",
                            "connector": "AND"
                        }
                    ],
                    "cep": false,
                    "types": [
                        "AU10CRg2lIeTS2Iksjhp"
                    ],
                    "rule": "rule \"asdasda\"\r\n\twhen\r\n\t$PC: Constant() from entry-point \"pathfinder\"\r\n\tDeposito(titular memberOf $PC.lielist) from entry-point \"pathfinder\"\r\n\tthen\r\n\t\tSystem.out.print(\"Rule: asdasda\");\r\n\t\tDisablerRule.getInstance().disable(\"asdasda\");\r\n\tend",
                    "bindings": {},
                    "bindingRules": {},
                    "active": true,
                    "published": false,
                    "limited": true,
                    "enabled": true
                }];
            }
        }else{
             $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.findRules,
                headers: {"Authorization": $scope.token}
              }).success(function(data,headers){
                if(data.success)
                $scope.gridOptionsSimple.data = data.response;
              });
        }
    }
    $scope.basicExec();
}]);
