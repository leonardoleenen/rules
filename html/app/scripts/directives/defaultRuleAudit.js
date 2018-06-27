app.directive('defaultRuleAudit',function(){
  return {
      replace:true,
      restrict: 'A',
      templateUrl: "views/directives/defaultAuditRow.html",
  }
});
