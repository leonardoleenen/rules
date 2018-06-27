function AuditRuleController($scope, $mdDialog, objData, $mdToast, $rootScope){

    $scope.rules = [];

    var rearmarReglas = function(rule) {
        $scope.name = rule.name;
        $scope.description = rule.description;
        for (var ite = 0; ite < rule.rules.length; ite++) {
            if(rule.rules[ite].parentesis){
                $scope.rules.push(rule.rules[ite]);
                continue;
            }
            if (rule.rules[ite].binding == "$") {
                rule.rules[ite].binding = "";
            }
            $scope.rules.push({
                type : rule.rules[ite].type,
                rawType : undefined, // TODO SEARCH EVENT TYPES
                conds : catchUndefinedBindings(rule.rules[ite].conds),
                plainAttr : rule.rules[ite].plainAttr,
                binding : rule.rules[ite].binding,
                used : true,
                connector: rule.rules[ite].connector
            });
        }

        if (rule.enabled)
            $scope.isEnabled = true;
        else
            $scope.isEnabled = false;
        if (rule.active)
            $scope.active = true;
        if (rule.published)
            $scope.published = true;
        if (rule.name)
            $scope.name = rule.name;
        if (rule.noloop)
            $scope.noloop = rule.noloop;
        if (rule.salience)
            $scope.salience = rule.salience;
        if (rule.duration)
            $scope.duration = rule.duration;
        if (rule.catalog)
            $scope.catalog = rule.catalog;
        if (rule.instruments)
            var names = [];
            for(var i in rule.instruments)
                names.push(rule.instruments[i].name);
            $scope.Instruments = names.join(', ');
        if (rule.atomic)
            $scope.atomic = rule.atomic;
        if (rule.halt)
            $scope.halt = rule.halt;
        if (rule.contraCondicion)
            $scope.contraCondicion = rule.contraCondicion;
        if (rule.limited)
            $scope.limited = rule.limited;

        $scope.actions = rule.actions;

    };

    var catchUndefinedBindings = function(conds) {
        for ( var i in conds) {
            if (conds[i].binding == "$") {
                conds[i].binding = "";
            }
        }
        return conds;
    };

    var rearmarConds = function(conds, rawTypeRef) {
        for (var i = 0; i < conds.length; i++) {
            var cond = conds[i];
            if (!cond.cep) {
                for (var j = 0; j < rawTypeRef.plainAttr.length; j++) {
                    if (typeof cond.attr != "undefined") {
                        if (rawTypeRef.plainAttr[j].type == cond.attr.type && rawTypeRef.plainAttr[j].name == cond.attr.name) {
                            cond.attr = rawTypeRef.plainAttr[j];
                        }
                    }
                }
            }
        };
    };

    $scope.basicExec = function(){
        rearmarReglas(objData)
    };



      $scope.basicExec();
      console.log("se cargo controller AuditRuleController");

      $scope.cancel = function(){
        $mdDialog.cancel();
      }



}
