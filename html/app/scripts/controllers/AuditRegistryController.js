function AuditRegistryController($scope, $mdDialog, objData, $mdToast, $rootScope){

    $scope.basicExec = function(){
        $scope.data = objData;
    };

      $scope.basicExec();
      console.log("se cargo controller AuditRegistryController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
