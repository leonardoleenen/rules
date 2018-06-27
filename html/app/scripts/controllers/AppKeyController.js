function AppKeyController( $scope,   $mdDialog,   item,   $mdToast,   $rootScope, $http, dataService, $rootScope) {

    $scope.matrixTable = [
        {
            writeName: "WriteRule",
            readName: "ReadRule",
            readableType: "Reglas"
        },{
            writeName: "WriteTable",
            readName: "ReadTable",
            readableType: "Tablas"
        },{
            writeName: "WriteCatalog",
            readName: "ReadCatalog",
            readableType: "Dominios"
        },{
            writeName: "WriteSimulation",
            readName: "ReadSimulation",
            readableType: "Escenarios"
        },{
            writeName: "WriteEntity",
            readName: "ReadEntity",
            readableType: "Entidades"
        },{
            writeName: "WriteLists",
            readName: "ReadLists",
            readableType: "Listas"
        },{
            writeName: "WriteInstrument",
            readName: "ReadInstrument",
            readableType: "Instrumentos Norm."
        },{
            writeName: "WriteFunction",
            readName: "ReadFunction",
            readableType: "Funciones"
        },{
            writeName: "WriteFormula",
            readName: "ReadFormula",
            readableType: "Formula"
        }
    ]

    $scope.basicExec = function(){
        if(item){
            $scope.key = item;
        }else{
            $scope.key = {
                name: "",
                description: "",
                matrix : {

                }
            }
        }
    };

    $scope.basicExec();

    $scope.closeDialog = function(){
        $mdDialog.hide();
    }
    $scope.save = function(){
        if($scope.key.name != ""){
            $http({
                method: 'POST',
                url: dataService.commonUrl+'/'+dataService.apiRegisterKey,
                headers: {
                    "Authorization": $rootScope.token
                },
                data : $scope.key,
              }).success(function(data,headers){
                if(data.success){
                    $mdToast.show($mdToast.simple().content("Guardado Correctamente").position("top right").hideDelay(3000) ); 
                    $scope.closeDialog();
                }else{
                    $mdToast.show($mdToast.simple().content("Hubo un error en el guardado: "+data.message).position("top right").hideDelay(3000) ); 
                }
            });
        }else{
            $mdToast.show($mdToast.simple().content("Nombre no puede estar vacío").position("top right").hideDelay(3000) ); 
            return;
          }
    }

}
