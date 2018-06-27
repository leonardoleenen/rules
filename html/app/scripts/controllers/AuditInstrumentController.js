function AuditInstrumentController($scope, $mdDialog, objData, ace, $mdToast, $rootScope){


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

    $scope.instNameForPath = ''

    $scope.basicExec = function(){

        $scope.instrument.id = objData.id;

        $scope.instrument.name = objData.name;

        $scope.instrument.description = objData.description;

        if(isNaN(objData.vigency_date))
            $scope.instrument.vigency_date = new Date(objData.vigency_date);

        if(isNaN(objData.ending_date))
            $scope.instrument.ending_date = new Date(objData.ending_date);

        if(isNaN(objData.signature_date))
            $scope.instrument.signature_date = new Date(objData.signature_date);

        if(isNaN(objData.application_date))
            $scope.instrument.application_date = new Date(objData.application_date);

        $scope.instrument.files = objData.files;

        if(objData.rules){
            var rules = [];
            for(var i in objData.rules)
                rules.push(objData.rules[i].name);
            $scope.instrument.rules = rules.join(', ');
        }

        if(objData.tables){
            var tables = [];
            for(var i in objData.tables)
                tables.push(objData.tables[i].name);
            $scope.instrument.tables = tables.join(', ');
        }

        $scope.instNameForPath = $scope.instrument.name.replace(/ /g,'_')

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

    $scope.basicExec();
    console.log("se cargo controller AuditInstrumentController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }

}
