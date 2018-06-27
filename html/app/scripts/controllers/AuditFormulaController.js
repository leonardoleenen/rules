function AuditFormulaController($scope, $mdDialog, objData, $mdToast, $rootScope){


    $scope.selectedItems = [];
    $scope.formula = {};

    $scope.basicExec = function(){
        $scope.formula =objData;
        $scope.selectedItems = objData.selectedItems;
    };

      $scope.basicExec();
      console.log("se cargo controller AuditFormulaController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
