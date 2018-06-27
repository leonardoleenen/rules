function AuditListController($scope, $mdDialog, objData, ace, $mdToast, $rootScope){

    $scope.list= {
        id: null,
        name: "",
        description:"",
        list: false,
        elements: []
    };

    $scope.basicExec = function(){
        $scope.list.elements={};
        $scope.list = objData;
    };


    $scope.basicExec();
    console.log("se cargo controller AuditListController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
