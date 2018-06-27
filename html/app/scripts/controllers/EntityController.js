app.controller('EntityController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$state', '$mdDialog', '$rootScope',
							function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $state,   $mdDialog ,  $rootScope) {
	$scope.entity = {
		 "schema": {
		 	"type":"object",
		 	"properties":{}
		 },
        "name" : "",
        "description" : ""
	};
	$scope.parentKey = "";
	$scope.adding = false;
	$scope.values = [{
			value: "string",
			readable: "texto"
		},{
			value: "integer",
			readable: "numero entero"
		},{
			value: "float",
			readable: "numero decimal"
		},{
			value: "date",
			readable: "fecha"
		},{
			value: "object",
			readable: "Objeto"
		},{
			value: "boolean",
			readable: "Verdadero/falso"
	}];

	$scope.editThis = function(value, key){
		value.editing = true;
		value.tempKey = key;
	}
	$scope.acceptEdit = function(value, parentKey, key){
		if(value.tempKey !=""){
			$http({
	            method: 'POST',
	            url: dataService.commonUrl+'/'+dataService.changeEntityAttribute,
	            data: {
	            	entity : {
	            		id : $scope.entity.id,
	            		name: $scope.entity.name
	            	},
	            	attr : {
	            		old : parentKey,
	            		new : parentKey.slice(0, -key.length)+value.tempKey
	            	}
	            },
	            headers: {"Authorization": $scope.token}
	        }).success(function(data){
	        	if(data.success){
	        		basicExec();
	        	}
	        })
	    }
	}
	$scope.whichRules = function(){

		$http({
	            method: 'POST',
	            url: dataService.commonUrl+'/'+dataService.whichRule,
	            data: {
	            			"id": $scope.entity.id,
	            			"name": $scope.entity.name
	            		},
	            headers: {"Authorization": $scope.token}
	        }).success(function(data,headers){
	          	if(data.success){
	          		$mdDialog.show({
	          			controller: 'ViewFactController',
					templateUrl: "views/dialogs/view-related-rules.html",
				      parent: angular.element(document.body),
				      locals : {
				      		array: data.response
				      }
				})

	        	}else{
        			$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000));
	        	}
	        });
	}

	$scope.addSchema = function(obj, name, type){
		if(name==""||!angular.isDefined(name)){
			$mdToast.show($mdToast.simple().content("Nombre no puede estar vacío").position("top right").hideDelay(3000) );
			return;
		}else{
			name = name.replace(/\s/g, "_");
			if(name.length>2){
				name = name.charAt(0).toLowerCase()+name.charAt(1).toLowerCase()+name.charAt(2).toLowerCase()+name.slice(3);
			}
			if(name[0]>=0){
				$mdToast.show($mdToast.simple().content("El nmombre del atributo no puede comenzar con un número").position("top right").hideDelay(3000) );
				return;
			}
		}
		if(type==""||!angular.isDefined(type)){
			$mdToast.show($mdToast.simple().content("Tipo no puede estar vacío").position("top right").hideDelay(3000) );
			return;
		}
		if(!angular.isDefined(obj.properties)){
			obj.properties = {};
		};
		t = angular.fromJson(type);
		obj.properties[name] = {
			"type": t.value,
			"readableType": t.readable
		}
		if(t.value=="object"){
			obj.properties[name].properties = {};
		};
		obj.tempName = "";
		obj.adding = false;
		return;
	};

	$scope.externalCloseTab = function(){
		$scope.$parent.displayEntity = false;
	};

	$scope.removeThis = function(obj, index){
		if($scope.entity.id){
			if(angular.isDefined(obj)){
				var base = "";
				angular.forEach($scope.entity.schema.properties,function(value,key){
					if(obj == value)
						base = key;
				});
				if(base!="")
					deleteObjAttr([index],base,obj,0,false)
			}else{
				var prop = $scope.entity.schema.properties[index];
				if(prop.type=="object" && prop.properties && Object.keys(prop.properties).length > 0){
					var keys = []
					angular.forEach(prop.properties,function(value,key){
						keys.push(key);
					});
					if(keys.length > 0){
						deleteObjAttr(keys,index,prop,0,true)
					}
				}else{
					$http({
						method: 'POST',
						url: dataService.commonUrl+'/'+dataService.removeEntityAttr,
						data: {
							"entity":{
								"id":$scope.entity.id,
								"name":$scope.entity.name
							},
							"attr":index
						},
						headers: {
							"Authorization": $scope.token
						}
					}).success(function(data,headers){
						if(data.success){
							delete $scope.entity.schema.properties[index];
						}else{
							$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000));
				        }
		    		}).error(function(data,status){
		    			console.log(status);
		    		});
				}

			}
		}else{
			if(angular.isDefined(obj)){
				delete obj.properties[index];
			}else{
				delete $scope.entity.schema.properties[index];
			}
		}
	};

	var deleteObjAttr = function(keys,base,obj,i,dbase){
		$http({
			method: 'POST',
			url: dataService.commonUrl+'/'+dataService.removeEntityAttr,
			data: {
				"entity":{
					"id":$scope.entity.id,
					"name":$scope.entity.name
				},
				"attr":base+"."+keys[i]
			},
			headers: {
				"Authorization": $scope.token
			}
		}).success(function(data,headers){
			if(data.success){
				delete obj.properties[keys[i]];
				i += 1;
				if(i<keys.length){
					deleteObjAttr(keys,base,obj,i,dbase);
				}else{
					if(dbase)
						deleteBase(base);
				}
			}else{
				$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000));
	        }
		}).error(function(data,status){
			console.log(status);
		});
	};

	var deleteBase = function(base){
		delete $scope.entity.schema.properties[base];
	};

	$scope.save = function(type, bypass){

		if(!bypass && $scope.entity.name=="" || !bypass && $scope.entity.name==" "){
			$mdToast.show($mdToast.simple().content("El nombre de la entidad no puede estar vacío").position("top right").hideDelay(3000) );
			return;
		}else{
			$scope.entity.name = $scope.entity.name.replace(/\s/g, "_").capitalizeFirstLetter();

		}
		$scope.entity.plainAttr = $scope.getAttrList($scope.entity.schema);
		if($scope.$parent.entitiesExternal){
			$scope.$parent.redoAttrList();
		}
		if(dataService.useStorage){
			if(!angular.isDefined($scope.entity.id)){
				$scope.entity.id = Date.now();
				$localStorage.entities.push($scope.entity);
			}else{
				var a = $localStorage.entities;
				for(var i in a){
					if($scope.entity.id == a[i].id){
						$scope.entity.plainAttr = $scope.getAttrList($scope.entity.schema);
						a[i] = $scope.entity;
						if($scope.$parent.entitiesExternal){
							$scope.$parent.redoAttrList();
						}
						$mdToast.show($mdToast.simple().content("Actualizado correctamente").position("top right").hideDelay(3000));
						return;
					}
				}
			}
		}else{
			if(bypass){
				return $scope.entity;
			}
			if(type == "accept"){
				$scope.entity.force = true;
			}else if(type == "decline"){
				$scope.entity.force = false;
			}
        	$http({
	            method: 'POST',
	            url: dataService.commonUrl+'/'+dataService.saveEntity,
	            data: $scope.entity,
	            headers: {"Authorization": $scope.token}
	        }).success(function(data,headers){
	          	if(data.success){
	          		$scope.entity.force = undefined ;
	          		$scope.$parent.$broadcast('remoteEntitySaved');
	        	    $mdToast.show($mdToast.simple().content("Guardado con exito.").position("top right").hideDelay(3000));
	        	    if(type == "goBack"){
	        	    	$state.go('app.entities');
	        	    }else{
		        	    if(!$scope.$parent.entitiesExternal)
		        	    	$state.go('app.entity', {entity: data.response.id});
	        	    }
	        	}else{
	        		if(data.retry){
	        			  $mdDialog.show({
					         template:
					           '<md-dialog aria-label="List dialog" flex="30">' +
						        '   <md-toolbar class="md-accent">'+
								'      <div class="md-toolbar-tools">'+
								'        <h2>'+
								'          <span>Se necesitan acciones adicionales.</span>'+
								'        </h2>'+
								'      </div>'+
								'    </md-toolbar>'+
					           '  <md-dialog-content>'+
					           '      <div class="md-dialog-content">'+
					           //'          <p>La entidad se encuentra en al menos un escenario, debido a esto, se necesitan acciones adicionales de su parte.</p>'+
					           '          <p class="text-danger"><b>Los objetos de datos de los escenarios involucrados se van a actualizar con las modificaciones que introdujo en la entidad. Si no quiere este cambio puede optar por no modificar el escenario, haciendo que el mismo quede intacto, siendo este el caso no se va a poder realizar ninguna acción sobre el. </b></p>'+
					           '          <h4>Los Escenarios involucrados son:</h4></br>'+
					           '          <ul class="list-group md-whiteframe-5dp">'+
					           '              <li class="list-group-item" ng-repeat="item in data.response">{{item}}</li>'+
					           '          </ul>'+
					           '      </div>'+
					           '  </md-dialog-content>' +
					           '  <div class="md-actions">' +
					           '    <md-button ng-click="accept()" class="md-primary">' +
					           '      Aceptar' +
					           '    </md-button>' +
					           '    <md-button ng-click="decline()" class="md-primary">' +
					           '      No modificar' +
					           '    </md-button>' +
					           '    <md-button ng-click="cancel()" class="md-primary">' +
					           '      Cancelar' +
					           '    </md-button>' +
					           '  </div>' +
					           '</md-dialog>',
					         locals: {
					           data: data,
					           parentScope: $scope
					         },
					         controller: DialogController
					      });
					      function DialogController($scope, $mdDialog, data, parentScope) {
					        $scope.data = data;
					        $scope.accept = function() {
					          $mdDialog.hide();
					          parentScope.save("accept");
					        }
					        $scope.decline = function() {
					          $mdDialog.hide();
					          parentScope.save("decline");
					        }
					        $scope.cancel = function() {
					          $mdDialog.hide();
					        }
					      }
	        		}else{
	        			$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000));
	        		}
	        	}
	            return;
	        });
		}
	}
	if(!$scope.$parent.entitiesExternal){
		$rootScope.getJson = function(){
			return $scope.save("accept", true);
		}
	}
	$scope.$on("ChangedEntity", function(){
		basicExec();
	});
	var basicExec = function(){
		if($scope.$parent.entitiesExternal){
			angular.copy($scope.$parent.entityEXT, $scope.entity)
			$scope.entity = $scope.$parent.entityEXT;
			if(angular.isDefined($scope.entity)){
				$scope.value = $scope.entity.schema
			}
		}else{
		    if(dataService.useStorage){
				var a = $localStorage.entities;
				if(angular.isDefined($scope.entity.schema)){
					$scope.value = $scope.entity.schema
				}
				for(var i in a){
					if($stateParams.entity == a[i].id){
						$scope.entity = a[i];
						return;
					}
				}
		    }else{
		    	if($stateParams.entity){
		         $http({
		            method: 'GET',
		            url: dataService.commonUrl+'/'+dataService.findEntity+'/'+$stateParams.entity,
		            headers: {"Authorization": $scope.token}
		          }).success(function(data,headers){
		            if(data.success){
						$scope.entity = data.response;
		            }
		          });
		        }
		    }
			// $mdToast.show($mdToast.simple().content("No se encontro el id").position("top right").hideDelay(3000) );
		}
	}
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
		for ( var ite in $scope.eventTypes) {
			$scope.eventTypes[ite].plainAttr = $scope.getAttrList($scope.eventTypes[ite].schema);
		}
	}
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

    $scope.goBack = function(){
        $state.go("app.entities");
    };

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Editor de Entidades"
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
            "description": "Esta pantalla se encarga de la creación/modificación de entidades que representan los objectos de datos que intervendran en las reglas"
        },
        {
            "name": "¿Qué son los atributos?",
            "description": "Los atributos representan a cada uno de los campos contenidos en los objetos de datos"
        },
        {
           "name": "¿Qué tipos de datos son soportados por el sistema?",
            "description": "Los datos soportados por el sistema son: numeros enteros, numeros reales (con coma), texto, fechas y verdadero falso"
        }
    ];

    basicExec();
}]);
