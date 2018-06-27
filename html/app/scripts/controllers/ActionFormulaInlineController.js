function ActionFormulaInlineController($scope, $mdDialog, action, bindings, $rootScope, isNew) {
	$scope.obj = {}
	console.log(bindings);
	$scope.outBind = {};
	$scope.bindings = bindings;
	$scope.closeDialog = function() {
		$mdDialog.hide();
	}
	$scope.saveAction = function(){
		action.code = true;
		action.value = $scope.editor.getValue();
		$mdDialog.hide();
	}
	$rootScope.$on('dialogTriggered', function(){
		$scope.editor = ace.edit("editor-min");
    	$scope.editor.setTheme("ace/theme/chrome");
		$scope.editor.getSession().setMode("ace/mode/java");
		if(action.value!=""&&action.value!=undefined&&!isNew){
			$scope.editor.setValue(action.value);
		}
		if(isNew){
			$scope.editor.setValue("");
		}
	});
	$scope.insert = function(){
		if($scope.outBind.name == undefined){
			return;
		}
		$scope.editor.insert("$"+$scope.outBind.name);
		$scope.outBind = {};
		$scope.editor.focus();
	}

}