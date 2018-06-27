app.controller('menuController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$rootScope', '$mdDialog', '$state',
                      	 function( $scope,   $http,   dataService,   $stateParams,  $mdToast,   $rootScope,   $mdDialog,   $state) {

	$scope.hui = dataService.hideUiElements;
}]);