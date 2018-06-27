function AuditEntityController($scope, $mdDialog, objData, $mdToast, $rootScope){

$scope.entity = {
         "schema": {
            "type":"object",
            "properties":{}
         },
        "name" : "",
        "description" : ""
    };

    $scope.values = [{
            value: "string",
            readable: "texto"
        },{
            value: "integer",
            readable: "numero entero"
        },{
            value: "float",
            readable: "numero decimal"
        },{
            value: "date",
            readable: "fecha"
        },{
            value: "object",
            readable: "Objeto"
        },{
            value: "boolean",
            readable: "Verdadero/falso"
    }];

    $scope.basicExec = function(){
        $scope.entity = objData;
    };

      $scope.basicExec();
      console.log("se cargo controller AuditEntityController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
