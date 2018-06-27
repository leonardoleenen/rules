function AuditTableController($scope, $mdDialog, objData, $mdToast, $rootScope){


  $scope.table = {
        "name":"",
        "entities" : [],
        "rows" : [],
        "default" : [],
        "different" : []
    }
    $scope.catalogs = [];
    $scope.catalog = [];
    $scope.bindings = {};
    $scope.instruments = [];
    $scope.SelectedInstruments = [];


    $scope.rearmarFilas = function(){
        // angular.forEach($scope.table.rows, function(row, rowKey){
        //  angular.forEach(row.entities, function(entity, entityKey){
        //      angular.forEach(entity.conds, function(cond, condKey){
        //          if($scope.table.entities[entityKey].conds[condKey].attrType == "date"){
        //              cond.value = new Date(cond.value);
        //          }
        //      });
        //  });
        // });
    }

    $scope.basicExec = function(){
         $scope.table = objData;

         if(angular.isUndefined($scope.table.default)){
            $scope.table.default = [];
        }

        if(angular.isUndefined($scope.table.different)){
            $scope.table.different = [];
        }

        $scope.rearmarFilas();

        if($scope.table.instruments){
            var instNor = [];
            for(var i in $scope.table.instruments)
                instNor.push($scope.table.instruments[i].name)
            $scope.SelectedInstruments = instNor.join(', ');
        }
    };



      $scope.basicExec();
      console.log("se cargo controller AuditTableController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }



}
