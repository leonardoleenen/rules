app.controller('FormulaController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$state', '$mdDialog', '$mdToast',function(  $scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $state,   $mdDialog,   $mdToast) {

    $scope.selectedItems = [];
    $scope.formula = {};
    $scope.wizard = {
        acumulators : ['SUMAR', 'MAXIMO', 'MINIMO', 'PROMEDIO', 'CONTAR'],
        step: 1,
        selected : {
            acumulator : {},
        }
    }

    var makeTheLine = function(){
        $scope.formula.selectedItems = $scope.selectedItems;
        $scope.formula.line = "";

        for(var i in $scope.selectedItems){
            var value = $scope.selectedItems[i];
            $scope.formula.line += " "+value.name;
        }
    }

    $scope.save = function(type){
        if($scope.formula.name==""||$scope.formula.name == undefined){
            $mdToast.show($mdToast.simple().content("El nombre de la formula no puede estar vacío").position("top right").hideDelay(3000) );
            return;
        }

        if(!$scope.validate()){
            return;
        }

        makeTheLine();

        $scope.formula.selectedItems = $scope.selectedItems;

        $http({
            method: 'POST',
            url: dataService.commonUrl+'/'+dataService.saveFormula,
            data: $scope.formula,
            headers: {
                "Authorization": $scope.token
            }
        }).success(function(data,headers){
            if(data.success){
                $mdToast.show($mdToast.simple().content("Guardado con exito.").position("top right").hideDelay(3000));

                if(type=="goBack"){
                    $state.go('app.formulas');
                }else{
                    $state.go('app.formula', {formula: data.response.id});
                }
            }else{
                $mdDialog.show(
                    $mdDialog.alert()
                    .parent(angular.element(document.body))
                    .title('Hubo un error')
                    .content('Motivo: '+data.message)
                    .ariaLabel('Dialog Alerta error')
                    .ok('Corregir!')
                );
            }
        });
    }

    $scope.validate = function(userTriggered){
        if($scope.selectedItems.length==0){
            $mdToast.show($mdToast.simple().content("Una Fórmula al menos debe contener un miembro.").position("top right").hideDelay(3000));
            return false;
        }

        if($scope.selectedItems[0].type == "operator"){
            $mdToast.show($mdToast.simple().content("Una formula no puede comenzar con un operador.").position("top right").hideDelay(3000));
            return false;
        }

        if($scope.selectedItems[$scope.selectedItems.length-1].type == "operator"){
            $mdToast.show($mdToast.simple().content("Una formula no puede terminar con un operador").position("top right").hideDelay(3000));
            return false;
        }

        for (var i=0; i<$scope.selectedItems.length;i++) {
            if($scope.selectedItems.length-1 > i){
                var posDetected = i+1;
                var curr = $scope.selectedItems[i];
                var next = $scope.selectedItems[posDetected];

                if(curr.type=="operator" && curr.type == next.type){
                    $mdToast.show($mdToast.simple().content("No se pueden poner dos operadores juntos. (Error en posición numero: "+posDetected+")").position("top right").hideDelay(3000));
            			return false;
                }

                if(curr.type=="acumulator" && curr.type == next.type){
                    $mdToast.show($mdToast.simple().content("No se pueden poner dos acumuladores juntos. (Error en posición numero: "+posDetected+")").position("top right").hideDelay(3000));
            			return false;
                }

                if((curr.type=="literal" && (curr.type == next.type || next.type == "acumulator"))|| curr.type=="acumulator" && next.type == "literal"){
                    $mdToast.show($mdToast.simple().content("No se pueden poner dos operandos juntos. (Error en posición numero: "+posDetected+")").position("top right").hideDelay(3000));
            			return false;
                }

                if(curr.type=="literal" && next.type == "acumulator"){
            	   $mdToast.show($mdToast.simple().content("No se pueden poner un acumulador junto a un literal sin un operador . (Error en posición numero: "+posDetected+")").position("top right").hideDelay(3000));
            			return false;
            	   }
        	}
        }

        if(userTriggered){
        	$mdToast.show($mdToast.simple().content("Expresion válida.").position("top right").hideDelay(3000));
        }

        return true;
    }

    var basicExec = function(){
        if($stateParams.formula){
            $http({
                method: 'GET',
                url: dataService.commonUrl+'/'+dataService.findFormula+'/'+$stateParams.formula,
                headers: {
                    "Authorization": $scope.token
                }
            }).success(function(data,headers){
                if(data.success){
                    $scope.formula = data.response;
                    $scope.selectedItems = data.response.selectedItems;
                }
            });
        }
    }

    $scope.goBack = function(){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Los cambios no guardados se perderán')
            .content('¿Esta seguro que desea volver?')
            .ok('Volver')
            .cancel('Cancelar')

        $mdDialog.show(confirm).then(function() {
        	$state.go("app.formulas");
        });
    }

    $scope.querySearch = function(query){
        var results = query ? $scope.items.filter(createFilterFor(query)) : [];

        if( !isNaN(query) || !isNaN( query.replace(",",".")) ){

            if(!isNaN(query.replace(",","."))){
                query = query.replace(",",".");
            }

            query = new Number(query);
            results.push({
                "name": query.valueOf(),
                "type" : "number"
            });
        }

        return results;
    }

    $scope.loadEntities = function(){
        $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findTypes,
            headers:{
                "Authorization": $scope.token
            }
        }).success(function(data,headers){
            if(data.success){
                $scope.entities = data.response;
                $scope.items = $scope.loadItems();
            }
        });
    }

    $scope.loadEntities();

    var buildAutocompleteList = function(){
        var list = [];
        var operators = ['SUMAR', 'MAXIMO', 'MINIMO', 'PROMEDIO', 'CONTAR'];

        angular.forEach($scope.entities, function(entity, keyE){
            angular.forEach(entity.plainAttr, function(attr, keyA){
                if((attr.type=="integer" || attr.type=="float") && (attr.name != "this")){
                    angular.forEach(operators, function(operator, keyO){
                        list.push({
                            name : operator+"("+entity.name+"."+attr.name+")",
                            entity : entity.id,
                            type: "acumulator",
                            acumulator : operator,
                            attr: attr
                        })
                    });
                }
        	});
        });

        return list;
    }
    $scope.loadItems = function(){
        var list = buildAutocompleteList();
        var items = [
            {
	   'name': '+',
                'type': 'operator'
            },
            {
                'name': '-',
                'type': 'operator'
            },
            {
                'name': '*',
                'type': 'operator'
            },
            {
                'name': '/',
                'type': 'operator'
            },
            {
                'name': '(',
                'type': 'open-parenthese'
            },
            {
                'name': ')',
                'type': 'close-parenthese'
            }];

        var allItems = items.concat(list);

        return allItems.map(function (item){
            item._lowername = item.name.toLowerCase();
            item._lowertype = item.type.toLowerCase();
            return item;
        });

    }

    $scope.postVerification = function(chip){
        var newChip = {};
        angular.copy(chip, newChip)
        return newChip;
    }



    function createFilterFor(query) {
        var lowercaseQuery = angular.lowercase(query);

        return function filterFn(item) {
            return (item._lowername.indexOf(lowercaseQuery) === 0) || (item._lowertype.indexOf(lowercaseQuery) === 0);
        };
    }

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de Formulas"
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
            "description": "Esta pantalla se encarga de la creación/modificación de formulas matemáticas que pueden ser usadas en las reglas"
        },
        {
            "name": "¿Qué son los acumuladores?",
            "description": "Los acumuladores son formulas pre definidas en el sistema que permiten la agrupación y contabilización de datos numericos"
        },
        {
           "name": "¿Como armo una formula?",
            "description": "La formula se debe armar por partes atomicas, es decir, por cada componenete ya sea numerico, operador o acumulador"
        },
        {
           "name": "Ya tengo mi formula armada, ¿Existe alguna forma de validarla?",
            "description": "Si, simplemente se hace click sobre el boton \"validar\" y se verificara la sintaxis de la formula. Adicionalmente, cuando se almacena la formula se realiza una validación sobre los miembros de la misma"
        }
    ];

    basicExec();

}]);
