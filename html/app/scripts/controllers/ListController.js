app.controller('ListController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog','$state',
						function(  $scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog,  $state) {

    $scope.activeTypesFull = {};
    $scope.activeTypes = [];
    // activetype = gridOptionsSimple.columnDefs[1].type
    $scope.types=[{
        name: 'texto (string)',
        type: 'string',
        varType: 'string'
    },{
        name: 'numero entero (integer)',
        type: 'number',
        varType: 'integer'
    },{
        name: 'numero decimal (float)',
        type: 'number',
        varType: 'float'
    },{
        name: 'Fecha',
        type: 'date',
        varType: 'date'
    }];
    $scope.activeType = $scope.types[0];

    var toaster = new function(){
        this.pop = function(type, title, message){
            message = message?message:"";
        	title = title?title:"";
        	$mdToast.show($mdToast.simple() .content(title+" "+message) .position("top right") .hideDelay(3000) );
        };
    };

    $scope.list= {
        id: null,
        name: "",
        description:"",
        list: true,
        elements: []
    };
    console.log(dataService.guid());
    $scope.$watch('list.list', function(newVal, oldVal){
        if($scope.list.elements.length > 1 && newVal === false){
        	toaster.pop("", "No es posible convertir la constante a elemento simple. Debe dejar solo un elemento para poder realizar la operacion");
        	$scope.list.list = true;
        }
    });

    $scope.addElement = function(element, index){
        if($scope.list.list || $scope.list.elements.length === 0){
            var val;
            switch($scope.gridOptionsSimple.columnDefs[1].type){
                case 'string': val = "Cambiar Valor"; break;
                case 'date': val = new Date(); break;
                case 'number': val = 0; break;
            }
            $scope.list.elements.push({
                "value": val,
                "id": dataService.guid(),
                "type": $scope.activeType.varType
            });
        }else{
            toaster.pop("", "No se pueden agregar elementos si la constante no es una lista, utilice el switch que lo habilita.");
        }
    };
    $scope.changedType = function(){
        for(var i in $scope.list.elements){
            var elem = $scope.list.elements[i];
            if(elem.type != $scope.activeType.varType){
                var confirm = $mdDialog.confirm()
                      .title('¿Está seguro que quieres cambiar el tipo de la constante?')
                      .content('Advertencia: Todos los elementos se borrarán')
                      .ariaLabel('Borrar elementos de la lista')
                      .ok('Aceptar')
                      .cancel('Cancelar');

                $mdDialog.show(confirm).then(
                  $scope.resetList(),
                  $scope.selectValidType(elem.type)
                );
                break;
            }
        }
        $scope.gridOptionsSimple.columnDefs[1].type = $scope.activeType.type;
    };
    $scope.selectValidType = function(varType){
      for(var j in $scope.types){
        var type = $scope.types[j];
        if(varType == type.varType){
          $scope.activeType = type;
          $scope.gridOptionsSimple.columnDefs[1].type = type.type;
       }
      }
    };
    $scope.parseValues = function(){
        if($scope.list.type == "date"){
            for(var i in $scope.list.elements){
                var elem = $scope.list.elements[i];
                elem.value = new Date(elem.value);
            }
        }
    }
    $scope.resetList = function(){
        $scope.list.elements = [];
        $scope.gridOptionsSimple.data = $scope.list.elements;
        //$scope.addElement();
    };
    $scope.removeElement = function(event, guid){
        for(var i in $scope.list.elements){
            if($scope.list.elements[i].id==guid){
                $scope.list.elements.splice(i,1);
                return;
            }
        }
    };
    $scope.viewSLA = function(){
        $scope.list.type = $scope.activeType.varType;
        $mdDialog.show({
            templateUrl: "views/dialogs/view-list-sla.html",
            controller: DialogController,
            locals: {
                list: $scope.list
            }
        });

        function DialogController($scope, $mdDialog,dataService, list) {
            var url = window.location.href.split("/");
            var url = url[0]+"//"+url[2];
            $scope.service = {
                url: url+"/"+dataService.saveList,
                method: "post",
                body: list
            }

            $scope.closeDialog = function() {
              $mdDialog.hide();
            }
        }

    };
    $scope.save = function(type){
        if($scope.list.name == "" || $scope.list.name == " "){
            toaster.pop("warning", "Es necesario ingresar un nombre para la lista");
        	return;
        }else{
            $scope.list.name = $scope.list.name.replace(/\s/g, "_").lowerFirstLetter();
        }
        if($scope.activeType.varType=='integer'){
            for(var i in $scope.list.elements){
                var elem = $scope.list.elements[i];
                elem.value = Number.parseInt(elem.value);
            }
        }

        $scope.list.type = $scope.activeType.varType;

        $http({
            method: 'POST',
            url: dataService.commonUrl+'/'+dataService.saveList,
            headers: {"Authorization": $scope.token},
            data: $scope.list
        }).success(function(data,headers){
            if(data.success){
                $mdToast.show($mdToast.simple().content("Guardado con exito").position("top right").hideDelay(3000));
                if(type=="goBack"){
                    $state.go('app.lists');
                }else{
                    $state.go('app.list', {list: data.response.id});
                }
        	}else{
        		$scope.list.elements.push({
        			"value": "",
        			"type": "string"
        		});
        		$mdToast.show($mdToast.simple().content("ERROR: "+data.message).position("top right").hideDelay(3000));
        	}
        });
    };

    var basicExec = function (){
        if($stateParams.list){
            $http({
    	   method: 'GET',
                url: dataService.commonUrl+'/'+dataService.findList+'/'+$stateParams.list,
                headers: {"Authorization": $scope.token}
            }).success(function(data,headers){
                if(data.success){
                    $scope.list.elements={};
                    $scope.list = data.response;
                    $scope.gridOptionsSimple.data = $scope.list.elements;
                    $scope.selectValidType($scope.list.type);
                    $scope.parseValues();
                }else{
                    $state.go("app.lists");
                }
            });
        }
    };

    $scope.goBack = function(){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Los cambios no guardados se perderán')
            .content('¿Esta seguro que desea volver?')
            .ok('Volver')
            .cancel('Cancelar');
        $mdDialog.show(confirm).then(function() {
        	$state.go("app.lists");
        });
    };

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de Constantes"
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
    $scope.getIndex = function(id){
        for(var i in $scope.list.elements){
            if($scope.list.elements[i].id == id){
                return i;
            }
        }
        return -1;
    }
    $scope.gridOptionsSimple = {
        //rowHeight: 36,
        data: $scope.list.elements,
        enableFiltering: true,//this
        paginationPageSizes: [10, 20, 40], //this
        paginationPageSize: 10, //this
        enableGridMenu: false,
        enableCellEdit: true, //this
        columnDefs:[
            {
                enableCellEdit: false,
                cellClass: "center",
                name:'number',
                displayName: '#',
                cellTemplate: '<div class="ui-grid-cell-contents"><b>{{grid.appScope.getIndex(row.entity.id)}}<b></div>',
                width:50,
                enableFiltering: false,
                enableSorting:false
            },
            {
                cellClass: "center",
                name: 'value', displayName: 'Valor (click para editar)',
                type: 'string'
            },
            {
                enableCellEdit: false,
                enableSorting: false,//this
                enableFiltering: false,//this
                exporterSuppressExport: true,
                cellClass: "center",
                name: 'Acciones',width: 100, displayName: 'Acciones', cellTemplate: '<a class="btn btn-danger" ng-click="grid.appScope.removeElement(row.entity.value, row.entity.id)"><i class="fa fa-trash"></a>'
            }
        ]
    };
    var faqs = [
        {
            "name": "¿Cual es el objetivo de esta pantalla?",
            "description": "Esta pantalla se encarga de la creación/modificación de Constantes que luego podrán ser usados en las reglas"
        },
        {
            "name": "¿Qué son los atributos?",
            "description": "Los atributos representan a cada uno de los campos contenidos en los objetos de datos"
        },
        {
           "name": "¿Qué tipos de datos son soportados por el sistema?",
            "description": "Los datos soportados por el sistema son: numeros enteros, numeros reales (con coma), texto, fechas y verdadero falso"
        },
        {
           "name": "¿Como edito los campos?",
            "description": "Todos los campos \"valor\" son editables, para ello, se requiere hacer doble click sobre el contenido del elemento, aparecerá un cuadro de texto donde se podrá introducir el valor deseado para el elemento."
        }
    ];

  	basicExec();

}]);
