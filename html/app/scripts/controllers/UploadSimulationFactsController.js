app.controller('UploadSimulationFactsController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog', '$state', 'models', 'parentScope',
										   function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog,   $state,  models, parentScope) {
	$scope.parentScope = parentScope;
	$scope.closeDialog = function() {
		$mdDialog.cancel();
	};

	$scope.saveCond = function(){
		$mdDialog.hide();
	};
	$scope.import = function (event, reader, fileList, fileObjs, file){

		if($scope.fileImport === undefined || ($scope.fileImport.filename.substr($scope.fileImport.filename.lastIndexOf(".")) != ".xls" && $scope.fileImport.filename.substr($scope.fileImport.filename.lastIndexOf(".")) != ".xlsx")){
			$mdToast.show($mdToast.simple().content("Debe ingresar un archivo xls o xlsx para realizar la importacion de escenario").position("top right").hideDelay(3000) );
			$scope.fileImport = undefined;
			return;
		}
		data = {
      id: parentScope.simulation.id,
      name: parentScope.simulation.name,
      file: $scope.fileImport,
      models: models
    };
		$http({
			method: 'POST',
      url: dataService.commonUrl + '/' + dataService.getSimulationJsons,
      headers: {
        "Authorization": parentScope.token
	     },
	     data: data
		}).success(function(data,headers){
	    	if(data.success){
	    		$mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
	    		// $scope.buildAllItems(data.response);
		        if(parentScope.simulation.sources.files === undefined)
		          parentScope.simulation.sources.files = [];

		        parentScope.simulation.sources.files.push(data.response);
	    		$mdDialog.hide();
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
	$scope.buildAllItems = function(items){
		angular.forEach(items, function(item, name){
			angular.forEach(parentScope.entities, function(entity, entityKey){
				if(entity.name == name){
					angular.forEach(item, function(obj, index){
						var dest = {};
						angular.copy(entity, dest);
						$scope.buildItemForCollection(dest.schema.properties, obj);
						//rebuildDates(dest.schema.properties);
						parentScope.collection.push(dest);
					});
				}
			});
		});
	};
	function rebuildDates (values){
		angular.forEach(values, function(value, key){
			if(value.type == "object"){
				rebuildDates(value.properties);
			}
			if(value.type=="date"){
				excelToUnix = (value.value - 25569)*86400;
				value.value = new Date(value.value);
			}
		});
	}
	$scope.buildItemForCollection = function(result, fact){

		angular.forEach(fact, function(f, k){
			if(typeof f == "object"){
				$scope.buildItemForCollection(result[k].properties, f);
			}else{
				if(result[k].type == "integer"){
					try {
						result[k].value = Number.parseInt(f);
					}
					catch(err) {
						$mdToast.show($mdToast.simple().content("Hubo un error en la importación, se detectó algun campo inválido.").position("top right").hideDelay(3000) );
					}

				}
				if(result[k].type == "float"){
					try {
						result[k].value = Number.parseFloat(f);
					}
					catch(err) {
						$mdToast.show($mdToast.simple().content("Hubo un error en la importación, se detectó algun campo inválido.").position("top right").hideDelay(3000) );
					}

				}
				if(result[k].type != "float" && result[k].type != "integer"){
					try {
						result[k].value = f;
					}
					catch(err) {
						$mdToast.show($mdToast.simple().content("Hubo un error en la importación, se detectó algun campo inválido.").position("top right").hideDelay(3000) );
					}

				}
			}
		});

	}
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

	$scope.exportModel = function(){
		if(parentScope.simulation.name == null || parentScope.simulation.name == undefined || parentScope.simulation.name == "" || parentScope.simulation.name == " "){
			$mdToast.show($mdToast.simple().content("El nombre del escenario es requerido","").position("top right").hideDelay(3000));
			return;
		}

		if(parentScope.simulation.catalogs == null || parentScope.simulation.catalogs == undefined || parentScope.simulation.catalogs.length == 0){
			$mdToast.show($mdToast.simple().content("No se puede realizar el guardado de un escenario sin seleccionar al menos 1 Dominio","").position("top right").hideDelay(3000));
			return;
		}
		var data = parentScope.prepareSimulation();
        	$http({
	            method: 'POST',
	            url: dataService.commonUrl+'/'+dataService.getSimulationModel,
	            headers: {
	                "Authorization": parentScope.token
	            },
            	data: data
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
}]);
