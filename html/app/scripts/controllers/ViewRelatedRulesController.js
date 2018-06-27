app.controller('ViewFactController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog', '$state', 'array',
							  function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog,   $state,   array) {
	$scope.array = array;

	$scope.accept = function(){
		$mdDialog.hide();
	};

	function rebuildDates (values){
		angular.forEach(values, function(value, key){
			if(value.type == "object"){
				rebuildDates(value.properties);
			}
			if(value.type=="date"){
				value.value = value.value != undefined ? new Date(value.value) : undefined;
			}
		});
	}
}]);
