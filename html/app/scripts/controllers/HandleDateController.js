 app.controller('HandleDateController', ['$scope', '$mdDialog', 'cond', 'bindings', 'typeAheadList', '$mdToast',
								 function($scope,   $mdDialog,   cond,   bindings,   typeAheadList,   $mdToast) {

    $scope.cond = cond;
    $scope.typeAheadList = typeAheadList;
    $scope.bindings = bindings;
    if(cond.value != null && cond.value[0] != "$" && cond.value != "null" && cond.value != ""){
    	cond.value = new Date(cond.value);
    }
    if(typeof cond.value == "object"){
    	$scope.opt = "calendar";
    }else if((cond.value != "" && cond.value != undefined)||(cond.value == "null")){
    	$scope.opt = "literal";
    }
    $scope.closeDialog = function() {
      $mdDialog.hide();
    }
    $scope.save = function() {
      if(cond.value == null){
  		$mdToast.show($mdToast.simple().content("La fecha no puede estar vacía").position("top right") .hideDelay(3000) ); 
  		return;
      }
      if(cond.value[0] == "$"){
      	if(bindings[cond.value.slice(1,cond.value.length)].type !="date"){
      		$mdToast.show($mdToast.simple().content("El atributo seleccionado debe ser una fecha").position("top right") .hideDelay(3000) ); 
      		return;
      	}
      }else if(typeof cond.value != "object" && cond.value != "null" ){
      	$mdToast.show($mdToast.simple().content("Una fecha solo puede ser comparada con un atributo de fecha o null").position("top right") .hideDelay(3000) ); 
  		return;
      }
      $mdDialog.hide();
    }
    $scope.retry = function(){
    	cond.value = "";
    	$scope.opt = undefined;
    }

}]);