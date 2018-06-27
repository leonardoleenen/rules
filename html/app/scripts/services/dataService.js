/*
* Servicio proveedor de links para datos/requests
*
* Author: Facundo Caselles
*/

app.service('dataService', ['$http', '$rootScope', '$mdDialog', function($http,   $rootScope,   $mdDialog){

    var local = this;
    this.useStorage = false; //use of localstorage or remote/local webservice (demo mode)
    //Common URIs
    this.getRuleServerUrl = "config/RULE_SERVER";
    this.runtimeBaseUrl = "http://localhost:8080";
    this.commonUrl = ".."; //url comun a todos los servicios... ejemplo commonurl+"/"+findtypes deberia dar la url final del servicio rest
    this.findToken = "security/token/create";
    this.isModified = "rulz/status/check" //+type


    //external's ...
    this.loginUrl = "http://labprueba3/garquitectura/aplicaciones/arg.aspx";
    this.securityMatrix = "/security/matrix";
    this.userDetails = "/security/user/get_roles";

    //uso interno propio
    this.findTypes = "rulz/entity/all"; //get all entities
    this.saveEntity = "rulz/entity"; //save entity (add or update)
    this.findEntity = "rulz/entity"; //find entity by id
    this.removeEntity = "rulz/entity/remove"; //remove entity by id in body  {id: "asdas"}
    this.removeEntityAttr = "rulz/check/entity/attribute";
    this.whichRule = "rulz/entity/rules_related";
    this.formCatalogs = "rulz/entity/in_catalogs";
    this.changeEntityAttribute = "rulz/change/entity/attribute";

    this.findCatalogs = "rulz/catalog/all"; //get all catalogs
    this.saveCatalog = "rulz/catalog"; //save catalog (add or update)
    this.findCatalog = "rulz/catalog"; //find catalog by id
    this.removeCatalog = "rulz/catalog/remove"; //remove catalog by id in body  {id: "asdas"}

    this.findRules = "rulz/rule/all"; //get all rules
    this.saveRule = "rulz/rule"; //save rule (add or update)
    this.findRule = "rulz/rule" //find rule by id
    this.removeRule = "rulz/rule/remove";
    this.rulesNotInCatalog = "rulz/rule/notincatalog";
    this.getRuleDRL = "rulz/drl/rule";

    this.saveDRL = "rulz/drls_new";
    this.getAllDRLs = "rulz/drls";
    this.removeDRL = "rulz/drls/remove";
    this.drlTest = "rulz/test";
    this.drlSimulate = "rulz/test/data";
    this.drlInstall = "rulz/test/install";

    this.findSimulations = "rulz/simulation/all";
    this.saveSimulation = "rulz/simulation";
    this.findSimulation = "rulz/simulation";
    this.removeSimulation = "rulz/simulation/remove";
    this.testSimulation = "rulz/simulate";
    this.getSimulationDRL = "rulz/drl/simulation";
    this.getSimulationJsons = "rulz/simulation/jsons"; //POST
    this.getSimulationModel = "rulz/simulation/model/get";

    this.findLists = "rulz/list/all";
    this.saveList = "rulz/list";
    this.findList = "rulz/list";
    this.removeList = "rulz/list/remove";

    this.publish = "rulz/install"
    this.unPublish = "rulz/uninstall"

    this.findFunctions = "rulz/function/all"; //get all functions
    this.saveFunction = "rulz/function"; //save function (add or update)
    this.findFunction = "rulz/function"; //find function by id
    this.removeFunction = "rulz/function/remove"; //remove function by id in body  {id: "asdas"}
    this.simulateFunction = "rulz/function/test";  //POST

    this.findNormatives = "rulz/instrument/all";
    this.saveNormative = "rulz/instrument";
    this.findNormative = "rulz/instrument";
    this.removeNormative = "rulz/instrument/remove";
    this.removeNormativeFile = "rulz/instrument/file/delete";
    this.getNormativeFile = "rulz/files";

    this.findTables = "rulz/table/all";
    this.saveTable = "rulz/table";
    this.findTable = "rulz/table";
    this.removeTable = "rulz/table/remove";
    this.tablesNotInCatalog = "rulz/table/notincatalog";
    this.getTableDRL = "rulz/drl/table";

    this.findPublications = "rulz/publication/all";
    this.publicationInstall = "rulz/install/publication";
    this.publicationUninstall = "rulz/uninstall/publication";
    this.removePublications = "rulz/publication/remove";

    this.findSnapshots = "snapshot/get/all";
    this.exportSnapShot = "snapshot/export";
    this.importSnapshot ="snapshot/import";
    this.newSnapshot = "snapshot/create";
    this.useSnapshot ="snapshot/use";
    this.deleteSnapshot ="snapshot/delete";
    this.editSnapshot ="snapshot/edit";

    this.findFormulas = "rulz/formula/all";
    this.saveFormula = "rulz/formula";
    this.findFormula = "rulz/formula";
    this.removeFormula = "rulz/formula/remove";

    this.getConfigurations = "config/as_dict";
    this.saveConfigurations = "config/save/dict";

    this.findAditoryUsers =  "auditory/registered_users";
    this.searchAuditoryData = "auditory/search";
    this.getAuditoryData = "auditory/getdata";
    this.getAuditoryRegistry = "auditory/getregistry";

    this.apiRegisterKey = "api/register_key";
    this.apiAllKeys = "api/all_keys";
    this.apiRemoveKey = "api/delete_key";
    this.serviceCounts = "rulz/count/all"
    this.serviceCount = [];
    this.hideUiElements = {};
    this.guid = function(){
      function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
          .toString(16)
          .substring(1);
      }
      return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
    }
    //shortcut a alerta md
    this.showAlert = function(title, message) {
        var alert = $mdDialog.alert({
            title: title,
            content: message,
            ok: 'Aceptar'
        });
        $mdDialog.show( alert );
    }

    //habilitacion progresiva de elementos de UI
    this.rebuildProgressive = function(){
        return  $http({
            method: 'GET',
            url: local.commonUrl+"/"+local.serviceCounts,
            headers: {
                "Authorization": $rootScope.token
            }
        }).success(function(data,headers){
            if(data.success){
                local.serviceCount = data.response;
                local.rebuildProgressiveAside();
            }
        });
    }

    this.rebuildProgressiveAside=function(){

        var flag = false;
        this.hideUiElements = {}
        var hide = this.hideUiElements;
        hide.tables = false;
        hide.rules = false;
        hide.catalogs = false;
        hide.simulations = false;
        hide.publications = false;

        return $http({
            method: 'GET',
            url: local.commonUrl+"/config/WIZARD",
            headers: {
            "Authorization": $rootScope.token
            }
        }).success(function(data,headers){

            if(data.success){
                flag = data.response;
                if(flag){
                    $http({
                        method: 'GET',
                        url: local.commonUrl+"/config/NEED_INSTRUMENTS",
                        headers: {
                            "Authorization": $rootScope.token
                        }
                    }).success(function(data,headers){
                        if(data.success){
                            flag = data.response;

                            if(local.serviceCount.entity == 0){
                                hide.tables = true;
                                hide.rules = true;
                                hide.catalogs = true;
                            }

                            if(flag){
                                //WIZARD Y NEED INSTRUMENTS HABILITADOS
                                if(local.serviceCount.instrument == 0 || local.serviceCount.entity == 0){
                                hide.tables = true;
                                hide.rules = true;
                                hide.catalogs = true;
                                }
                            }
                        }

                        if(local.serviceCount.rule==0&&local.serviceCount.table==0){
                            hide.simulations = true;
                        }

                        if(local.serviceCount.simulation == 0 && local.serviceCount.publication == 0){
                            hide.publications = true;
                        }

                        //tests
                        // hide.tables = true;
                        // hide.rules = true;
                        // hide.catalogs = true;
                        // hide.simulations = true;
                        // hide.publications = true;
                    });
            }
            }
        });

    }

}]);
