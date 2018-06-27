app.controller('SimulationController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog', '$state', '$mdBottomSheet',
								function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog,   $state, $mdBottomSheet) {
	//👉 Last addon FEB17
	function sortNumber(a,b) {
	    return b - a;
	}

	$scope.collection = [];
	$scope.catalogs = [];
	$scope.tempCatalogs = [];
	$scope.entities = [];
	$scope.runtimeBaseUrl = dataService.runtimeBaseUrl;
	$scope.simulation = {
		"id":null,
		"instances" : "", //SETEADO EN SAVE
		"collection": "", //SETEADO EN SAVE
		"name" : "",
		"description": "",
		"version":0,
		"catalogs" : [],
		"installed": false,
		"sources": {
			"services": [],
			"files": []
		}
	};

	var toaster = new function(){
		this.pop = function(type, title, message){
		  message = message?message:"";
		  title = title?title:"";
		  //type useless
		  $mdToast.show($mdToast.simple() .content(title+" "+message) .position("top right") .hideDelay(3000) );
		};
	};
	$scope.showOptions = function(){
		$mdBottomSheet.show({
	        templateUrl: 'views/sheet/options-sheets.html',
	        scope: $scope,
	        preserveScope: true,
	    })
	}
	$scope.editFact = function($event, fact, index){
		$mdDialog.show({
	      controller: 'ViewFactController',
	      targetEvent: $event,
		  templateUrl: "views/dialogs/view-fact.html",
	      parent: angular.element(document.body),
	      clickOutsideToClose:false,
	      locals : {
	      	fact : fact,
	      	index : index
	      }
	    });
	};
	$scope.$on("initialConfig", function(){
		getInitialVars();
	});

	var getInitialVars = function(){
		$scope.requireInstrument = dataService.requireInstrument;
		$scope.autoVersion = dataService.autoVersion;
	};

	$scope.basicExec = function(){
		if(dataService.initiatedSuccessfully){
			getInitialVars();
		}
		if(dataService.useStorage){
			$scope.catalogs = $localStorage.catalogs;
			$scope.entities = $localStorage.entities;
		}else{
			$http({
				method: 'GET',
				url: dataService.commonUrl+'/'+dataService.findCatalogs,
				headers: {"Authorization": $scope.token}
			}).success(function(data,headers){
				if(data.success){
				  $scope.catalogs = data.response;
				}
				if($stateParams.simulation){
					$http({
						method: 'GET',
						url: dataService.commonUrl+'/'+dataService.findSimulation+'/'+$stateParams.simulation,
						headers: {"Authorization": $scope.token}
					}).success(function(data,headers){
						if(data.success){
							$scope.simulation = data.response;
							if(!$scope.simulation.sources){
								$scope.simulation.sources = {
									files :[],
									services: []
								}
							}
							$scope.simulation.initial_date = $scope.simulation.initial_date !== undefined ? new Date($scope.simulation.initial_date) : undefined;
							$scope.simulation.ending_date = $scope.simulation.ending_date !== undefined ? new Date($scope.simulation.ending_date) : undefined;
							$scope.collection = data.response.collection;
							$scope.instances = data.response.instances;

							$scope.getEntities(data.response.catalogs);
						}
					});
				}
		  	});
		}
	};

	$scope.getEntities = function(catalogs, force){
		$http({
			method: 'POST',
			url: dataService.commonUrl+"/"+dataService.formCatalogs,
			data: {'catalogs': catalogs},
			headers: {"Authorization": $scope.token}
		}).success(function(data,headers){
			if(data.success){
			 	$scope.entities = data.response;
			 	$scope.cleanCollection(force);
			}
		});
	};

	$scope.cleanCollection = function(force){
		var eNames = [];
		angular.forEach($scope.entities, function(entity, key){
			eNames.push(entity.name);
		});

		var delIndex = [];

		for(var index in $scope.collection){
			if(eNames.indexOf($scope.collection[index].name) == -1)
				delIndex.push(index);
		}

		for(var i=(delIndex.length - 1); i>=0; i--){
			$scope.collection.splice(index, 1);
		}
		$scope.removeServices();
		if(force){
			$scope.removeExcel();
		}
	};
	$scope.removeHttp = function(index){
		var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar este request?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
        	$scope.simulation.sources.services.splice(index,1);
        });
	}
	$scope.addHttp = function(obj){
		$mdBottomSheet.hide();
		$mdDialog.show({
		  templateUrl: "views/dialogs/add-http-request.html",
		  locals: {
			parentScope: $scope,
			obj: obj,
			models: $scope.makeAllModels()
		  },
		  controller: "AddHttpRequestController",
		  controllerAs: "m"
		});
	};

	$scope.addObj = function ($event, cond) {
		var parentEl = angular.element(document.body);
		$mdBottomSheet.hide();
	 	$mdDialog.show({
		  parent: parentEl,
		  targetEvent: $event,
		  templateUrl: "views/dialogs/simulation-addObj.html",
		  locals: {
			parentScope: $scope
		  },
		  controller: DialogController
		})
		function DialogController($scope, $mdDialog, parentScope) {
		  $scope.obj = {
			// entity : {},
			// atributo : {},
			// conn : ""
		  };
		  $scope.connSelectable = ["==", ">", "<", "<=", ">=", "!="];
		  $scope.entities = parentScope.entities;
		  $scope.closeDialog = function() {
				$mdDialog.hide();
		  };
		  $scope.saveAccion = function(){
				$scope.builded = {};
				//$scope.buildObj($scope.obj.entity.schema.properties, $scope.builded);
				var a = {};
				angular.copy($scope.obj.entity, a);
				parentScope.collection.push(a);
				console.log($scope.builded);
				$mdDialog.hide();
		  };

		}
	};

	$scope.addRule = function(){
		$scope.rows.push({
		  conds: {},
		  acciones: {}
		});
	};

	$scope.makeAllModels = function(){
		var models = {};
		angular.forEach($scope.entities, function(entity, key){
			models[entity.name] = {};
			$scope.buildObj(entity.schema.properties, models[entity.name]);
		});
		return models;
	};
	$scope.buildObj = function(obj, tobj){
		angular.forEach(obj, function(value, key){
			if(value.type == "object"){
				tobj[key] = {};
				$scope.buildObj(value.properties, tobj[key]);
			}else{
				switch(value.type){
					case "integer":
							tobj[key] = (value.value === undefined)?null:value.value;
						break;
					case "float":
							tobj[key] = (value.value === undefined)?null:value.value;
						break;
					default:
							tobj[key] = (value.value === undefined || value.value === "")?null:value.value;
						break;
				}
			}

		});
	};

	$scope.prepareSimulation = function(){
		var arrObj = [];
		var simulationForPersist = {};
		angular.forEach($scope.collection, function(value, key){
		  arrObj.push({
			"entity" : value.name,
			"instance": {}
		  });
		  $scope.buildObj(value.schema.properties,arrObj[arrObj.length-1].instance);
		});
		simulationForPersist = $scope.simulation;
		simulationForPersist.instances = arrObj;
		simulationForPersist.collection = $scope.collection;
		//console.log(simulationForPersist);
		return simulationForPersist;
	};

	$rootScope.getJson = function() {
		return $scope.prepareSimulation();
	};
	$scope.save = function(flag, type){
		if($scope.simulation.name == null || $scope.simulation.name == undefined || $scope.simulation.name == "" || $scope.simulation.name === ""){
			toaster.pop("error","El nombre del escenario es requerido","");
			return;
		}
		if($scope.simulation.catalogs == null || $scope.simulation.catalogs == undefined || $scope.simulation.catalogs.length == 0){
			toaster.pop("error","No se puede realizar el guardado de un escenario sin seleccionar al menos 1 Dominio","");
			return;
		}
		if($scope.simulation.version == null || $scope.simulation.version == undefined || $scope.simulation.version === ""){
			toaster.pop("error","No se puede realizar el guardado de un escenario sin indicar numero de versión","");
			return;
		}
		if($scope.simulation.version < 0){
			toaster.pop("error","No se puede realizar el guardado de un escenario con numero de versión negativo","");
			return;
		}
		var data = $scope.prepareSimulation();
		return $http({
		  method : 'POST',
		  url : dataService.commonUrl+'/'+dataService.saveSimulation,
		  headers : {
			'Authorization' : $scope.token
		  },
		  data: data
		}).success(function(data) {
		  if (data.success) {
		  	if(!flag)
				toaster.pop("success","El escenario ha sido almacenado con exito");

    		if(type=="goBack"){
    	    	$state.go('app.simulations');
    	    }else{
    	    	$state.go('app.simulation', {simulation: data.response.id});
    	    }

		  	return data;
		  } else {
			toaster.pop("error","No se pudo realizar la operacion de guardado del escenario",data.message);
		  }
		}).error(function(data) {
		  toaster.pop("error", "Error", "Hubo un problema");
		  return $q.reject(data);
		});
	}
	$scope.testSim = function($event){
		$scope.save(true).then(function(data){
			if($scope.simulation.id==null){
			  toaster.pop("success","El escenario debe ser guardado para poder simularse.");
			  return;
			}
			function DialogController($scope, $mdDialog, $filter, result) {
				$scope.data = result;
				$scope.closeDialog = function() {
					$mdDialog.hide();
				}
				$scope.saveAccion = function(){
					$mdDialog.hide();
				}
				$scope.saveJSON = function () {
					console.debug("Downloading file")
					$scope.toJSON = '';
					$scope.toJSON = $filter('json')($scope.data.response);
					var blob = new Blob([$scope.toJSON], { type:"application/json;charset=utf-8;" });			
					var downloadLink = angular.element('<a></a>');
	                downloadLink.attr('href',window.URL.createObjectURL(blob));
	                downloadLink.attr('download', 'simulation.json');
					downloadLink[0].click();
				};

			}
			var parentEl = angular.element(document.body);

			$http({
				method: 'GET',
				url: dataService.commonUrl+'/'+dataService.testSimulation+'/'+$scope.simulation.id,
				headers: {"Authorization": $scope.token},
			}).success(function(data,headers){
				$mdDialog.show({
					parent: parentEl,
					targetEvent: $event,
					templateUrl: "views/dialogs/simulation-result.html",
					locals: {
						result: data
					},
					controller: DialogController
				});
			});
		}, function(error){
			toaster.pop("success","No se pudo guardar: "+error.message);
		});
	};
	$scope.showImport = function(){
		$mdBottomSheet.hide();
		$mdDialog.show({
			templateUrl: "views/dialogs/upload-simulation-facts.html",
			locals: {
				models: $scope.makeAllModels(),
				parentScope: $scope
			},
			controller: 'UploadSimulationFactsController'
		})
	};
	$scope.publish = function($event, force){
		$scope.save(true).then(function(data){
			if($scope.simulation.id==null){
			  toaster.pop("success","El escenario debe ser guardado para poder publicarse.");
			  return;
			}
			var isForced=""
			if(force){
				isForced="?force=true";
			}
			$http({
				method: 'GET',
				url: dataService.commonUrl+'/'+dataService.publish+'/'+$scope.simulation.id+isForced,
				headers: {"Authorization": $scope.token},
			}).success(function(data,headers){
				if(data.success){
					$scope.simulation.installed = true;
					toaster.pop("success","El escenario se publico correctamente.");
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
					           '          <p class="text-danger"><b>Ya hay publicado un servicio con el mismo nombre y versión, por lo que la publicación se sobreescribirá si desea continuar. </b></p>'+
					           '      </div>'+
					           '  </md-dialog-content>' +
					           '  <div class="md-actions">' +
					           '    <md-button ng-click="accept()" class="md-primary">' +
					           '      Continuar y reemplazar' +
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
					          parentScope.publish(undefined, true);
					        }
					        $scope.cancel = function() {
					          $mdDialog.hide();
					        }
					      }
	        		}else{
	        			$mdDialog.show(
                        $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .title('')
                        .content(data.message)
                        .ariaLabel('dialogo de error de guardado')
                        .ok('Ok..')
            		);
	        		}
				}
			});
		}, function(error){
			toaster.pop("success","No se pudo guardar: "+error.message);
		})
	}
	$scope.unPublish = function($event){
		if($scope.simulation.id==null){
		  toaster.pop("success","El escenario debe ser guardado para poder publicarse.");
		  return;
		}
		$http({
			method: 'GET',
			url: dataService.commonUrl+'/'+dataService.unPublish+'/'+$scope.simulation.id,
			headers: {"Authorization": $scope.token},
		}).success(function(data,headers){
			if(data.success){
				$scope.simulation.installed = false;
				toaster.pop("success","El escenario se despublico correctamente.");
			}else{
				toaster.pop("success","No se pudo despublicar");
			}
		});
	}
	$scope.removeObject = function(index){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar este objeto?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
        	$scope.collection.splice(index,1);
        });
	};
	$scope.removeAllObjects = function(){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar todos los objetos?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
        	$scope.collection = [];
        });
	};
	$scope.removeFile = function(index){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion de borrado')
            .content('¿Esta seguro que desea borrar este archivo?')
            .ok('Borrar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
        	$scope.simulation.sources.files.splice(index,1);
        });
	};
	$scope.goBack = function(){
        $state.go("app.simulations");
	}
	$scope.addCatalogs = function(){
		var globalFlag = false;
		angular.forEach($scope.tempCatalogs, function(catalog, key){
			var flag = false;
			for(var i in $scope.simulation.catalogs){
				var cat = $scope.simulation.catalogs[i];
				if(catalog.name == cat.name){
					flag = true;
				}
			}
			if(!flag){
				$scope.simulation.catalogs.push(catalog);
				globalFlag = true;
			}
		});
		if(globalFlag){
			angular.forEach($scope.catalogs, function(value, key){
				value.ticked = false;
			});
			toaster.pop("success","Los dominios fueron agregados correctamente.");
		}else{
			toaster.pop("success","Todos los dominios seleccionados ya se encuentran agregados.");
		}

		$scope.getEntities($scope.simulation.catalogs);
	}
	$scope.catalogUp = function(index){
		var aux = {}
		angular.copy($scope.simulation.catalogs[index], aux);
		$scope.simulation.catalogs.splice(index-1,0,aux);
		$scope.simulation.catalogs.splice(index+1,1);
	}
	$scope.catalogDown = function(index){
		var aux = {}
		angular.copy($scope.simulation.catalogs[index], aux);
		$scope.simulation.catalogs.splice(index+2,0,aux);
		$scope.simulation.catalogs.splice(index,1);
	}
	$scope.catalogRemove = function(index){
		var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion')
            .content('Todos los Objetos del escenario, servicios HTTP y archivos excel que correspondan se eliminarán del escenario. ¿Esta seguro que desea quitar el dominio seleccionado del escenario de pruebas?')
            .ok('Quitar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
        	$scope.simulation.catalogs.splice(index,1);
        	$scope.getEntities($scope.simulation.catalogs, true);
        });
	}
	$scope.removeExcel = function(){
		$scope.simulation.sources.files = [];
	}
	$scope.removeServices = function(){
		var toremove = [];
		mainstuff:
		 for(var i in $scope.simulation.sources.services){
			var serv = $scope.simulation.sources.services[i];
			for(var j in $scope.entities){
				var ent = $scope.entities[j];
				if(serv.entityId == ent.id){
					continue mainstuff;
				}
			}
			toremove.push(i);
		}
		toremove.sort(sortNumber);
		for(var i in toremove){
			var pos = toremove[i]
			$scope.simulation.sources.services.splice(pos, 1);
		}
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
            };
        }
    };

    var faqs = [
        {
            "name": "¿Cual es el objetivo de esta pantalla?",
            "description": "Esta pantalla se encarga de la administración de escenarios"
        },
        {
            "name": "¿Cual es la utilidad de los escenarios?",
            "description": "Los escenarios sirven para generar un ambiente de prueba y simulación de un conjunto de reglas agrupadas en uno o varios dominios, entrega un resultado muy claro en el cual se puede observar el comportamiento del set de reglas especificado."
        },
        {
           "name": "¿Como comienzo a utilizarlo?",
            "description": "El funcionamiento es simple. Primero se debe agregar uno o varios dominios, luego debemos agregar uno o varios objetos de datos para comenzar a operar con ellos, un objeto de datos es una instancia de una entidad previamente declarada que se encuentra siendo utilizada por las reglas."
        },
    ];
	$scope.basicExec();

}]);
