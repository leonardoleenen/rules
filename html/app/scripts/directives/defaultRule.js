app.directive('defaultRule',function(){
  return {
      replace:true,
      restrict: 'A',
      templateUrl: "views/directives/defaultRow.html",
  }
});