app.controller('DashboardController', ['$scope', '$http', 'dataService', '$stateParams','$mdToast', '$rootScope', '$mdDialog', '$state',
                               function($scope,   $http,   dataService,   $stateParams,  $mdToast,   $rootScope,   $mdDialog,   $state) {
    $scope.count = {
        "function" : "1"
    }
    $scope.doErrorCode = function (code){
        $http({
            method: 'GET',
            url: dataService.commonUrl+"/svc-test/"+code,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){
                $scope.gridOptionsSimple.data = data.response;
            }
        });
    }
    $scope.basicExec = function (){
        dataService.rebuildProgressive().then(function(){
            $scope.count = dataService.serviceCount;
        })

        $http({
            method: 'GET',
            url: dataService.commonUrl+"/"+dataService.serviceCounts,
            headers: {
                "Authorization": $scope.token
            }
          }).success(function(data,headers){
            if(data.success){
                $scope.count = data.response;
            }
        });
    }

    $scope.basicExec();
}])