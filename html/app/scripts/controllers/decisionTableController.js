app.controller('DecisionTableController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog', '$state', 'focus',
                                                      function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog,   $state, focus) {
	$scope.table = {
		"name":"",
		"entities" : [],
		"rows" : [],
		"default" : [],
		"different" : []
	}
	$scope.catalogs = [];
	$scope.catalog = [];
	$scope.bindings = {};
	$scope.instruments = [];
	$scope.SelectedInstruments = [];
	$scope.lists = {
		"integer": [],
		"float": [],
		"string": [],
		"date": []
	};

	$scope.loadCatalogs = function(){
		if(dataService.useStorage){
			$scope.catalogs = $localStorage.catalogs
		}else{
			$http({
				method : 'GET',
				url : dataService.commonUrl+'/'+dataService.findCatalogs,
				tracker : 'wait',
				headers : {
					'Authorization' : $scope.token
				}
			}).success(function(data) {
				if (data.success) {
					$scope.autoBindings();
					$scope.catalogs = data.response;
					if($stateParams.table!="" && $scope.catalog.length!=0){
						for(i in $scope.catalogs){
							if($scope.catalog[0] != undefined && $scope.catalogs[i].id == $scope.catalog[0].id){
								$scope.catalogs[i].ticked = true;
								break;
							}
						}
					}
				}
				$scope.loadLists();
				$scope.loadInstruments();
			});
		}
	};
	$scope.loadEntities = function(){
	    $http({
	        method: 'GET',
	        url: dataService.commonUrl+'/'+dataService.findTypes,
	        headers: {"Authorization": $scope.token}
	    }).success(function(data,headers){
	        if(data.success){
	            $scope.entities = data.response;
	        }
	    }).then(function(){
	    	$scope.loadCatalogs();
	    });
	}
	$scope.autoBindings = function(){
		var newBindings = {};
		angular.forEach($scope.table.entities, function(entity, key){
			angular.forEach(entity.entity.plainAttr, function(attr, key){
				var n = entity.entity.name+"."+attr.name;
				newBindings[n] = {
					name : n,
					type: attr.type
				}
			});
		});
		$scope.bindings = newBindings;
		$scope.buildConstantBindings();
		$scope.typeAheadList = returnTypeAheadList();
	};
	var returnTypeAheadList = function() {
		var arrReturn = [];
		for ( var ite in $scope.bindings) {
			arrReturn.push("$" + ite);
		}
		for ( var ite in $scope.bindingRules) {
			arrReturn.push("$" + ite);
		}
		return arrReturn;
	};
	$scope.addEntity = function ($event) {
		var parentEl = angular.element(document.body);
		$mdDialog.show({
			 parent: parentEl,
			 targetEvent: $event,
			 templateUrl: "views/dialogs/table-add-entity.html",
			 locals: {
				 entities: $scope.entities,
				 table: $scope.table,
			 },
			 controller: DialogController
		}).then(function(data){
			$scope.autoBindings();
		});
		function DialogController($scope, $mdDialog, entities, table) {
			$scope.entityToAdd = "";
			$scope.entities = entities;
			$scope.table = table;
			$scope.closeDialog = function() {
				$mdDialog.hide();
			}
			$scope.saveCond = function(){
				if($scope.entityToAdd == ""){
					$mdToast.show($mdToast.simple().content("Debe seleccionar una entidad para continuar").position("top right").hideDelay(3000) );
					return;
				}
				for (var i in table.entities) {
					var ent =table.entities[i];
					if($scope.entityToAdd.name == ent.entity.name){
						$mdToast.show($mdToast.simple().content("La entidad ya se encuentra agregada").position("top right").hideDelay(3000) );
						return;
					}
				};
				table.entities.push({
					"entity" : $scope.entityToAdd,
					"conds" : []
				});
				angular.forEach(table.rows, function(row, key){
					row.entities.push({
						conds:[]
					});
				})
				$mdDialog.hide();
			}
		}
	}
	$scope.addRow = function(){
		var entities = [];
		angular.forEach($scope.table.entities, function(entity, i){
			var conds = [];
			angular.forEach(entity.conds, function(cond, j){
				conds.push({
					"type": "none",
					"value": ""
				});
			});
			entities.push({
				"conds" : conds
			})
		});
		$scope.table.rows.push({
			"entities": entities,
			"actions" : []
		})
	}

	$scope.acceptCase = function(row){
		if(row.tempCase){
			row.case = row.tempCase;
			delete row.tempCase;
		}else{
			$mdToast.show($mdToast.simple().content("Debe introducir un valor en caso").position("top right").hideDelay(3000) );
		}
	}
	$scope.moveRowUp = function(index){
		var aux = {}
		angular.copy($scope.table.rows[index], aux);
		$scope.table.rows.splice(index-1,0,aux);
		$scope.table.rows.splice(index+1,1);
	}
	$scope.moveRowDown = function(index){
		var aux = {}
		angular.copy($scope.table.rows[index], aux);
		$scope.table.rows.splice(index+2,0,aux);
		$scope.table.rows.splice(index,1);
	}
	$scope.editCase = function(row){
		row.tempCase = row.case;
		delete row.case;
	}
	$scope.delRow = function(index){
		var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar la fila?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
			$scope.table.rows.splice(index,1);
        });

	}
	$scope.delRowCondition = function(rowCondition){
		rowCondition.type = "none";
		rowCondition.value = "";
		rowCondition.funct = undefined;
		rowCondition.formula = undefined;
		//$scope.refreshTable();
	}
	$scope.useCondition = function(rowCondition){
		rowCondition.type= "preNormal";
	}
	$scope.refreshTable = function(){
	    var tableCopy = {};
        angular.copy($scope.table, tableCopy);
        delete $scope.table;
        $scope.table = tableCopy;
	}
	$scope.editCondValue = function(rowCondition){
		rowCondition.type = "preNormal";
	}
	var searchBinding = function(value, type){
		var binding = $scope.bindings[value.slice(1,999)];

		if(binding && type==binding.type){
			return true;
		} else {
			return false;
		}
	}
	$scope.acceptValue = function (rowCondition, headCondition){
		//espacio para validaciones
		var h = headCondition;
		var r = rowCondition;

		if(rowCondition.value==""){
			$mdToast.show($mdToast.simple().content("Debe introducir un valor").position("top right").hideDelay(3000) );
			return;
		}

		if(r.value[0]=="$"){
			if(!searchBinding(r.value, h.attrType)){
				if($scope.bindings[r.value.slice(1,999)]){
					$mdToast.show($mdToast.simple().content("El enlace/variable que introdujo no es del mismo tipo al del atributo que esta intentando comparar").position("top right").hideDelay(3000) );
					return;
				}else{
					$mdToast.show($mdToast.simple().content("El enlace/variable que introdujo no existe").position("top right").hideDelay(3000) );
					return;
				}
			}
		}else{
			//es type integer y no es un numero valido muestra error de valor invalido
			if(h.attrType == "integer" && isNaN(r.value)){
					$mdToast.show($mdToast.simple().content("El valor que introdujo no es un número entero válido").position("top right").hideDelay(3000) );
					return;
			}
			//es type integer, es un numero pero tiene punto.
			if(h.attrType == "integer" && !isNaN(r.value)  && r.value.toString().indexOf('.') != -1 ){
					$mdToast.show($mdToast.simple().content("El valor que introdujo debe ser un numero entero (sin punto)").position("top right").hideDelay(3000) );
					return;
			}
			//Es type float y no es un numero valido
			if(h.attrType == "float" && isNaN(r.value)){
					$mdToast.show($mdToast.simple().content("El valor que introdujo no es un número válido").position("top right").hideDelay(3000) );
					return;
			}
			if(h.attrType == "object" && r.value!="null"){
					$mdToast.show($mdToast.simple().content("El valor que introdujo es inválido: Un objeto solo puede ser comparado con una variable ($...) o con null").position("top right").hideDelay(3000) );
					return;
			}
			if(h.attrType == "boolean" && !(r.value =="true" || r.value=="false" || r.value==true || r.value==false || r.value =="null")){
					$mdToast.show($mdToast.simple().content("El valor que introdujo es inválido: Un verdadero/falso solo puede ser comparado con \"true\" , \"false\" , una variable ($...) o con null").position("top right").hideDelay(3000) );
					return;
			}
		}
		rowCondition.type = "normal";
	}
	$scope.delCondition = function(entityIndex, conditionIndex){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar esta condición?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
            $scope.table.entities[entityIndex].conds.splice(conditionIndex, 1);
            for (var i in $scope.table.rows){
            	row = $scope.table.rows[i];
            	console.log("por eliminar"+entityIndex+conditionIndex);
            	row.entities[entityIndex].conds.splice(conditionIndex, 1);
            };
            $scope.refreshTable();
        });
	}
	$scope.addCondition = function($event, entity, index){
		var parentEl = angular.element(document.body);
		$mdDialog.show({
			 parent: parentEl,
			 targetEvent: $event,
			 templateUrl: "views/dialogs/table-add-condition.html",
			 locals: {
				 entity: entity,
				 table: $scope.table,
				 index : index
			 },
			 controller: DialogController
		});
		function DialogController($scope, $mdDialog, entity, table, index) {
			$scope.connectors = ["==", "!="];
			$scope.obj = {};
			$scope.entity = entity;
			$scope.closeDialog = function() {
				$mdDialog.hide();
			}
			$scope.changeConnectors = function(){
				if($scope.obj.attrToAdd.type=="integer" || $scope.obj.attrToAdd.type=="float"){
					$scope.connectors = ["==", ">", "<", "<=", ">=", "!=", "en", "no en"];
				}else if($scope.obj.attrToAdd.type=="date"){
					$scope.connectors = ["==", ">", "<", "<=", ">=", "!=", "en", "no en"];
				}else if($scope.obj.attrToAdd.type=="boolean"){
					$scope.connectors = ["==", "!="];
				}else{
					$scope.connectors = ["==", "!=", "en", "no en","comienza con", "termina con"];
				}
			};
			$scope.saveCond = function(){
				if(!$scope.obj.attrToAdd){
					$mdToast.show($mdToast.simple().content("Debe seleccionar un atributo para continuar").position("top right").hideDelay(3000) );
					return;
				}
				if(!$scope.obj.connector){
					$mdToast.show($mdToast.simple().content("Debe seleccionar un conector para continuar").position("top right").hideDelay(3000) );
					return;
				}
				for(var i in entity.conds){
					cond = entity.conds[i];
					if((cond.attribute == entity.entity.name+'.'+$scope.obj.attrToAdd.name)&&(cond.connector == $scope.obj.connector)){
						$mdToast.show($mdToast.simple().content("La condicion ya se encuentra agregada en la tabla.").position("top right").hideDelay(3000) );
						return;
					}
				}
				entity.conds.push({
					"type" : "normal",
					"attribute" : entity.entity.name+'.'+$scope.obj.attrToAdd.name,
					"connector": $scope.obj.connector,
					"attrType" : $scope.obj.attrToAdd.type
				});
				angular.forEach(table.rows, function(row, i){
					row.entities[index].conds.push({
						"type" : "none",
						"value" : ""
					})
				});
				$mdDialog.hide();
			}
		}
	}
	/*ESPECIFICO DE LLAMADO A EDITOR DE ENTIDADES*/
	$scope.entitiesExternal = true;
	$scope.entityEXT = {
		 "schema": {
			"type":"object",
			"properties":{}
		 },
				"name" : "",
				"description" : ""
	};
	$scope.isEnabled = true;
	$scope.addNewEntity = function(){
	$scope.displayEntity = true;
	$scope.entityEXT = {
		 "schema": {
			"type":"object",
			"properties":{}
		 },
			"name" : "",
			"description" : ""
	};
	$rootScope.$broadcast('ChangedEntity');
	}
	$scope.editEntity = function(){
		// $scope.entityEXT = angular.toJson(entitySTR);
		$rootScope.$broadcast('ChangedEntity');
		$scope.displayEntity= true;
	}
	$scope.actions = function($event, actions, index){
		var parentEl = angular.element(document.body);
		var entities = [];
		angular.forEach($scope.table.entities, function(entity, key){
			entities.push(entity.entity);
		});
		$mdDialog.show({
			 parent: parentEl,
			 targetEvent: $event,
			 templateUrl: "views/dialogs/table-actions.html",
			 locals: {
				 actions: actions,
				 table: $scope.table,
				 entities : entities,
				 index : index,
				 bindings : $scope.bindings
			 },
			 controller: DialogController
		});
		function DialogController($scope, $mdDialog, actions, entities, index, bindings) {
			$scope.obj = {
				value : ""
				//entityToAdd
				//attr
				//value
			}
			$scope.bindings = bindings;
			$scope.action = {};
			if(index>=0){
				$scope.action = actions[index];
				for(var i in entities){
					var entity = entities[i];
					if($scope.action.entity == entity.name){
						$scope.obj.entityToAdd = entity;
					}
				}
				for(var i in $scope.obj.entityToAdd.plainAttr){
					var plainAttr = $scope.obj.entityToAdd.plainAttr[i];
					if(($scope.action.attr.name == plainAttr.name) &&($scope.action.attr.type == plainAttr.type)){
						$scope.obj.attr = plainAttr;
					}
				}
				$scope.obj.value = $scope.action.value;
			}
			$scope.actions = actions;
			$scope.entities = entities;

			$scope.closeDialog = function() {
				$mdDialog.hide();
			};
			$scope.doIt = function (type){
				$scope.obj.type = type;
				$scope.action.type = type;

				if(type=="message"){
					focus("idMessage");
				}
			}
			$scope.save = function(){
				if($scope.action.type=="modify"){
					if(!$scope.obj.entityToAdd){
						$mdToast.show($mdToast.simple().content("Debe seleccionar una entidad para continuar").position("top right").hideDelay(3000) );
						return;
					}
					if(!$scope.obj.attr){
						$mdToast.show($mdToast.simple().content("Debe seleccionar un atributo para continuar").position("top right").hideDelay(3000) );
						return;
					}
					if($scope.obj.value==""){
						$mdToast.show($mdToast.simple().content("Debe introducir un valor para continuar").position("top right").hideDelay(3000) );
						return;
					}
				}
				var finalAction = {}
				var action = $scope.action;
				switch($scope.action.type){
					case "message":
						finalAction = {
								type : "message",
								value : $scope.obj.value
						}
					break;
					case "modify":
						finalAction = {
						type : action.type,
						attr : $scope.obj.attr,
						entity : $scope.obj.entityToAdd.name,
						value : $scope.obj.value
						}
					break;
					case "funct":
						finalAction = {
						type : action.type,
						attr : $scope.obj.attr,
						funct: action.funct,
						entity : $scope.obj.entityToAdd.name,
						value : $scope.obj.value
						}
					break;
					case "formula":
						finalAction = {
						type : action.type,
						attr : $scope.obj.attr,
						formula: action.formula,
						entity : $scope.obj.entityToAdd.name,
						value : $scope.obj.value
						}
					break;

				}
				if(action.type != undefined){
					if(index==-1){
						actions.push(finalAction);
					}else{
						actions[index] = finalAction;
					}
					$mdDialog.hide();
				}
			}
			$scope.addFunction = function ($event, cond) {
				 var parentEl = angular.element(document.body);
				 console.log($scope.bindings);
				 cond.attr = $scope.obj.attr;
				 $mdDialog.show({
					 parent: parentEl,
					 templateUrl: "views/dialogs/function-rule.html",
					 locals: {
						 bindings: $scope.bindings,
						 cond: cond,
					 },
					 controller: FunctionRuleController
				}).then(function(){
					if(cond.funct){
						cond.type="funct";
					}
					if(cond.formula){
						cond.type="formula";
					}
					$scope.save();
				});
			}
		}
	}
	var asignInstruments = function(){
		if($scope.SelectedInstruments){
			$scope.table.instruments = $scope.SelectedInstruments
		}
	}

	//servicio para devolucion de datos, puede usarse externamente.
	$rootScope.getJson = function(){
		asignInstruments();
		return $scope.table;
	}
	$scope.save = function(type){
		if($scope.catalog.length!=0)
			$scope.table.catalog = $scope.catalog[0];

		for(var i in $scope.table.rows){
			var row = $scope.table.rows[i];
			if(row.tempCase||!row.case){
				$mdToast.show($mdToast.simple().content("Hay al menos un caso que no esta definido, revise").position("top right").hideDelay(3000));
				return;
			}
		}
		asignInstruments(); //asigna instrumentos con f()
		return $http({
		  method : 'POST',
		  url : dataService.commonUrl+'/'+dataService.saveTable,
		  headers : {
			'Authorization' : $scope.token
		  },
		  data: $scope.table
		}).success(function(data) {
		  if (data.success) {
		  	$mdToast.show($mdToast.simple().content("La tabla de decisiones ha sido almacenada con exito").position("top right").hideDelay(3000) );
    	    if(type=="goBack"){
    	    	$state.go('app.decisionTables');
    	    }else{
				$state.go('app.decisionTable', {table: data.response.id},{reload:true});
    	    }
		  	return data;
		  } else {
		  	$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
		  }
		}).error(function(data) {
		  $mdToast.show($mdToast.simple().content("Hubo un problema y no se pudo guardar").position("top right").hideDelay(3000) );
		});
	}
	$scope.goBack = function(){
		var confirm = $mdDialog.confirm()
	        .parent(angular.element(document.body))
	        .title('Los cambios no guardados se perderán')
	        .content('¿Esta seguro que desea volver?')
	        .ok('Volver')
	        .cancel('Cancelar')
	    $mdDialog.show(confirm).then(function() {
	    	$state.go("app.lists");
	    });
	}
	$scope.delAction = function($event, actions, index){
		var confirm = $mdDialog.confirm()
	        .parent(angular.element(document.body))
	        .title('Confirmacion de borrado')
	        .content('¿Esta seguro que desea borrar la acción?')
	        .ok('Borrar')
	        .cancel('Cancelar')
	    $mdDialog.show(confirm).then(function() {
	    	actions.splice(index, 1);
	    });
	}
	$scope.basicExec = function(){
		if(dataService.useStorage){
			//traer tablas de localstorage
		}else{
			if($stateParams.table){
				$http({
					method: 'GET',
					url: dataService.commonUrl+'/'+dataService.findTable+'/'+$stateParams.table,
					headers: {"Authorization": $scope.token}
				}).success(function(data,headers){
					if(data.success){
					  $scope.table = data.response;
					  if(angular.isUndefined($scope.table.default)){
					  	$scope.table.default = [];
					  }
					  if(angular.isUndefined($scope.table.different)){
					  	$scope.table.different = [];
					  }
					  $scope.catalog.push($scope.table.catalog);
					  if ($scope.table.instruments)
					  	$scope.SelectedInstruments = $scope.table.instruments;
					}
				});
			}
			$scope.loadEntities();
		}
	}
	$scope.goBack = function(){
	    	$state.go("app.decisionTables");
	}


	$scope.delEntity = function($event, entity, index){
		if($scope.table.entities.length==1 && $scope.table.rows.length != 0){
			dataService.showAlert("No se puede remover la entidad", "No se pudo remover la entidad debido a que es la unica agregada en la tabla y tambien hay filas agregadas a la misma.")
		    return;
		}
		var confirm = $mdDialog.confirm()
	        .parent(angular.element(document.body))
	        .title('Eliminar entidad de la tabla de decisiones.')
	        .content('¿Esta seguro que desea continuar?')
	        .ok('Continuar')
	        .cancel('Cancelar')
	    $mdDialog.show(confirm).then(function() {
	    	$scope.table.entities.splice(index,1);
	    	angular.forEach($scope.table.rows, function(row, key){
	    		row.entities.splice(index,1);
	    	}).then(function(){
	    		$scope.autoBindings();
	    	});
	    });
	}
	$scope.addFunction = function ($event, cond) {
		 var parentEl = angular.element(document.body);
		 console.log($scope.bindings);

		 $mdDialog.show({
			 parent: parentEl,
			 targetEvent: $event,
			 templateUrl: "views/dialogs/function-rule.html",
			 locals: {
				 bindings: $scope.bindings,
				 cond: cond,
			 },
			 controller: FunctionRuleController
		}).then(function(){
			if(cond.funct){
				cond.type="funct";
			}
			if(cond.formula){
				cond.type="formula";
			}
		});
	}

	$scope.loadLists = function(){
		$http({
			method: 'GET',
			url: dataService.commonUrl+'/'+dataService.findLists,
			headers: {
				"Authorization": $scope.token
			}
		}).success(function(data,headers){
			$scope.constants = [];
			if(data.success){
			  for(var i in data.response){
			  	var list = data.response[i];
				if(list.list){
					$scope.lists[list.type].push(list);
				}else{
					$scope.constants.push(list);
				}
			  }
			}
			$scope.autoBindings();
		});
	}

	$scope.buildConstantBindings = function(){
		angular.forEach($scope.constants, function(value, key){
			var bindingName = "PC."+value.name;
			var bindingType = value.elements[0].type;
			$scope.bindings[bindingName] = {
				name : bindingName,
				type : bindingType
			}
		});
		/*triggerTypeAhead();*/
	}

	$scope.loadInstruments = function(){
		$http({
			method : 'GET',
			url : dataService.commonUrl+'/'+dataService.findNormatives,
			tracker : 'wait',
			headers : {
				'Authorization' : $scope.token
			}
		}).success(function(data) {
			if (data.success) {
				$scope.instruments = data.response;

				if($stateParams.table != "" && $scope.SelectedInstruments.length!=0){
					for(i in $scope.instruments){
						for(e in $scope.SelectedInstruments){
							if($scope.instruments[i].id == $scope.SelectedInstruments[e].id){
								$scope.instruments[i].ticked = true;
								break;
							}
						}
					}
				}

			}
		});
	};
	$scope.handleDate = function(cond, $event) {
        var parentEl = angular.element(document.body);
        $mdDialog.show({
         parent: parentEl,
         targetEvent: $event,
         templateUrl: "views/dialogs/handle-date.html",
         locals: {
           cond: cond,
           bindings: $scope.bindings,
           typeAheadList: $scope.typeAheadList,
         },
         controller: "HandleDateController"
	    });
	}

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Tabla de decisiones"
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
            "description": "Esta pantalla se encarga de la creación/modificación de Tablas de decisiones"
        },
        {
            "name": "¿Cual es la utilidad de las tablas de decisiones?",
            "description": "las tablas tienen la utilidad de funcionar como multiples reglas relacionadas entre si en un mismo editor, puede simbolizar una tabla de verdad, o incluso representar una hoja de calculo compleja."
        },
        {
           "name": "¿Como comienzo a utilizarla?",
            "description": "El funcionamiento es simple. Primero se debe agregar una entidad para comenzar a operar con ella, para realizar esto, tenemos que hacer click en agregar entidad, seleccionamos una y presionamos agregar, luego ya se nos genera la tabla en la cual podemos agregar condiciones y acciones."
        },
        {
           "name": "¿Como agrego una condición?",
            "description": "Solo se necesita hacer click sobre el boton +Condición al lado de la entidad que agregó a la tabla previamente, allí podrá seleccionar que atributo y que conector van a identificar a la acción a realizar.."
        },
        {
           "name": "¿Como agrego una accion?",
            "description": "Solo se necesita hacer click sobre el boton \"agregar nueva\"  en la columna de acciones de la fila que desee que realize estas acciones, puede definir una o varias acciones por fila"
        },{
           "name": "¿Cuales son las acciones disponibles y para que sirven?",
            "description": "Disponemos de dos acciones, la primera es Generar un mensaje, el cual va a escribir un mensaje en la salida del procesamiento, luego está la accion modificar un campo, el cual realiza una modificación en el objeto de datos ingresante a la ejecución y poniendole el valor que usted introdujo."
        }

    ];
	$scope.basicExec();
}]);
