app.controller('NormativeController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$localStorage', '$rootScope', '$mdDialog','$state',
                            function($scope,    $http,   dataService,   $stateParams,  $mdToast,   $localStorage,   $rootScope,   $mdDialog,$state) {

  $scope.instrument = {
    "id":null,
    "name": null,
    "description": "",
    "vigency_date":0,
    "ending_date":0,
    "signature_date":0,
    "application_date":0,
    "files":[],
    "rules": [],
    "tables": []
  }

  $scope.rules = [];

  $scope.selectedRules = [];

  $scope.tables = [];

  $scope.selectedTables = [];

  var b64toBlob = function(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
  }

  $scope.downloadFile = function(instName,fileName,fileType){

    $http({
      method: 'GET',
      url: dataService.commonUrl+'/'+dataService.getNormativeFile+'/'+instName+'/'+fileName,
      headers: {"Authorization": $scope.token}
    }).success(function(data,headers){
      if(data.success){
        bb =b64toBlob(data.response, fileType);
        /*window.open(URL.createObjectURL(bb));*/
        url = URL.createObjectURL(bb)
        var a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        a.href = url
        a.download = fileName
        a.click();
        /*window.URL.revokeObjectURL(url);*/
      }else{
        console.log(data.message);
      }
    });

  }

  $scope.files = []

  $scope.instNameForPath = ''

  $scope.basicExec = function(){
    if($stateParams.normative){
      $http({
        method: 'GET',
        url: dataService.commonUrl+'/'+dataService.findNormative+'/'+$stateParams.normative,
        headers: {"Authorization": $scope.token}
      }).success(function(data,headers){

        if(data.success){

          $scope.instrument.id = data.response.id;

          $scope.instrument.name = data.response.name;

          $scope.instrument.description = data.response.description;

          if(isNaN(data.response.vigency_date))
            $scope.instrument.vigency_date = new Date(data.response.vigency_date);

          if(isNaN(data.response.ending_date))
            $scope.instrument.ending_date = new Date(data.response.ending_date);

          if(isNaN(data.response.signature_date))
            $scope.instrument.signature_date = new Date(data.response.signature_date);

          if(isNaN(data.response.application_date))
            $scope.instrument.application_date = new Date(data.response.application_date);

          $scope.instrument.files = data.response.files;

          if(data.response.rules)
            $scope.instrument.rules = data.response.rules;

          if(data.response.tables)
            $scope.instrument.tables = data.response.tables;

          $scope.instNameForPath = $scope.instrument.name.replace(/ /g,'_')
        }

        getRules();
        getTables();
      });
    }else{
      getRules();
      getTables();
    }
  };

  var getRules = function(){

    $http({
      method: 'GET',
      url: dataService.commonUrl+'/'+dataService.findRules,
      headers: {"Authorization": $scope.token}
    }).success(function(data,headers){
      if(data.success){
        $scope.rules = data.response;
      }
      reloadInstrumenRules();
    });

  };

  var getTables = function(){

    $http({
      method: 'GET',
      url: dataService.commonUrl+'/'+dataService.findTables,
      headers: {"Authorization": $scope.token}
    }).success(function(data,headers){
      if(data.success){
        $scope.tables = data.response;
      }
      reloadInstrumenTables();
    });

  }

  var reloadInstrumenRules = function(){
      for(i in $scope.instrument.rules){
        for(e in $scope.rules){
          if($scope.rules[e].id == $scope.instrument.rules[i].id){
            $scope.rules[e].ticked = true;
            break;
          }
      }
    }
  }

  var reloadInstrumenTables = function(){
    for(i in $scope.instrument.tables){
        for(e in $scope.tables){
          if($scope.tables[e].id == $scope.instrument.tables[i].id){
            $scope.tables[e].ticked = true;
            break;
          }
      }
    }
  }

  $scope.delFile = function(index,fName){
    $http({
      method: 'POST',
      url: dataService.commonUrl+'/'+dataService.removeNormativeFile,
      headers: {
        "Authorization": $scope.token
      },
      data: {"id":$scope.instrument.id,"file":fName}
    }).success(function(data,headers){
      if(data.success){
        $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
        $scope.instrument.files.splice(index,1);
      }else{
        $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000) );
      }
    });
  }


  var checkDates = function(date1,date2){
    if(date1==undefined || date1=="" || date1==0){
      return "Debe ingresar una fecha de aplicacion";
    }
    if(date2==undefined || date2=="" || date2==0){
      return "Debe ingresar una fecha de finalizacion";
    }
    if(Date.parse(date1)>Date.parse(date2)){
      return "La fecha de aplicacion no puede ser menor a la de finalizacion";
    }
    return "";
  }

  $scope.save = function(type) {
    $scope.upload($scope.files, type);
  }

  $scope.upload = function (files, type){

    if($scope.instrument.name==undefined || $scope.instrument.name==""){
      $mdToast.show($mdToast.simple().content("Debe ingresar un nombre para el instrumento normativo").position("top right").hideDelay(3000) );
      return;
    }

    if($scope.instrument.description==undefined || $scope.instrument.description==""){
      $mdToast.show($mdToast.simple().content("Debe ingresar una descripcion para el instrumento normativo").position("top right").hideDelay(3000) );
      return;
    }

    if($scope.instrument.vigency_date==undefined || $scope.instrument.vigency_date=="" || $scope.instrument.vigency_date==0){
      $mdToast.show($mdToast.simple().content("Debe ingresar una fecha de vigencia").position("top right").hideDelay(3000) );
      return;
    }

    var chek = "";
    chek = checkDates($scope.instrument.application_date,$scope.instrument.ending_date);
    if(chek!=""){
      $mdToast.show($mdToast.simple().content(chek).position("top right").hideDelay(3000) );
      return;
    }


    for(i in $scope.instrument.files){
      delete $scope.instrument.files[i].$$hashKey
    }

    $scope.instrument.tmpinst = files;

    $scope.instrument.rules = $scope.selectedRules;
    $scope.instrument.tables = $scope.selectedTables;

    $http({
      method: 'POST',
      url: dataService.commonUrl + '/' + dataService.saveNormative,
      headers: {
        "Authorization": $scope.token
      },
      data: $scope.instrument
    }).success(function(data,headers){
      if(data.success){
        $mdToast.show($mdToast.simple().content("Guardado con exito").position("top right").hideDelay(3000));

        if(type=="goBack"){
                    $state.go('app.normatives');
        }else{
            $state.go('app.normative', {normative: data.response.id},{reload:true});
        }
      }else{
        $mdToast.show($mdToast.simple().content("ERROR: "+data.message).position("top right").hideDelay(3000));
      }
    });

  };

  $scope.sizeOnKb = function(size){
    var onKB = size / (1024*1024)
    if(onKB>1){
      return onKB.toFixed(2) +' MB';
    }

    onKB = size / 1024
    return onKB.toFixed(2) + ' KB';
  }

  $scope.nameToShow = function(name){
    if(name.length<=15){
      return name;
    }
    return name.slice(0,13) + '...' + name.substring(name.lastIndexOf("."));
  }

    $scope.goBack = function(){
        var confirm = $mdDialog.confirm()
            .parent(angular.element(document.body))
            .title('Los cambios no guardados se perderán')
            .content('¿Esta seguro que desea volver?')
            .ok('Volver')
            .cancel('Cancelar')

        $mdDialog.show(confirm).then(function() {
          $state.go("app.normatives");
        });
    }

    $scope.showFAQs = function(){
        var parentEl = angular.element(document.body);
        $mdDialog.show({
            parent: parentEl,
            templateUrl: "views/dialogs/faqs-view.html",
            locals: {
                faqs: faqs,
                name: "Instrumentos Normativos"
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
            "description": "Esta pantalla se encarga de la creación/modificación de instrumentos normativos"
        },
        {
            "name": "¿Cual es la utilidad de los intrumentos normativos?",
            "description": "Los intrumentos sirven para darle marco legal a las reglas de uno o varios dominios, esta también le otorga un marco de tiempo de ejecución, deshabilitando la misma cuando la fecha de finalización vence."
        },
        {
           "name": "¿Que datos tengo que poner aquí?",
            "description": "Es necesario que incluya, nombre, las cuatro fechas, y al menos una descripcion, tambien puede adjuntar archivos/imagenes/pdf."
        }
    ];



  $scope.basicExec();

}]);
