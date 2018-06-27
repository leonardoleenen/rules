function RenovateDirectorsSessionController($scope, $mdDialog, rejection, $sce) {
	if(rejection.data.redirect){
		$scope.urlToIframe = $sce.trustAsResourceUrl(rejection.data.redirect) 
		//$scope.urlToIframe = $sce.trustAsResourceUrl("http://www.google.com.ar");
		console.debug("URL "+$scope.urlToIframe);
	}
	$scope.iframeLoadedCallBack = function() {
	  setTimeout(function(){
	  	$mdDialog.hide(); //espero 2 segundos hasta que la cookie se cargue dentro del iframe
	  	//si el enlace dio 404, en firefox/opera/safari no funciona el cerrar
	  },2000);
	}
}