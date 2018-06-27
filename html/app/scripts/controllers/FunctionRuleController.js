function FunctionRuleController($scope, $mdDialog, bindings, cond, valueList, $mdToast, $http, dataService, $rootScope) {
  $scope.bindings = [];
  $scope.bindings2 = bindings;
  $scope.obj = {
    formula:{
      name: "wut",
      formula: null,
      acums: null,
      types: []
    },
    funct:{
      name: "wut"
    },
    flags:[]
  };

  $scope.formulas=[];

  var loadBind = function(){
    /*angular.copy(bindings,$scope.bindings);*/
    for(var i in bindings){
      $scope.bindings.push("$" + i);
    }
    for(var type in valueList){
      for(var index in valueList[type])
        $scope.bindings.push("$PCList." + valueList[type][index].name);
    }

    console.log($scope.bindings);
  };


  $scope.loadFunctions = function(obj){
       $http({
          method: 'GET',
          url: dataService.commonUrl+'/'+dataService.findFunctions,
          headers: {
            "Authorization": $rootScope.token
          },
        }).success(function(data,headers){
          if(data.success){
              console.log(data.response);
              $scope.functions=data.response;
          }
          $scope.loadFormulas();
        });
  };

  $scope.loadFormulas = function(){
    $http({
      method: 'GET',
      url: dataService.commonUrl+'/'+dataService.findFormulas,
      headers: {
        "Authorization": $rootScope.token
      },
    }).success(function(data,headers){
      if(data.success){
        console.log(data.response);
        $scope.formulas=data.response;
      }
      $scope.basicExec();
    });
  };

  $scope.closeDialog = function() {
    $mdDialog.cancel();
  };

  $scope.saveCond = function(){
    if($scope.obj.type=="function"){
      if($scope.obj.funct.name=="wut"){
          $mdToast.show($mdToast.simple().content("Debe seleccionar una función").position("top right").hideDelay(3000) );
          return;
      }

      cond.formula = undefined;

      console.debug($scope.obj);

      if(cond.attr !== undefined && $scope.obj.funct.type != "void" && $scope.obj.funct.type != "Object" && $scope.obj.funct.type.toLowerCase() != cond.attr.type.toLowerCase()){
        $mdToast.show($mdToast.simple().content("El tipo de retorno de la funcion seleccionada debe ser igual al del atributo a comparar ("+cond.attr.type+")").position("top right").hideDelay(3000) );
        return;
      }
      for(var key in $scope.obj.funct.fields){
        var val = $scope.obj.funct.fields[key];
        switch(val.type){
          case "String":
            break;
          case "Integer":
            if(val.name.indexOf("$")==-1 && isNaN(val.name)){
              $mdToast.show($mdToast.simple().content("El valor del atributo "+val.at+" debe ser un numero o el binding de un elemento").position("top right").hideDelay(3000) );
              return;
            }
            break;
          case "Float":
            if(val.name.indexOf("$")==-1 && isNaN(val.name)){
              $mdToast.show($mdToast.simple().content("El valor del atributo "+val.at+" debe ser un numero o el binding de un elemento").position("top right").hideDelay(3000) );
              return;
            }
            break;
          case "Boolean":
            if(val.name.indexOf("$")==-1 && val.name!="true" && val.name!="false"){
              $mdToast.show($mdToast.simple().content("El valor del atributo "+val.at+" debe ser true o false o el binding de un elemento").position("top right").hideDelay(3000) );
              return;
            }
            break;
          case "Date":
            break;
          case "void":
            break;
          default:
            try {
              if(val.name.indexOf("$")==-1){
                var arr = angular.fromJson(val.name);
                if(!Array.isArray(arr)){
                  $mdToast.show($mdToast.simple().content("El valor del atributo "+val.at+" debe ser un arreglo o el binding de un elemento").position("top right").hideDelay(3000) );
                  return;
                }
              }
            }
            catch(err) {
              $mdToast.show($mdToast.simple().content("El valor del atributo "+val.at+" debe ser un arreglo o el binding de un elemento").position("top right").hideDelay(3000) );
              return;
            }
            break;
        }
      }
      cond.funct = $scope.obj.funct;
      cond.value = "null";
      console.log(cond);
      $mdDialog.hide();

    }else if($scope.obj.type=="formula"){
      if($scope.obj.formula.name=="wut"){
          $mdToast.show($mdToast.simple().content("Debe seleccionar una formula").position("top right").hideDelay(3000) );
          return;
      }
      cond.funct = undefined;
      cond.formula = $scope.obj.formula;
      cond.value = "null";
      $mdDialog.hide();
    }

  };

  $scope.useFormula = function(){
    for(index in $scope.formulas){
      if($scope.obj.formula.name == $scope.formulas[index].name){
        $scope.obj.formula.formula = $scope.formulas[index].formula;
        $scope.obj.formula.acums = $scope.formulas[index].acums;
        $scope.obj.formula.types = $scope.formulas[index].types;
        $scope.obj.formula.line = $scope.formulas[index].line;
        break;
      }
    }
  }

  $scope.redoFunctionParams = function(){
    angular.forEach($scope.functions, function(funct, i){
      if(funct.name==$scope.obj.funct.name){
        delete $scope.obj.funct.fields;
        delete $scope.obj.funct.type;
        $scope.obj.funct.type = funct.returnType;
        $scope.obj.funct.fields= [];
        angular.forEach(funct.params, function(param,j){
          $scope.obj.funct.fields.push({
            name: "",
            type: param.type,
            at: param.name
          })
        });
      }
    });
  };

  $scope.basicExec = function(){
    if(cond.funct){
      console.log(cond.funct);
      $scope.obj.type="function";
      $scope.obj.funct.name = cond.funct.name;
      $scope.redoFunctionParams();
      $scope.obj.funct.fields = [];
      angular.forEach(cond.funct.fields,function(param,j){
        $scope.obj.funct.fields.push(param);
      });
    }
    if(cond.formula){
      console.log(cond.formula);
      $scope.obj.type="formula";
      $scope.obj.formula.name = cond.formula.name;
      $scope.obj.formula.formula = $scope.formulas[index].formula;
      $scope.obj.formula.acums = $scope.formulas[index].acums;
      $scope.obj.formula.types = $scope.formulas[index].types;
      $scope.obj.formula.line = $scope.formulas[index].line;
    }
  };

  $scope.cleanThis = function(){
    $scope.obj = {
      type: null,
      formula:{
        name: "wut",
        formula: null,
        acums: null,
        types: []
      },
      funct:{
        name: "wut"
      },
      flags:[]
    }
  }

  $scope.loadFunctions();
  console.log("se cargo controller FunctionRuleController")
  loadBind();

}
