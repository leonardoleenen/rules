/**
 * @ngdoc function
 * @name app.controller:AppCtrl
 * @description
 * # MainCtrl
 * Controller of the app
 */
 app.config(function($httpProvider) {
		//Enable cross domain calls
		$httpProvider.defaults.useXDomain = true;
});
angular.module('app')
	.controller('AppCtrl', ['$scope', '$translate', '$localStorage', '$window', '$document', '$location', '$rootScope', '$timeout', '$mdSidenav', '$mdColorPalette', 'dataService', '$http', '$q', '$mdDialog', '$state',
				  function ( $scope,   $translate,   $localStorage,   $window,   $document,   $location,   $rootScope,   $timeout,   $mdSidenav,   $mdColorPalette,   dataService,   $http ,  $q ,  $mdDialog ,  $state) {
	$rootScope.token = null;


	$rootScope.getToken = function(){
		return $http({
			method: 'POST',
			url: dataService.commonUrl+'/'+dataService.findToken,
			data: {
				"organization": {
					"organization_id": "luzia"
				}
			}
		}).success(function(data,headers){
			$localStorage.token = data.result.token;
			$rootScope.token = data.result.token;
			//console.log($rootScope.token);
		})
	}
	$rootScope.getMatrixUrl = function(){
		$rootScope.securityMatrix= [];
		return $http({
			method: 'GET',
			url: '/config/initial',
			headers: {"Authorization": $scope.token}
		}).success(function(data,headers){
			if(data.success){
				//console.log("mtrx:" + data.response);
				dataService.ssoDriven = data.response.sso;
				dataService.securityMatrix = data.response.matrixurl;
				dataService.requireInstrument = data.response.instruments;
				dataService.autoVersion = data.response.auto_version;
				$rootScope.$broadcast("initialConfig");
				dataService.initiatedSuccessfully = true;
			}
		})
	}
	$rootScope.getUserDetails = function(){
		return $http({
			method: 'GET',
			url: dataService.userDetails,
			headers: {
				"Authorization": $scope.token
			}
		}).success(function(data,headers){
			if(data.success){
				$rootScope.userName= data.data.cn;
				//console.log($scope.userName);
			}
		})
	}
	$rootScope.getUserRoles = function(){
		return $http({
			method: 'GET',
			url: dataService.securityMatrix,
			headers: {
				"Authorization": $scope.token
			}
		}).success(function(data,headers){
			if(data.success)
				$rootScope.securityMatrix = data.result;
		})
	}
	var getBasicStuff = function(){
		return $http({
	        method: 'GET',
	        url: dataService.commonUrl+'/'+dataService.getRuleServerUrl,
	        headers: {
	        	"Authorization": $rootScope.token
	        }
	  	}).success(function(data,headers){
	  		if(data.success){
	  			$rootScope.runtimeBaseUrl = data.response;
	    	}
	  	});
	}
	$rootScope.doInitialSteps = function(override){
		var defer = $q.defer();
		if($localStorage.token && !override){
			$rootScope.token = $localStorage.token;
			$scope.getMatrixUrl().then(function(data){
				if(data.data.success){
					$scope.getUserDetails().then(function(data){
						if(data.data.success){
							$scope.getUserRoles().then(function(data){
								defer.resolve(data);
							}).then(function(data){
								getBasicStuff();
								dataService.rebuildProgressive();
							});
						}
					})
				}
			})
		}else{
			$scope.getToken().then(function(data){
				if(data.data.success){
					$scope.getMatrixUrl().then(function(data){
						if(data.data.success){
							$scope.getUserDetails().then(function(data){
								if(data.data.success){
									$scope.getUserRoles().then(function(data){
										defer.resolve(data);
									}).then(function(data){
										getBasicStuff();
										dataService.rebuildProgressive();
									})
								}
							})
						}
					})
				}
			})
		}
		return defer.promise;
	}

	$scope.doInitialSteps(true).then(function(data){
		//console.log(data);
	})
	// add 'ie' classes to html
	var isIE = !!navigator.userAgent.match(/MSIE/i) || !!navigator.userAgent.match(/Trident.*rv:11\./);
	isIE && angular.element($window.document.body).addClass('ie');
	isSmartDevice( $window ) && angular.element($window.document.body).addClass('smart');
	// config
	$scope.app = {
		name: 'LuzIa Rulz',
		version: '1.5.0',
		// for chart colors
		color: {
			primary: '#002f86',
			info:    '#00b5ac',
			success: '#d4e05a',
			warning: '#ed135a',
			danger:  '#f44336',
			accent:  '#00adef',
			white:   '#ffffff',
			light:   '#f1f2f3',
			dark:    '#475069'
		},
		setting: {
			theme: {
				primary: 'cyan',
				accent: 'blue',
				warn: 'light-blue'
			},
			asideFolded: true
		},
		search: {
			content: '',
			show: false
		}
	}

	$scope.setTheme = function(theme){
		$scope.app.setting.theme = theme;
	}

	// angular translate
	$scope.langs = {en:'English', zh_CN:'中文'};
	$scope.selectLang = $scope.langs[$translate.proposedLanguage()] || "English";
	$scope.setLang = function(langKey) {
		// set the current lang
		$scope.selectLang = $scope.langs[langKey];
		// You can change the language during runtime
		$translate.use('langKey');
	};
	$http.get("")
	function isSmartDevice( $window ) {
		// Adapted from http://www.detectmobilebrowsers.com
		var ua = $window['navigator']['userAgent'] || $window['navigator']['vendor'] || $window['opera'];
		// Checks for iOs, Android, Blackberry, Opera Mini, and Windows mobile devices
		return (/iPhone|iPod|iPad|Silk|Android|BlackBerry|Opera Mini|IEMobile/).test(ua);
	};

	$scope.getColor = function(color, hue){
		if(color == "bg-dark" || color == "bg-white") return $scope.app.color[ color.substr(3, color.length) ];
		return rgb2hex($mdColorPalette[color][hue]['value']);
	}

	//Function to convert hex format to a rgb color
	function rgb2hex(rgb) {
		return "#" + hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2]);
	}

	function hex(x) {
		var hexDigits = new Array("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f");
		return isNaN(x) ? "00" : hexDigits[(x - x % 16) / 16] + hexDigits[x % 16];
	}

	$rootScope.$on('$stateChangeSuccess', openPage);

	function openPage() {
		$scope.app.search.content = '';
		$scope.app.search.show = false;
		$scope.closeAside();
	}

	$scope.goBack = function () {
		$window.history.back();
	}

	$scope.openAside = function () {
		$timeout(function() { $mdSidenav('aside').open(); });
	}
	$scope.closeAside = function () {
		$timeout(function() { $document.find('#aside').length && $mdSidenav('aside').close(); });
	}
	var force = false; //para usar en eventos de cambio de estado forzado
	$rootScope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
		force = false;
	});
	$rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams){

    	var type = "";
    	switch(fromState.name){
		    	case "app.entity":
		    		type = "entity";
		    	 break;
		    	 case "app.simulation":
		    		type = "simulation";
		    	 break;
		    	 case "app.decisionTable":
		    		type = "table";
		    	 break;
	 	    	 case "app.rulesEditor":
		    		type = "rule";
		    	 break;
		    	 default:
		    	 	type = "";
		    	 break;
	    }

	    // console.log("toState:"+ JSON.stringify(toState));
	    console.debug("toParams:"+ JSON.stringify(toParams));
	    //console.info("fromState:"+ JSON.stringify(fromState));
	    //console.warn("toState:"+ JSON.stringify(toState));
	    if(force){
	    	return;
	    }
	    if(type!=""){
	    	var jsonToCompare = $rootScope.getJson();
	    	event.preventDefault();
		    if(jsonToCompare.id){
		    	// if(!force){

		    	// }
		    	var data = $rootScope.getJson();
			    $http({
			    	"url" : dataService.commonUrl+'/'+dataService.isModified+'/'+type,
					headers: {
						"Authorization": $scope.token
					},
			    	"method" : "POST",
			    	"data": jsonToCompare
			    }).success(function(data){
			    	if(data.success){
			    		if(data.response){
	    			        var confirm = $mdDialog.confirm()
					            .parent(angular.element(document.body))
					            .title('Los cambios no guardados se perderán')
					            .content('¿Esta seguro que desea volver?')
					            .ok('Salir')
					            .cancel('Quedarme aqui')
					        $mdDialog.show(confirm).then(function() {
					            force = true
					            $state.go(toState.name, toParams);
					        });
			    		}else{
			    			force = true
			    			$state.go(toState.name, toParams);
			    		}
			    	}
			    })
			}else{
				if(fromState.name!=toState.name){
					var confirm = $mdDialog.confirm()
			            .parent(angular.element(document.body))
			            .title('Los cambios no guardados se perderán')
			            .content('¿Esta seguro que desea volver?')
			            .ok('Salir')
			            .cancel('Quedarme aqui')
			        $mdDialog.show(confirm).then(function() {
			            force = true
			            $state.go(toState.name, toParams);
					});
				}else{
					force = true
					$state.go(toState.name, toParams);
				}
			}
	    }

	})
}]);

