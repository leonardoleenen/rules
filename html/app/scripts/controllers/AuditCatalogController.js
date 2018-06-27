function AuditCatalogController($scope, $mdDialog, objData, $mdToast, $rootScope){


    $scope.catalog = {
        name : "",
        description: "",
        rules : [],
        tables : []
    }
    $scope.rules = "";
    $scope.tables = "";

    $scope.basicExec = function(){
        $scope.catalog = objData;
        var rules = [];
        var tables = [];
        for(var i in $scope.catalog.rules){
            rules.push($scope.catalog.rules[i].name);
        }

        for(var i in $scope.catalog.tables){
            tables.push($scope.catalog.tables[i].name);
        }

        $scope.rules = rules.join(", ");
        $scope.tables = tables.join(", ");

    };

      $scope.basicExec();
      console.log("se cargo controller AuditCatalogController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
