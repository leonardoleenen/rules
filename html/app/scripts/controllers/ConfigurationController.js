app.controller('ConfigurationController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$rootScope', '$mdDialog', '$state',
                                   function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $rootScope,   $mdDialog, $state) {

  $scope.configuration = {};

  var notShowKeys = ["APP_PATH", "ARG_RULZ_PORT", "RULE_DIALECT", "i18n"]

  $scope.readable={
       "APP_PATH": {
           "name": "Directorio de la aplicación",
           "description":"Es el lugar donde se encuentran las fuentes de la aplicación"
       },
       "DEBUG_MODE": {
           "name": "Modo debug",
           "description":"Muestra traces en pantalla"
       },
       "DEV_MODE": {
           "name": "Modo desarrollador",
           "description":"Utiliza caracteristicas de desarrollo"
       },
       "FETCH_SUBORGS_URL": {
           "name": "Url de suborganización",
           "description":"Trae la información de las suborganizaciones del usuario"
       },
       "FILE_STORAGE_BUCKET_PATH": {
           "name": "Directorio de guardado de archivos",
           "description":"Donde se almacenan todos los archivos generados por la plataforma."
       },
       "FILE_STORAGE_SNAPSHOTS": {
           "name": "Directorio de guardado de snapshots",
           "description":"Donde se almacenan los archivos de los snapshots"
       },
       "FILTER_BY_ROLES": {
           "name": "Filtrado por roles",
           "description":"Si la aplicación filtra por roles o no."
       },
       "LOAD_USER_DATA_URL": {
           "name": "URI de datos de usuario",
           "description":"Uri para obtener datos del usuario"
       },
       "LOGGER_CONFIG": {
           "name": "Configuracion de logs",
           "description":"Directorio al archivo de configuración del logger"
       },
       "MODULES_MATRIX_SERVICE": {
           "name": "Matriz de roles",
           "description":"Servicio que devuelve matriz de roles"
       },
       "MONGO_HOST": {
           "name": "Host de mongodb",
           "description":"direccion de host de mongo"
       },
       "MONGO_PORT": {
           "name": "puerto de mongodb",
           "description":"puerto donde se encuentra corriendo mongodb"
       },
       "OAUTH_CREDENTIALS": {
           "name": "Credenciales de oauth",
           "description":"Credenciales de oauth"
       },
       "OAUTH_ENABLED": {
           "name": "Oauth habilitado?",
           "description":"Habilitar o deshabilitar oauth"
       },
       "RULE_SERVER": {
           "name": "Servidor de reglas",
           "description":"URI de servidor de reglas"
       },
       "RULE_SERVER_BASE": {
           "name": "Base del servidor de reglas",
           "description":"servicio de base de servidor de reglas"
       },
       "RULE_SERVER_INSTALL": {
           "name": "Servicio instalador de reglas",
           "description":"URI Servicio instalador de reglas"
       },
       "RULE_SERVER_LIST": {
           "name": "Listado de reglas publicadas",
           "description":"direccion de listado de reglas"
       },
       "RULE_SERVER_TEST": {
           "name": "Test de servidor de reglas",
           "description":"Direccion para probar las reglas en analizador"
       },
       "RULE_SERVER_UNISTALL": {
           "name": "Servicio desinstalador de reglas",
           "description":"Direccion para desinstalar una regla"
       },
       "RULE_SERVER_VALIDATE": {
           "name": "Servicio validador de reglas",
           "description":"Direccion de Servicio validador de reglas"
       },
       "TMP_FOLDER": {
           "name": "Carpeta de temporales",
           "description":"Direccion de carpeta de temporales"
       },
       "SERVICE_PROTECTION": {
            "name": "Protección de Servicios",
            "description": "Habilitación de la securización de los servicios"
       },
       "AUTO_VERSION": {
            "name": "Versionado automatico",
            "description": "Habilita/inhabilita el versionado automatico de escenarios"
       },
       "TTL_KEY_WEBUSER": {
            "name": "Duración Token",
            "description": "Tiempo de duración de la sesión"
       },
       "HANDLED_BY_DIRECTOR": {
            "name": "Director",
            "description": "Habilita/inhabilita el uso del director"
       },
       "NEED_INSTRUMENTS": {
          "name": "Instrumentos Normativos",
          "description": "Indica si son obligatorios los instrumentos normativos para el flujo del sistema"
       }
  }
  $scope.basicExec = function(){
      $http({
        method: 'GET',
        url: dataService.commonUrl+'/'+dataService.getConfigurations,
        headers: {
          "Authorization": $scope.token
        }
      }).success(function(data,headers){

        if(data.success){
          $scope.configuration = data.response;
        }
        else{
          $mdToast.show($mdToast.simple().content("Guardado con exito").position("top right").hideDelay(3000));
        }
      });
  };

  $scope.needToShow = function(key){
    return (notShowKeys.indexOf(key) == -1)
  }

  $scope.saveConfigurations = function(){

    $http({
      method: 'POST',
      url: dataService.commonUrl + '/' + dataService.saveConfigurations,
      headers: {
        "Authorization": $scope.token
      },
      data: $scope.configuration
    }).success(function(data,headers){
      if(data.success){
        $mdToast.show($mdToast.simple().content(data.message).position("top right").hideDelay(3000));
        $scope.basicExec();
      }else{
        $mdToast.show($mdToast.simple().content("ERROR: "+data.message).position("top right").hideDelay(3000));
      }
    });

  }

  $scope.nameToShow = function(name){
    if(name.length<=15){
      return name;
    }
    return name.slice(0,13) + '...' + name.substring(name.lastIndexOf("."));
  }

  $scope.basicExec();

}]);