app.config(function($mdThemingProvider) {
	$mdThemingProvider.definePalette('rlzPalette', {
        "50": "#e0f7fa",
        "100": "#b2ebf2",
        "200": "#80deea",
        "300": "#4dd0e1",
        "400": "#26c6da",
        "500": "#00bcd4",
        "600": "#00acc1",
        "700": "#0097a7",
        "800": "#00838f",
        "900": "#006064",
        "A100": "#84ffff",
        "A200": "#18ffff",
        "A400": "#00e5ff",
        "A700": "#00b8d4",
        "contrastDefaultColor": "light",
        "contrastLightColors": "700 800 900",
        "contrastStrongLightColors": "700 800 900"
	});
	$mdThemingProvider.theme('default')
		.primaryPalette('rlzPalette');
});

app.factory('httpInterceptor', function($q, $injector, $rootScope) {
    return {
       request: function(config) {
       		var cookies = $injector.get('$cookies');
            config.headers['Auth-Token'] = cookies.get('token');
			config.headers['User'] = cookies.get('username');
            return config;
        },
      responseError: function(rejection) {
      	var stateService = $injector.get('$state');
      	var mdDialog = $injector.get('$mdDialog');
        if (rejection.status === 428) {
        	//Reobtener token (redis) automaticamente y reintentar el request http.
			var $http = $injector.get('$http');

			var defer = $q.defer();

			$rootScope.doInitialSteps(true).then(function(data){
				defer.resolve();
			}, function(data){
				defer.reject();
			})
			return defer.promise.then(function() {
				rejection.config.headers.Authorization = $rootScope.token;
				return $http(rejection.config);
			});
        } else if (rejection.status === 412){
        	//Reobtener token (director) automaticamente y reintentar el request http.
			var $http = $injector.get('$http');
			var $sce = $injector.get('$sce');

			var defer = $q.defer();
		       var parentEl = angular.element(document.body);
		       mdDialog.show({
			         template:
			           '<md-dialog aria-label="List dialog">' +
			           '  <md-dialog-content>'+
			           ' 	<div layout="row" layout-sm="column" layout-align="space-around">'+
			           '    <md-button class="md-primary">' +
			           '      Por favor espere.' +
			           '    </md-button>' +
			           '	</div>'+
			           '      <iframe style="display: none;" iframe-onload="iframeLoadedCallBack()" width="0" height="0" ng-src="{{urlToIframe}}"></iframe>'+
   			           ' 	<div layout="row" layout-sm="column" layout-align="space-around">'+
    				   '		<md-progress-circular md-mode="indeterminate"></md-progress-circular>'+
  					   '	</div>'+
			           '    <md-button class="md-primary">' +
			           '      <small class="cute"> Estamos renovando su sesión.</small>' +
			           '    </md-button>' +
			           '  </md-dialog-content>' +
			           '</md-dialog>',
			         locals : {
			         	rejection: rejection
			         },
			         controller: RenovateDirectorsSessionController,
			      }).then(function(){
			      	defer.resolve();
			      });

			return defer.promise.then(function() {
				rejection.config.headers.Authorization = $rootScope.token;
				return $http(rejection.config);
			});

        }else{
        	if (rejection.status === 302||rejection.status === 401||rejection.status === 0) {
        		location.reload();
        	}else if (rejection.status === 403 ) {
				stateService.go("404");
	 		} else if (rejection.status >= 500){
				stateService.go("505");
	 		} else if (rejection.status === 408){
	 			stateService.go("404");
	 		} else if (rejection.status === 404){
	 			stateService.go("404");
	 		} else {
	 			location.reload();
	 		}
          	return $q.reject(rejection);
        }
      }
    };
  });

