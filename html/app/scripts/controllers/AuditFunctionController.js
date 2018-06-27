function AuditFunctionController($scope, $mdDialog, objData, ace, $mdToast, $rootScope){


    $scope.funct = {
        id : null,
        params : []

    }
    $scope.temp={};

    $scope.types = [{
        type: "void",
        readableType: "Vacío (void)"
    },{
        type: "String",
        readableType: "Texto (String)"
    },{
        type: "Integer",
        readableType: "Numero entero (Integer)"
    },{
        type: "Float",
        readableType: "Numero decimal (Float)"
    },{
        type: "Boolean",
        readableType: "Booleano (Boolean)"
    },{
        type: "Date",
        readableType: "Fecha (Date)"
    },{
        type: "String[]",
        readableType: "Arreglo de textos (String[])"
    },{
        type: "Integer[]",
        readableType: "Arreglo de Numeros enteros (Integer[])"
    },{
        type: "Float[]",
        readableType: "Arreglo de Numeros decimales (Float[])"
    },{
        type: "Boolean[]",
        readableType: "Arreglo de Booleanos (Boolean[])"
    },{
        type: "Date[]",
        readableType: "Arreglo de fechas (Date[])"
    }]

    $scope.basicExec = function(){
        $scope.editor = ace.edit("editor");
        $scope.editor.setTheme("ace/theme/chrome");
        $scope.editor.getSession().setMode("ace/mode/java");
        $scope.editor.setValue($scope.funct.body);

    };

    $scope.funct = objData;

    setTimeout(function(){$scope.basicExec();}, 500);
    console.log("se cargo controller AuditFunctionController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
