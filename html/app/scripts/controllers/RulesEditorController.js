app.controller('RulesEditorController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$state' , '$localStorage', '$rootScope', '$mdDialog', 'focus',
								function($scope,    $http,   dataService,   $stateParams,  $mdToast,   $state,    $localStorage,   $rootScope,   $mdDialog, focus) {
	var commonUrl = dataService.commonUrl;
	var findEvents = commonUrl + "/rest/event/types/all"; // get
	var doTestUrl = commonUrl + "/rest/rule/stage/test"; // post
	var getScenariosUrl = commonUrl + "/rest/rule/stage/all"; // get
	var urlRetrieveRule = commonUrl + "/rest/rule/"; //+ $routeParams.rule; // get
	$scope.connSelectable = ["==", ">", "<", "<=", ">=", "!=", "entre", "en", "no en", "contiene"];
	$scope.connSelectableOther = ["==", "!=", "en", "no en", "contiene"];
	$scope.connSelectableString = ["==", "!=", "en", "no en", "contiene", "comienza con", "termina con"];
	$scope.connSelectableDate = ["==", ">", "<", "<=", ">=", "!=", "en", "no en"];
	$scope.tempOperators = [ "before", "meets", "overlaps", "finishes", "includes", "starts", "coincides", "after", "metBy", "overlappedBy", "finishedBy", "during", "finishes" ];
	var urlRetrieveLists = commonUrl+ "/rest/lists?col=name&iDisplayStart=0&iDisplayLength=100";
	$scope.booleans = [{
		"name" : "Null",
		"value" : "null"
	},{
		"name" : "Verdadero",
		"value" : "true"
	},{
		"name" : "Falso",
		"value" : "false"
	},{
		"name" : "Enlace/binding",
		"value" : ""
	}];
	$scope.constants={};
	$scope.parentheses = false; //indica la presencia de un parentesis abierto.
	$scope.entitiesExternal = true;
	$scope.typeAheadConstants = [];
	$scope.entityEXT = {
		 "schema": {
		 	"type":"object",
		 	"properties":{}
		 },
        "name" : "",
        "description" : ""
	};
	$scope.lists = {
		"integer": [],
		"float": [],
		"string": [],
		"date": []
	};
	$scope.constants = [];
	$scope.actions = [];
	$scope.isEnabled = true;
	$scope.rules = [];
	$scope.typeAattr = [];
	$scope.eventTypes = [];
	$scope.bindings = {};
	$scope.time = {};
	$scope.bindingRules = {};
	$scope.salience = 0;
	$scope.noloop = false;
	$scope.cepRulesCount = 0;
	$scope.published = false;
	$scope.advanced = false;
	$scope.catalogs = [];
	$scope.instruments = [];
	$scope.SelectedInstruments = [];
	$scope.catalog = [];
	$scope.atomic = false;
	//$scope.id = $routeParams.rule;
	$scope.isLimited = false;
	var toaster = new function(){
		this.pop = function(type, title, message){
			message = message?message:"";
			title = title?title:"";
			//type useless
			$mdToast.show($mdToast.simple() .content(title+" "+message) .position("top right") .hideDelay(3000) );
		};
	};
	$scope.addAction = function(value){
		if(value=="modify"){
			$scope.actions.push({
				binding: "",
				value: ""
			});
		}
		if(value=="message"){
			$scope.actions.push({
				message: true,
				value: ""
			});
			focus("idMessage-" + ($scope.actions.length-1));
		}
	};
	$scope.removeAction = function(index){
		$scope.actions.splice(index,1);
	};


	$scope.loadCatalogs = function(){
		if(dataService.useStorage){
			$scope.catalogs = $localStorage.catalogs;
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
					$scope.catalogs = data.response;
					if($stateParams.rule !== "" && $scope.catalog.length !== 0){
						for(var i in $scope.catalogs){
							if($scope.catalogs[i].id == $scope.catalog[0].id){
								$scope.catalogs[i].ticked = true;
								break;
							}
						}
					}
				}
			});
		}
	};

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

				if($stateParams.rule !== "" && $scope.SelectedInstruments.length !== 0){
					for(var i in $scope.instruments){
						for(var e in $scope.SelectedInstruments){
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

	$scope.completeType = function(newObj, oldObj){
		angular.forEach(newObj.plainAttr, function(newValue, newValue){
			var found = false;
			angular.forEach(oldObj.plainAttr, function(oldValue, newKey){
				if(newValue.name == newValue.name){
					found = true;
				}
				// if(found==false&&newValue.name==oldValue.name&&newValue.type!=oldValue.type){ //si nombre es el mismo pero tipo distinto significa que cambio el tipo
				// 	oldValue.type = newValue.type;
				// 	oldValue.recognized = true;
				// 	found=true;
				// }
				// if(found==false&&newValue.name==oldValue.name&&newValue.type==oldValue.type){
				// 	found=true;
				// }
			});
			if(!found){
				console.log("not found "+newObj);
				oldObj.plainAttr.push(newValue);
			}
		});
		angular.forEach(oldObj.plainAttr, function(oldValue, oldKey){
			if(!oldValue.recognized){
				delete oldValue;
			}
		});
	};

	$scope.$on("remoteEntitySaved", function(event, data){
		$http({
	        method: 'GET',
	        url: dataService.commonUrl+'/'+dataService.findTypes,
	        headers: {"Authorization": $scope.token}
	      }).success(function(data,headers){
	        if(data.success){
	        	$scope.eventTypes = data.response;
	        	var aux = $scope.prepareRulesForPlugin();
	        	$scope.rules = [];
	        	rearmarReglas(aux);
	        }
	      });

	});

	$scope.$safeApply = function($scope, fn){
		fn = fn || function(){};
		if($scope.$$phase){
			fn();
		}else{
			$scope.$apply(fn);
		}
	};

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
	};

	$scope.editEntity = function(){
		$rootScope.$broadcast('ChangedEntity');
		$scope.displayEntity= true;
	};

	$scope.removeBinding = function(binding) {
		if (typeof $scope.bindings[binding] != "undefined") {
			//console.log("Borrado binding: " + binding);
			delete $scope.bindings[binding];
		}
	};

	$scope.removeRuleBinding = function(rule) {
		if (typeof $scope.bindingRules[rule.binding] != "undefined") {
			//console.log("Borrado binding: " + rule.binding);
			for ( var ite in rule.rawType.plainAttr) {
				var attr = rule.rawType.plainAttr[ite];
				$scope.removeBinding(rule.binding + "." + attr);
			}
			delete $scope.bindingRules[rule.binding];
		}
	};

	$scope.bindThis = function(bindeable, rule) {
		if (typeof bindeable.binding != "undefined") {
			$scope.binding = bindeable.binding;
			$scope.bindReplace = bindeable.binding;
		} else {
			$scope.binding = "";
			$scope.bindReplace = undefined;
		}
		$scope.bindingRule = rule; // referencia a booleano que indica si es una regla
		$scope.bindeable = bindeable;
		$('#modalBinding').modal('show');
	};

	$scope.saveBinding = function(userTriggered) {
		if ($scope.bindingRule) {
			$scope.bindeable.used = true;
			if ($scope.bindReplace) {
				if ($scope.bindeable.type) {
					var aux = $scope.binding;
					if ($scope.bindReplace.substring(0, 1) == "$") {
						$scope.bindeable.binding = $scope.bindReplace
								.substring(1, 99);
					} else {
						$scope.bindeable.binding = $scope.bindReplace;
					}
					$scope.removeRuleBinding($scope.bindeable);
				}
			}
			$scope.bindingRules[$scope.binding] = {
				"name" : $scope.binding,
				"type" : "object"
			};
			for ( var ite in $scope.bindeable.rawType.plainAttr) {
				var attr = $scope.bindeable.rawType.plainAttr[ite];
				if (attr.name != "this")
					$scope.bindings[$scope.binding + "." + attr.name] = {
						"name" : $scope.binding + "." + attr.name,
						"type" : attr.type
					};
			}
			//console.log($scope.bindingRules);
		} else {
			if ($scope.bindReplace.substring(0, 1) == "$") {
				$scope.removeBinding($scope.bindReplace.substring(1, 99));
			} else {
				$scope.removeBinding($scope.bindReplace);
			}
			$scope.bindings[$scope.binding] = {
				"tag" : $scope.binding
			};
		}
		$scope.bindeable.binding = $scope.binding;
		triggerTypeAhead();
		$('#modalBinding').modal('hide');
		$scope.triggerTooltip();
		if(userTriggered){
			$scope.autoBindings();
		}
	};

	$scope.triggerTooltip = function(){
		$scope.$safeApply($scope, function() {
			setTimeout(function() {
				$('[data-toggle="tooltip"]').tooltip('destroy');
				$('[data-toggle="tooltip"]').tooltip();
			}, 1000);
		});
	};

	$scope.removeCond = function(rule, $index) {
		if (typeof rule.cep != "undefined") {
			$scope.cepRulesCount--;
		}
		if (typeof rule.conds[$index].binding != "undefined")
			$scope.removeBinding(rule.conds[$index].binding);
		rule.conds.splice($index, 1);
	};

	$scope.removeRule = function($index) {
		if ($scope.rules[$index].windowTime)
			$scope.cepRulesCount--;
		if(!$scope.rules[$index].parentesis)
			$scope.removeRuleBinding($scope.rules[$index]);
		else
			$scope.parentheses = !$scope.parentheses;
		$scope.rules.splice($index, 1);
		$scope.autoBindings();
	};

	$scope.addCondNoVerif = function(rule, $index) {
		triggerTypeAhead();
		rule.conds.push({
			"attr" : "",
			"value" : "",
			"operator" : "==",
			"connector" : "&&",
			"binding": ""
		});
		$scope.triggerTooltip();
		$mdToast.show({
	      template: function(){
	      	return "<b> a </b>";
	      },
	      hideDelay: 6000,
	      position: "top right"
	    });
	};

	$scope.addCond = function(rule, $index) {

		if (typeof rule.conds[$index].cep == "undefined") {
			var type = rule.conds[$index].attr.type;
			var data = rule.conds[$index].value;
			var operator = rule.conds[$index].operator;


			//CHEQUEOS QUE PERDIERON VALIDEZ POR CAMBIO DE PARADIGMA MAS USER FIRENDLY (PF LIMITADO-> A REGLAS +FREEDOM)
			// checks... y verificaciones.
			// if(rule.conds[$index].operator != "en" && rule.conds[$index].operator != "en"){
			// 	switch (type) {
			// 	case "object":
			// 		if(data.substring(1) in $scope.bindings && $scope.bindings[data.substring(1)].type == type)
			// 			break;
			// 		if (data != "null"	&& typeof $scope.bindingRules[data.substring(1, 99)] == "undefined") {
			// 			toaster.pop("warning","","Un objeto solo puede ser comparado con null u otro objeto");
			// 			return;
			// 		}
			// 		if (operator != "!=" && operator != "==") {
			// 			toaster.pop("warning", "","Un objeto solo puede ser comparado con operadores '==' ó '!='");
			// 			return;
			// 		}
			// 		break;
			// 	case "string":
			// 		if(data.substring(1) in $scope.bindings && $scope.bindings[data.substring(1)].type == type)
			// 			break;
			// 		if (operator != "!=" && operator != "==") {
			// 			toaster.pop("warning", "","Un texto solo puede ser comparado con operadores '==' ó '!='");
			// 			return;
			// 		}
			// 		break;
			// 	case "boolean":
			// 		if(data.substring(1) in $scope.bindings && $scope.bindings[data.substring(1)].type == type)
			// 			break;
			// 		if (data != "true" && data != "false") {
			// 			toaster.pop("warning", "","Un booleano solo puede ser comparado con true y false");
			// 			return;
			// 		}
			// 		if (operator != "==") {
			// 			toaster.pop("warning", "","Un booleano solo puede ser comparado con operador '==' ");
			// 			return;
			// 		}
			// 		break;
			// 	case "integer":
			// 		if((data.substring(1) in $scope.bindings)&&($scope.bindings[data.substring(1)].type == 'number' || $scope.bindings[data.substring(1)].type == 'integer' ))
			// 			break;
			// 		if(isNaN(data)&&!rule.conds[$index].formula&&!rule.conds[$index].funct) {
			// 			toaster.pop("warning", "","Un numero solo puede ser comparado con otro numero");
			// 			return;
			// 		}
			// 		break;
			// 	case "array":
			// 		if(data.substring(1) in $scope.bindings && $scope.bindings[data.substring(1)].type == type)
			// 			break;
			// 		if (data != "null") {
			// 			toaster.pop("warning", "", "Un arreglo solo puede ser comparado con null");
			// 			return;
			// 		}
			// 		if (operator != "!=" && operator != "==") {
			// 			toaster .pop("warning", "", "Un arreglo solo puede ser comparado con operadores '==' ó '!='"); return;
			// 		}
			// 		break;
			// 	}
		} else {
			if ((rule.conds[$index].cep.startTime == "")
					|| (rule.conds[$index].cep.endTime == "")
					|| (rule.conds[$index].cep.tempOperator == "")
					|| (rule.conds[$index].cep.bindingTo.trim() == "")) {
				toaster.pop("danger", "Error", "campos vacíos, verifique");
				return;
			}
		}
		$scope.addCondNoVerif(rule, $index);
	};
	$scope.addCep = function(cond) {
		cond.cep = {
			"startTime" : "0h0m0s",
			"endTime" : "0h0m0s",
			"tempOperator" : "after",
			"bindingTo" : ""
		};
		$scope.cepRulesCount++;
	};
	$scope.addParentheses = function(){
		$scope.rules.push({
			"parentesis" : true
		});
		$scope.parentheses = !$scope.parentheses;
	}
	$scope.addRule = function() {
		triggerTypeAhead();
		$scope.triggerTooltip();
		$scope.rules.push({
			type : undefined,
			conds : [],
			connector: "AND"
		});
	};
	$scope.parenthesesUp = function(index){
		var aux = {}
		angular.copy($scope.rules[index], aux);
		$scope.rules.splice(index-1,0,aux);
		$scope.rules.splice(index+1,1);
	}
	$scope.parenthesesDown = function(index){
		var aux = {}
		angular.copy($scope.rules[index], aux);
		$scope.rules.splice(index+2,0,aux);
		$scope.rules.splice(index,1);
	}
	$scope.prepareRulesForPlugin = function() {
		var rules = [];
		var bindAux;
		var typesID = [];
		var condAux = [];
		for ( var ite in $scope.rules) {
			var rule = $scope.rules[ite];
			condAux = [];
			if(rule.parentesis){
				rules.push(rule);
				continue;
			}
			if (typeof rule.binding != "undefined"
					&& rule.binding != "") {
				if (rule.binding.substring(0, 1) == "$")
					bindAux = rule.binding;
				else
					bindAux = "$" + rule.binding;
			} else {
				bindAux = "";
			}
			for ( var iteCond in rule.conds) {
				var cond = rule.conds[iteCond];
				if (!cond.cep) {
					var value = "";

					// if(cond.attr.type == "date"){
					// 	value = new Date(cond.value);
					// }else{
					// 	value = cond.value;
					// }

					if ((cond.attr != ""&& cond.value != ""&& cond.operator != "")||(cond.memberOf != undefined)) {
						condAux.push({
							"attr" : cond.attr,
							"value" : cond.value,
							"value2" : cond.value2,
							"operator" : cond.operator,
							"binding" : (typeof cond.binding == "undefined" || cond.binding == "$") ? "": (cond.binding.substring(0, 1) == "$" ? cond.binding: cond.binding.length>0?"$"+ cond.binding:""),
							"used" : cond.used ? true: false,
							"connector": cond.connector,
							"memberOf" : cond.memberOf,
							"formula" : cond.formula,
							"funct" : cond.funct
						});
					}
				}
			}
			rules.push({
				type : $scope.rules[ite].rawType.name,
				conds : condAux,
				binding : bindAux,
				// rawType: $scope.rules[ite].rawType,
				plainAttr : $scope.rules[ite].plainAttr,
				connector: $scope.rules[ite].connector
			});
			if (typesID.indexOf($scope.rules[ite].rawType.id) == -1)
				typesID.push($scope.rules[ite].rawType.id);
		}
		if($scope.name!=""&& $scope.name != null && $scope.name != undefined){
			$scope.name = $scope.name.replace(/\s/g, "_");
		}
		return {
			"name" : $scope.name,
			"description": $scope.description,
			"actions" : $scope.actions,
			"rules" : rules,
			"cep" : ($scope.cepRulesCount > 0) ? true : false,
			"salience" : undefined,// $scope.salience,
			"noloop" : undefined,// $scope.noloop,
			"duration" : undefined,// $scope.duration,
			"types" : typesID,
			"instruments": $scope.SelectedInstruments,
			"rule" : null,
			"bindings" : angular.toJson($scope.bindings),
			"bindingRules" : $scope.bindingRules,
			"id" : $stateParams.rule ? $stateParams.rule : undefined,
			"active" : $scope.active,
			"published" : false,
			"limited" : $scope.isLimited,
			"catalog" : $scope.catalog[0],
			"atomic": $scope.atomic,
			"halt" : $scope.halt,
			"contraCondicion": $scope.contraCondicion,
			"limited": $scope.limited,
			"user_name": $scope.user_name
		};
	};
	$rootScope.getJson = function(){
		var finalRule = $scope.prepareRulesForPlugin();
		finalRule.enabled = $scope.isEnabled;
		return finalRule;
	}
	$scope.saveAll = function(type) {
		if($scope.main.$invalid){
			toaster.pop("", "Hay campos inválidos, revise los errores y reintente.");
			return;
		}
		if($scope.name=="" || $scope.name == null || $scope.name == undefined){
			toaster.pop("", "El campo Nombre es requerido.");
			return;
		}
		if($scope.parentheses){
			toaster.pop("", "Existe un parentesis abierto, debe cerrarlo para continuar.");
			return;
		}
		var finalRule = $scope.prepareRulesForPlugin();
		finalRule.enabled = $scope.isEnabled;
		//console.log(JSON.stringify(finalRule));
		// console.log(JSON.stringify(finalRule));
        function DialogController($scope, $mdDialog, data) {
            $scope.data = data;
            $scope.closeDialog = function() {
                $mdDialog.hide();
            }
            $scope.saveAccion = function(){
                $mdDialog.hide();
            }
        }
		$http({
			method : 'POST',
			url : dataService.commonUrl+'/'+dataService.saveRule,
			tracker : 'wait',
			headers : {
				'Authorization' : $scope.token
			},
			data: finalRule
		}).success(function(data) {
			if (data.success) {
				toaster.pop("success","La regla ha sido almacenada con exito");
        	    if(type=="goBack"){
        	    	$state.go('app.rules');
        	    }else{
        	    	$state.go('app.rulesEditor', {rule: data.response.id},{reload:true});
        	    }

			} else {
				if(data.message=="Invalid DRL"){
					$mdDialog.show({
		                templateUrl: "views/dialogs/invalid-drl.html",
		                locals: {
		                    data: data
		                },
		                controller: DialogController
		            });
				}else{
					$mdDialog.show(
				      $mdDialog.alert()
				        .parent(angular.element(document.querySelector('#popupContainer')))
				        .clickOutsideToClose(true)
				        .title('No se pudo realizar la operacion de guardado de la regla.')
				        .content('Mensaje de error: '+data.message)
				        .ariaLabel('Alert Dialog')
				        .ok('Aceptar')
				    );
				}

			}
		}).error(function(data) {
			toaster.pop("error", "Error", "Hubo un problema");
		});
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

	var triggerTypeAhead = function() {
		//$(".typeahead").typeahead('destroy');
		$scope.typeAheadList = returnTypeAheadList();
		//setTimeout(function() {
			//console.log(returnTypeAheadList());
			//$(".typeahead").typeahead({
			//	source : auxList
			//});
		//}, 500);
	};

	var makeAttrList = function(objects, actual) {
		var attrList = [];
		for ( var key in objects) {
			var object = objects[key];
			if (Object.keys(object).length !== 0) {
				if (object.properties != null) {
					var innerObjects = object.properties;
					key = (actual != null && actual.length !== 0) ? actual
							+ "." + key : key;
					var theType;
					if (object["type"] != "null")
						theType = object["type"];
					else
						theType = "object";
					var attr = {
						"name" : key,
						"type" : theType
					};
					attrList.push(attr);
					attrList = attrList.concat(arguments.callee(innerObjects,
							key));
				} else {
					if (actual != null && actual.length !== 0)
						key = actual + "." + key;
					var theType;
					if (object["type"] != "null")
						theType = object["type"];
					else
						theType = "object";
					var attr = {
						"name" : key,
						"type" : theType
					};
					attrList.push(attr);
				}
			}

		}
		return attrList;
	};

	$scope.getAttrList = function(schema) {
		if (schema != null && schema.properties != null
				&& Object(schema.properties).length !== 0) {
			var attr = {
				"name" : "this",
				type : "object"
			};
			var response = [];
			response.push(attr);
			response = response.concat(makeAttrList(schema.properties, null));
			return response;
		} else
			return [];
	};
	$scope.redoAttrList = function(){
		// for ( var ite in $scope.eventTypes) {
		// 	$scope.eventTypes[ite].plainAttr = $scope.getAttrList($scope.eventTypes[ite].schema);
		// }
	}

	var getTypes = function() {
		if(dataService.useStorage){
			$scope.eventTypes = $localStorage.entities;
			// for ( var ite in $scope.eventTypes) {
			// 	$scope.eventTypes[ite].plainAttr = $scope.getAttrList($scope.eventTypes[ite].schema);
			// }
			basicExec();
		}else{
			$http({
				method : 'GET',
				url : dataService.commonUrl+"/"+dataService.findTypes,
				headers: {
					"Authorization": $scope.token
				}
			}) .success(function(result) {
				if (result.success == true) {
					$scope.eventTypes = result.response;
					for ( var ite in $scope.eventTypes) {
						$scope.eventTypes[ite].plainAttr = $scope .getAttrList($scope.eventTypes[ite].schema);
						if ($scope.eventTypes[ite].name == "consulta") {
							console .log(JSON .stringify($scope.getAttrList($scope.eventTypes[ite].schema))); }
					}
					//console.log(angular.fromJson($scope.eventTypes));
					basicExec();
				} else {
					//console.log(result.message);
					$scope.eventTypes = [];
				}
			}).error(function(result) {
				$scope.eventTypes = [];
			});
		}
	};

	$scope.setTime = function(varIn, key) {
		$('#modalTime').modal();
		$scope.time = {
			hours : "",
			minutes : "",
			seconds : ""
		};
		$scope.time.varIn = varIn; // REFERENCIA A OBJETO
		$scope.time.key = key; // NOMBRE DE VARIABLE DENTRO DE OBJETO
		// REFERENCIADO
	};
	$scope.saveTime = function() {
		varIn = $scope.time.varIn;
		key = $scope.time.key;
		if (key == "windowTime")
			$scope.cepRulesCount++;
		var aux = "";
		if (key && varIn) {
			if ($scope.time.hours != "") {
				aux = $scope.time.hours + "h";
			}
			if ($scope.time.minutes != "") {
				if ($scope.time.minutes < 60 && $scope.time.minutes >= 0) {
					aux += $scope.time.minutes + "m";
				} else {
					toaster
							.pop("danger", "Error",
									"Los minutos deben estar comprendidos entre 0 y 60");
					return;
				}
			}
			if ($scope.time.seconds != "") {
				if ($scope.time.seconds < 60 && $scope.time.seconds >= 0) {
					aux += $scope.time.seconds + "s";
				} else {
					toaster .pop("danger", "Error", "Los segundos deben estar comprendidos entre 0 y 60"); return;
				}
			}
			varIn[key] = aux;
			if (varIn[key] != "") {
				$('#modalTime').modal('hide');
			}
		}
	};

	var basicExec = function() {
		getLists();
		if ($stateParams.rule != "") {
			$http({
				method : 'GET',
				url : dataService.commonUrl+'/'+dataService.findRule+'/'+$stateParams.rule,
				headers : {
					'Authorization' : $scope.token
				}
			}).success(function(data, headers) {
				if (data.success) {
					rearmarReglas(data.response);
					$scope.user_name = data.response.user_name;
				} else {
					toaster.pop("error", "Error", data.message);
				}
				$scope.loadCatalogs();
				$scope.loadInstruments();
			}).error(function() {

			});
		} else {
			$scope.published = false;
			$scope.active = true;
			$scope.loadCatalogs();
			$scope.loadInstruments();
		}
	};
	var getLists = function(){
		$http({
			method : 'GET',
			url : dataService.commonUrl + "/" + dataService.findLists,
			tracker : 'wait',
			headers : {
				'Authorization' : $scope.token
			}
		}).success(function(data, headers) {
			if (data.success) {
				for(i in data.response){
					var list = data.response[i];
					if(list.list){
						//$scope.lists.push(list);
						$scope.lists[list.type].push(list);
					}else{
						$scope.constants.push(list);
						$scope.typeAheadConstants.push("$PC." + list.name);
					}
				}
				$scope.buildConstantBindings();
			}
		});
	}
	$scope.buildConstantBindings = function(){
		angular.forEach($scope.constants, function(value, key){
			var bindingName = "PC." + value.name;
			var bindingType = value.elements[0].type;
			$scope.bindings[bindingName] = {
				name : bindingName,
				type : bindingType
			}
		});
		triggerTypeAhead();
	}
	var catchUndefinedBindings = function(conds) {
		for ( var i in conds) {
			if (conds[i].binding == "$") {
				conds[i].binding = "";
			}
		}
		return conds;
	}
	$scope.rearmarAcciones = function(actions, external){
		if(!external){
			$scope.actions = actions;
		}
		angular.forEach($scope.actions, function(action, acKey){
			if(!action.message){
				angular.forEach($scope.bindings, function(binding, binKey){
				 	if(action.binding.name==binding.name&&action.binding.type==binding.type){
				 		action.binding = binding;
				 	}
				 });
			}else{
				angular.forEach($scope.bindingRules, function(binding, binKey){
				 	if(!action.message && action.binding.name==binding.name&&action.binding.type==binding.type){
				 		action.binding = binding;
				 	}
				 });
			}
		});
	}
	var rearmarReglas = function(rule) {
		$scope.name = rule.name;
		$scope.description = rule.description;
		for (var ite = 0; ite < rule.rules.length; ite++) {
			if(rule.rules[ite].parentesis){
				$scope.rules.push(rule.rules[ite]);
				continue;
			}
			var rawTypeRef = $scope.eventTypes[searchEventTypeIndex(rule.rules[ite].type)];
			rearmarConds(rule.rules[ite].conds, rawTypeRef);
			if (rule.rules[ite].binding == "$") {
				rule.rules[ite].binding = "";
			}
			$scope.rules.push({
				type : rule.rules[ite].type,
				rawType : rawTypeRef, // TODO SEARCH EVENT TYPES
				conds : catchUndefinedBindings(rule.rules[ite].conds),
				plainAttr : rule.rules[ite].plainAttr,
				binding : rule.rules[ite].binding,
				used : true,
				connector: rule.rules[ite].connector
			});
		}
		//console.log("Crudo Rearmadas:" + JSON.stringify(rule));

		if (rule.enabled)
			$scope.isEnabled = true;
		else
			$scope.isEnabled = false;
		if (rule.active)
			$scope.active = true;
		if (rule.published)
			$scope.published = true;
		if (rule.name)
			$scope.name = rule.name;
		if (rule.noloop)
			$scope.noloop = rule.noloop;
		if (rule.salience)
			$scope.salience = rule.salience;
		if (rule.duration)
			$scope.duration = rule.duration;
		// if (rule.bindings)
		// 	$scope.bindings = angular.fromJson(rule.bindings);
		// if (rule.bindingRules)
		// 	$scope.bindingRules = rule.bindingRules;
		if (rule.catalog)
			$scope.catalog.push(rule.catalog);
		if (rule.instruments)
			$scope.SelectedInstruments = rule.instruments;
		if (rule.atomic)
			$scope.atomic = rule.atomic;
		if (rule.halt)
			$scope.halt = rule.halt;
		if (rule.contraCondicion)
			$scope.contraCondicion = rule.contraCondicion;
		if (rule.limited)
			$scope.limited = rule.limited;
		//rearmando acciones de reglas
		$scope.autoBindings(); //rearmar bindings
		$scope.rearmarAcciones(rule.actions?rule.actions:[]);
	};
	var rearmarConds = function(conds, rawTypeRef) {
		for (var i = 0; i < conds.length; i++) {
			var cond = conds[i];
			if (!cond.cep) {
				for (var j = 0; j < rawTypeRef.plainAttr.length; j++) {
					if (cond.attr != undefined && cond.attr!=null) {
						if (rawTypeRef.plainAttr[j].type == cond.attr.type && rawTypeRef.plainAttr[j].name == cond.attr.name) {
							cond.attr = rawTypeRef.plainAttr[j];
							//if(cond.attr.type == "date" && cond.value != null){
							//	//cond.value = new Date(cond.value);
							//	if(typeof cond.value != "object"){
							//		cond.value= "";
							//	}
							//}
						}
					}
				}
			}
		};
	};
	var searchEventTypeIndex = function(eventTypeName) {
		for ( var ite in $scope.eventTypes) {
			if ($scope.eventTypes[ite].name == eventTypeName) {
				return ite;
			}
		}
		//console.log("Hubo un error, no se encontro el tipo");
	};

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
				 valueList: $scope.lists
			 },
			 controller: FunctionRuleController
		});
	}
	$scope.addFormula = function ($event, action, isNew) {
		 var parentEl = angular.element(document.body);
		 console.debug("isNew?"+isNew);
		 $mdDialog.show({
			 parent: parentEl,
			 targetEvent: $event,
			 templateUrl: "views/dialogs/action-formula-inline.html",
			 locals: {
				 bindings: $scope.bindings,
				 action: action,
				 isNew: isNew
			 },
			 controller: ActionFormulaInlineController
		});
		setTimeout(function(){
			$rootScope.$broadcast('dialogTriggered');
		},1000)

	}

	getTypes();

	$scope.goBack = function(){
    	$state.go("app.rules");
	};

	$scope.autoBindings = function(){

		$scope.bindings = {};
		$scope.bindingRules = {};
		$scope.buildConstantBindings();
		var i = 1;

		for(var r in $scope.rules){
			rule = $scope.rules[r];
			if(!rule.parentesis){
				if (rule.rawType) {
					if (rule.binding) {
						if(rule.binding[0]=="$"){
							$scope.binding = rule.binding.substr(1, rule.binding.length);
						}else{
							$scope.binding = rule.binding;
						}
					} else {
						$scope.binding = rule.rawType.name + i;
					}
					$scope.bindReplace = undefined;
					$scope.bindingRule = true;
					$scope.bindeable = rule;
					$scope.saveBinding();
				}
				i++;
			}
		}
		$scope.rearmarAcciones(true,true);
	};

	$scope.removeBindingReference = function(binding){

		if(binding && binding!="" && binding.indexOf("$")==0){

			for(var r in $scope.rules){

				var rule = $scope.rules[r];

				for(var i in rule.conds){
					var cond = rule.conds[i];

					if(cond.value.indexOf("$")==0 && cond.value==binding){
						cond.value="";
					}
				}

			}

		}

	}

	$scope.addBindingToValue = function(obj, $event) {
        var parentEl = angular.element(document.body);
        $mdDialog.show({
         parent: parentEl,
         targetEvent: $event,
         template:
           '<md-dialog aria-label="List dialog">' +
           '  <md-dialog-content>'+
           '  <h5>Seleccione binding a agregar</h5>' +
           '  <select type="text" class="form-control cust-select" ng-options="name for (name, value) in bindings" ng-model="bindingToAdd" ></select>' +
           '  </md-dialog-content>' +
           '  <div class="md-actions">' +
           '    <md-button ng-click="closeDialog()" class="md-primary">' +
           '      Cancelar' +
           '    </md-button>' +
           '    <md-button ng-click="accept()" class="md-primary">' +
           '      Aceptar' +
           '    </md-button>' +
           '  </div>' +
           '</md-dialog>',
         locals: {
           obj: obj,
           bindings: $scope.bindings
         },
         controller: DialogController
	    });
	    function DialogController($scope, $mdDialog, obj, bindings) {
		    $scope.items = obj;
		    $scope.bindings = bindings;
		    $scope.closeDialog = function() {
		      $mdDialog.hide();
		    }
		    $scope.accept = function() {
		      $scope.items.value += " "+"$"+$scope.bindingToAdd.name+" ";
		      $mdDialog.hide();
		    }

		}
	}
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
	var searchBinding = function(value, type){
		var binding = $scope.bindings[value.slice(1,999)];

		if(binding && type==binding.type){
			return true;
		} else {
			return false;
		}
	}
	var setInvalid = function(who, what){
		who.$setValidity("invalidLength", true);
		who.$setValidity("invalidBinding", true);
		who.$setValidity("invalidNumber", true);
		who.$setValidity("invalidBoolean", true);

		if(what){
			who.$setValidity(what, false);
		}
	}
	$scope.validateInput = function(ruleIndex, condIndex, value, type){
		var who = $scope.main["rule"+ruleIndex+"Cond"+condIndex]
		if(value.length == 0){
			setInvalid(who, "invalidLength");
		}else{
			if(value && value.length > 0 && value[0] == "$"){
				if(searchBinding(value, type)){
					setInvalid(who);
				}else{
					setInvalid(who, "invalidBinding");
				}
			}else{
				switch(type){
					case "integer" || "long" || "float" || "double":
							if(isNaN(value)){
								setInvalid(who, "invalidNumber");
							}else{
								setInvalid(who);
							}
						break;
					case "boolean":
							if(value != "null" && value != "true" && value != "false"){
								setInvalid(who, "invalidBoolean");
							}else{
								setInvalid(who);
							}
						break;
					default:
							setInvalid(who);
						break;
				}
			}
		}
	}
    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de reglas avanzado"
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

    $scope.attributeChanged = function(type, rule, cond){
    	rule.used=true;
    	cond.value=""
    	if(type=="boolean"){
    		cond.value="null";
    	}
    }

    var faqs = [
        {
            "name": "¿Cual es el objetivo de esta pantalla?",
            "description": "Esta pantalla se encarga de la creación/modificación de reglas avanzadas que no estan soportadas por el editor de tablas de decisiones."
        },
        {
            "name": "¿Como comienzo a utilizar el editor?",
            "description": "Primero se deben agregar las condiciones presionando el boton agregar condicion, (se pueden agregar paréntesis para una logica mas compleja si es necesario). Luego será necesario que se declare una accion para la regla."
        },
        {
            "name": "¿Que son las restricciones?",
            "description": "Las restricciones son componentes de cada condicion, supongamos que se realiza una condicion con entidad cualquiera, se pueden crear tantas restricciones a esta condicion como se deseen, por ejemplo \"atributo1\" == \"valor1\" (Y) \"atributo2\" == \"valor2\"."
        },
        {
            "name": "¿Como cambio los conectores logicos?",
            "description": "Los conectores los puede cambiar haciendo click sobre los mismos, éste alternará entre los conectores disponibles."
        },{
            "name": "¿Para que sirven los enlaces?",
            "description": "Los enlaces facilitan la comparación de atributos de distintas condiciones o incluso de la misma condición, una vez que un objeto de datos ingresa y es correspondido por las restricciones de la condición ese objeto estará disponible para su vinculación a través de enlaces.."
        },
        {
           "name": "¿Como declaro acciones?",
            "description": "Simplemente haciendo click en el boton \"Modificar un campo\" o \"agregar mensaje\" , estas son las dos opciones de acciones para esta pantalla. "
        }
    ];


}]);