app.config(['$httpProvider', function($httpProvider) {
		//Http Intercpetor to check auth failures for xhr requests
		$httpProvider.interceptors.push('httpInterceptor');
}]);

String.prototype.capitalizeFirstLetter = function() {
		return this.charAt(0).toUpperCase() + this.slice(1);
}
String.prototype.lowerFirstLetter = function() {
    return this.charAt(0).toLowerCase() + this.slice(1);
}

app.filter('removepc', function() {
  return function(item) {
  	var aux = {};
  	for(var i in item){
  		var it = item[i];
  		if(i[0]=="P" && i[1]=="C" && i[2]=="."){
  			continue;
  		}
		aux[i] = it;
  	}
    return aux;
  };
});

app.filter('makeLittle', function() {
  return function(item) {
    if(item){
  	if(item.length>10){
  		return item.substr(0,10)+"...";
  	}else{
  		return item;
  	}
    }
    return item;
  };
});
app.config(function($mdDateLocaleProvider) {
  $mdDateLocaleProvider.months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  $mdDateLocaleProvider.shortMonths = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  $mdDateLocaleProvider.days = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes'];
  $mdDateLocaleProvider.shortDays = ['Do', 'Lu', 'Ma', 'Mie', 'Jue', 'Vie', 'Sab'];
  $mdDateLocaleProvider.weekNumberFormatter = function(weekNumber) {
    return 'Semana ' + weekNumber;
  };
  $mdDateLocaleProvider.parseDate = function(dateString) {
    var m = moment(dateString, 'D/M/YYYY', true);
    return m.isValid() ? m.toDate() : new Date(NaN);
  };
    // Example uses moment.js to parse and format dates.
  $mdDateLocaleProvider.formatDate = function(date) {
  	if(date==null || date == undefined || date == ""){
  		return ""
  	}else{
    	return moment(date).format('D/M/YYYY');
  	}
  };
  $mdDateLocaleProvider.msgCalendar = 'Calendario';
  $mdDateLocaleProvider.msgOpenCalendar = 'Abrir en calendario';
});

app.directive('iframeOnload', [function(){
return {
    scope: {
        callBack: '&iframeOnload'
    },
    link: function(scope, element, attrs){
        element.on('load', function(){
            return scope.callBack();
        })
    }
}}])

app.factory('focus', function($timeout, $window) {
   return function(id) {
     // timeout makes sure that it is invoked after any other event has been triggered.
     // e.g. click events that need to run before the focus or
     // inputs elements that are in a disabled state but are enabled when those events
     // are triggered.
     $timeout(function() {
       var element = $window.document.getElementById(id);
       if(element)
         element.focus();
     });
   };
 });
