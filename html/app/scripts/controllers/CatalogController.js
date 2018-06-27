app.controller('CatalogController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog','$state',
                            function($scope,    $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog, $state) {  
  $scope.catalogs = $localStorage.catalogs;
  $scope.catalog = {
    name : "",
    description: "",
    rules : [],
    tables : []
  }
  $scope.notInCatalog = {
    rules: [],
    tables: [],
    rulesSelected: [],
    tablesSelected: []
  }
  $scope.rules = [];
  $scope.tables = [];

  var sortNumber = function(a,b){
    return b-a;
  }
  $scope.basicExec = function(){
    if(dataService.useStorage){
        $scope.rules = $localStorage.rules;
          //USE OF STORAGE, NOT IMPLEMENTED FOR DEMO
    }else{
        if($stateParams.catalog){
          $http({
            method: 'GET',
            url: dataService.commonUrl+'/'+dataService.findCatalog+'/'+$stateParams.catalog,
            headers: {"Authorization": $scope.token}
          }).success(function(data,headers){
            if(data.success){
              $scope.catalog = data.response;                
            }
          });
        }
    }
    $scope.getRules();
    $scope.getTables();
  }
  
  $scope.catalogUp = function(index, raw){
    var aux = {}
    angular.copy(raw[index], aux);
    raw.splice(index-1,0,aux);
    raw.splice(index+1,1);
  }
  $scope.catalogDown = function(index, raw){
    var aux = {}
    angular.copy(raw[index], aux);
    raw.splice(index+2,0,aux);
    raw.splice(index,1);
  }
  $scope.catalogRemove = function(index, type){
    var phrase = "";
    var raw = {};
    if(type=="table"){
      phrase = '¿Esta seguro que desea quitar la tabla seleccionada del dominio?'
      raw = $scope.catalog.tables;
      $scope.notInCatalog.tables.push(raw[index])
    }else{
      phrase = '¿Esta seguro que desea quitar la regla seleccionada del dominio?'
      raw = $scope.catalog.rules;
      $scope.notInCatalog.rules.push(raw[index])
    }
    var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Confirmacion')
            .content('¿Esta seguro que desea quitar el dominio seleccionado del escenario de pruebas?')
            .ok('Quitar')
            .cancel('Cancelar')
        $mdDialog.show(confirm).then(function() {
          raw.splice(index,1);
        });
  }

  $scope.addRules = function(){
    for(var i in $scope.notInCatalog.rulesSelected){
      var rule = $scope.notInCatalog.rulesSelected[i];
      $scope.catalog.rules.push({id: rule.id, name: rule.name})
    }
    $scope.notInCatalog.rulesSelected = [];
    var toRemove = [];
    for(var i in $scope.catalog.rules){
      var catalogRule = $scope.catalog.rules[i];
      for(var j in $scope.notInCatalog.rules){
        var notCatalogRule = $scope.notInCatalog.rules[j];
        if(catalogRule.name == notCatalogRule.name){
          toRemove.push(j);
        }
      }
    }
    toRemove.sort(sortNumber);
    console.log(toRemove)
    for(var i in toRemove){
      $scope.notInCatalog.rules.splice(toRemove[i],1);
    }
  }

  $scope.addTables = function(){
    for(var i in $scope.notInCatalog.tablesSelected){
      var rule = $scope.notInCatalog.tablesSelected[i];
      $scope.catalog.tables.push({id: rule.id, name: rule.name})
    }
    $scope.notInCatalog.tablesSelected = [];
    var toRemove = [];
    for(var i in $scope.catalog.tables){
      var catalogRule = $scope.catalog.tables[i];
      for(var j in $scope.notInCatalog.tables){
        var notCatalogRule = $scope.notInCatalog.tables[j];
        if(catalogRule.name == notCatalogRule.name){
          toRemove.push(j);
        }
      }
    }
    toRemove.sort(sortNumber);
    console.log(toRemove)
    for(var i in toRemove){
      $scope.notInCatalog.tables.splice(toRemove[i],1);
    }

  }

  $scope.getRules = function(){
    $http({
      method: 'GET',
      url: dataService.commonUrl+'/'+dataService.rulesNotInCatalog,
      headers: {"Authorization": $scope.token}
    }).success(function(data,headers){
      if(data.success){
        r = data.response
        for (i in r){
          o = {"name":r[i].name,"id":r[i].id}
          $scope.notInCatalog.rules.push(o);
        }      
      }
    });
  };
  

  $scope.getTables = function(){
    $http({
      method: 'GET',
      url: dataService.commonUrl+'/'+dataService.tablesNotInCatalog,
      headers: {"Authorization": $scope.token}
    }).success(function(data,headers){
      if(data.success){
        r = data.response
        for (i in r){
          o = {"name":r[i].name,"id":r[i].id}
          $scope.notInCatalog.tables.push(o);
        }
      }
    }); 
  };
  


  $scope.save = function(type){
    $http({
      method: 'POST',
      url: dataService.commonUrl+'/'+dataService.saveCatalog,
      headers: {"Authorization": $scope.token},
      data: $scope.catalog
    }).success(function(data,headers){
      if(data.success){
        $mdToast.show($mdToast.simple().content("Guardado con exito").position("top right").hideDelay(3000));
        if(type=="goBack"){
          $state.go('app.catalogs');
        }else{
          $state.go('app.catalog', {catalog: data.response.id});
        }
      }else{
        $mdToast.show($mdToast.simple().content("ERROR: "+data.message).position("top right").hideDelay(3000));   
      }
    });
  };
  $scope.goBack = function(){
    var confirm = $mdDialog.confirm()
          .parent(angular.element(document.body))
          .title('Los cambios no guardados se perderán')
          .content('¿Esta seguro que desea volver?')
          .ok('Volver')
          .cancel('Cancelar')
      $mdDialog.show(confirm).then(function() {
        $state.go("app.catalogs");
      });
  }

  $scope.showFAQs = function(){
      var parentEl = angular.element(document.body);
      $mdDialog.show({
          parent: parentEl,
          templateUrl: "views/dialogs/faqs-view.html",
          locals: {
              faqs: faqs,
              name: "Dominios"
          },
          controller: DialogController
      });
      function DialogController($scope, $mdDialog, faqs, name) {
          $scope.faqs = faqs;
          $scope.name = name;
          $scope.closeDialog = function() {
              $mdDialog.hide();
          }
      }
  };

  var faqs = [
      {
          "name": "¿Cual es el objetivo de esta pantalla?",
          "description": "Esta pantalla se encarga de la administración de dominios"
      },
      {
          "name": "¿Que es un dominio?",
          "description": "Un dominio es una agrupación lógica de reglas y tablas para luego poder ser usada en escenarios y posteriormente ser publicadas."
      }

  ];
  $scope.basicExec();

}]);
