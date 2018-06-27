'use strict';

/**
 * @ngdoc function
 * @name app.config:uiRouter
 * @description
 * # Config
 * Config for the router
 */
angular.module('app')
  .run(
    [           '$rootScope', '$state', '$stateParams',
      function ( $rootScope,   $state,   $stateParams ) {
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;
      }
    ]
  )
  .config(['$stateProvider', '$urlRouterProvider', 'MODULE_CONFIG', function ( $stateProvider,   $urlRouterProvider,  MODULE_CONFIG ) {
        $urlRouterProvider
          .otherwise('/');
        $stateProvider
          .state('app', {
            abstract: true,
            views: {
              '': {
                templateUrl: 'views/layout.html'
              },
              'aside': {
                templateUrl: 'views/aside.html'
              },
              'content': {
                templateUrl: 'views/content.html'
              }
            },
            resolve : load(['scripts/controllers/menuController.js'])
          })
            .state('app.rules', {
              url: '/rules',
              templateUrl: 'views/pages/rules.html',
              data : { title: 'Reglas' },
              controller: 'rulesController',
              resolve: load([ 'scripts/controllers/rulesController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            }).state('app.drls', {
              url: '/drls',
              templateUrl: 'views/pages/drls.html',
              data : { title: 'DRLs' },
              controller: 'DRLsController',
              resolve: load(['scripts/controllers/drlsController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            }).state('app.test', {
              url: '/test/:id/:type',
              templateUrl: 'views/pages/test.html',
              data : { title: 'Editor de código DRL' },
              controller: 'TestController',
              resolve: load(['scripts/controllers/TestController.js','aceEditor','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.rulesEditor', {
              url: '/rule/:rule',
              templateUrl: 'views/pages/rules-editor.html',
              data : { title: 'Editor' },
              controller: 'RulesEditorController',
              resolve: load(['scripts/controllers/RulesEditorController.js','aceEditor', 'scripts/controllers/ActionFormulaInlineController.js' ,'scripts/controllers/EntityController.js','scripts/controllers/ViewRelatedRulesController.js', 'scripts/controllers/FunctionRuleController.js','isteven-multi-select', 'scripts/controllers/HandleDateController.js'])
            })
            .state('app.dashboard', {
              url: '/',
              templateUrl: 'views/pages/dashboard.html',
              data : { title: 'Inicio' },
              controller: 'DashboardController',
              resolve: load(['scripts/controllers/DashboardController.js'])
            })
            .state('app.entities', {
              url: '/entities',
              templateUrl: 'views/pages/entities.html',
              data : { title: 'Entidades' },
              controller: 'EntitiesController',
              resolve: load(['scripts/controllers/EntitiesController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.entity', {
              url: '/entity/:entity',
              templateUrl: 'views/pages/entity.html',
              data : { title: 'Entidad' },
              controller: 'EntityController',
              resolve: load(['scripts/controllers/EntityController.js', 'scripts/controllers/ViewRelatedRulesController.js'])
            })
            .state('app.decisionTables', {
              url: '/decision-tables',
              templateUrl: 'views/pages/decision-tables.html',
              data : { title: 'Tabla de Decisiones' },
              controller: 'DecisionTablesController',
              resolve: load(['scripts/controllers/decisionTables.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.decisionTable', {
              url: '/decision-table/:table',
              templateUrl: 'views/pages/desicion-table.html',
              data : { title: 'Tabla de Decisiones' },
              controller: 'DecisionTableController',
              resolve: load(['scripts/controllers/decisionTableController.js','scripts/controllers/EntityController.js', 'scripts/controllers/FunctionRuleController.js', 'isteven-multi-select', 'scripts/controllers/HandleDateController.js', 'scripts/directives/defaultRule.js', 'scripts/directives/differentRule.js'])
            })
            .state('app.catalogs', {
              url: '/catalogs',
              templateUrl: 'views/pages/catalogs.html',
              data : { title: 'Dominios' },
              controller: 'CatalogsController',
              resolve: load(['scripts/controllers/CatalogsController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.catalog', {
              url: '/catalog/:catalog',
              templateUrl: 'views/pages/catalog.html',
              data : { title: 'Dominio' },
              controller: 'CatalogController',
              resolve: load(['ui.select', 'isteven-multi-select' ,'scripts/controllers/CatalogController.js'])
            })
            .state('app.simulations', {
              url: '/simulations',
              templateUrl: 'views/pages/simulations.html',
              data : { title: 'Escenarios' },
              controller: 'SimulationsController',
              resolve: load(['scripts/controllers/SimulationsController.js' , '../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.simulation', {
              url: '/simulation/:simulation',
              templateUrl: 'views/pages/simulation.html',
              data : { title: 'Escenario' },
              controller: 'SimulationController',
              resolve: load(['isteven-multi-select','scripts/controllers/SimulationController.js','scripts/controllers/ViewFactController.js', 'naif.base64', 'scripts/controllers/UploadSimulationFactsController.js',, 'scripts/controllers/AddHttpRequestController.js'])
            })
            .state('app.functions', {
              url: '/functions',
              templateUrl: 'views/pages/functions.html',
              data : { title: 'Funciones' },
              controller: 'FunctionsController',
              resolve: load(['scripts/controllers/FunctionsController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.function', {
              url: '/function/:function',
              templateUrl: 'views/pages/function.html',
              data : { title: 'Función' },
              controller: 'FunctionController',
              resolve: load(['scripts/controllers/FunctionController.js', 'aceEditor'])
            })
            .state('app.formulas', {
              url: '/formulas',
              templateUrl: 'views/pages/formulas.html',
              data : { title: 'Fórmulas' },
              controller: 'FormulasController',
              resolve: load(['scripts/controllers/FormulasController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.formula', {
              url: '/formula/:formula',
              templateUrl: 'views/pages/formula.html',
              data : { title: 'Formula' },
              controller: 'FormulaController',
              resolve: load(['scripts/controllers/FormulaController.js', 'aceEditor'])
            })
            .state('app.lists', {
              url: '/lists',
              templateUrl: 'views/pages/lists.html',
              data : { title: 'Constantes' },
              controller: 'ListsController',
              resolve: load(['scripts/controllers/ListsController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.list', {
              url: '/list/:list',
              templateUrl: 'views/pages/list.html',
              data : { title: 'Constante' },
              controller: 'ListController',
              resolve: load(['scripts/controllers/ListController.js'])
            })
            .state('app.normatives', {
              url: '/normatives',
              templateUrl: 'views/pages/normatives.html',
              data : { title: 'Instrumentos' },
              controller: 'NormativesController',
              resolve: load(['scripts/controllers/NormativesController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.normative', {
              url: '/normative/:normative',
              templateUrl: 'views/pages/normative.html',
              data : { title: 'Instrumentos' },
              controller: 'NormativeController',
              resolve: load(['scripts/controllers/NormativeController.js', 'naif.base64','isteven-multi-select' ])
            })
            .state('app.history', {
              url: '/history',
              templateUrl: 'views/pages/history.html',
              data : { title: 'Historial' },
              controller: 'HistoryController',
              resolve: load(['scripts/controllers/HistoryController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js', 'naif.base64'])
            })
            .state('app.auditory', {
              url: '/auditory',
              templateUrl: 'views/pages/auditory.html',
              data : { title: 'Auditorias' },
              controller: 'AuditoryController',
              resolve: load(['scripts/controllers/AuditoryController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js', 'scripts/controllers/AuditRuleController.js', 'scripts/controllers/AuditTableController.js', 'scripts/controllers/AuditEntityController.js', 'scripts/controllers/AuditCatalogController.js', 'scripts/controllers/AuditFormulaController.js', 'scripts/controllers/AuditFunctionController.js', 'aceEditor', 'scripts/controllers/AuditListController.js', 'scripts/controllers/AuditInstrumentController.js', 'scripts/controllers/AuditRegistryController.js', 'scripts/directives/defaultRuleAudit.js', 'scripts/directives/differentRuleAudit.js'])
            })
            .state('app.publications', {
              url: '/publications',
              templateUrl: 'views/pages/publications.html',
              data : { title: 'Publicaciones' },
              controller: 'PublicationsController',
              resolve: load(['scripts/controllers/PublicationsController.js','../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('app.configuration', {
              url: '/configuration',
              templateUrl: 'views/pages/configuration.html',
              data : { title: 'Configuraciones' },
              controller: 'ConfigurationController',
              resolve: load(['scripts/controllers/ConfigurationController.js'])
            })
            .state('app.appkeys', {
              url: '/appkeys',
              templateUrl: 'views/pages/appkeys.html',
              data : { title: 'Administrador de appkeys' },
              controller: 'AppkeysController',
              resolve: load(['scripts/controllers/AppkeysController.js', 'scripts/controllers/AppKeyController.js' ,'../libs/angular/angular-ui-grid/csv.js', '../libs/angular/angular-ui-grid/pdfmake.js','../libs/angular/angular-ui-grid/vfs_fonts.js'])
            })
            .state('404', {
              url: '/404',
              templateUrl: 'views/pages/404.html'
            })
            .state('505', {
              url: '/505',
              templateUrl: 'views/pages/505.html'
            })
            .state('access', {
              url: '/access',
              template: '<div class="indigo bg-big"><div ui-view class="fade-in-down smooth"></div></div>'
            })
            .state('access.signin', {
              url: '/signin',
              templateUrl: 'views/pages/signin.html'
            })
            .state('access.signup', {
              url: '/signup',
              templateUrl: 'views/pages/signup.html'
            })
            .state('access.forgot-password', {
              url: '/forgot-password',
              templateUrl: 'views/pages/forgot-password.html'
            })
            .state('access.lockme', {
              url: '/lockme',
              templateUrl: 'views/pages/lockme.html'
            })
          ;


          function load(srcs, callback) {
            return {
                deps: ['$ocLazyLoad', '$q',
                  function( $ocLazyLoad, $q ){
                    var deferred = $q.defer();
                    var promise  = false;
                    srcs = angular.isArray(srcs) ? srcs : srcs.split(/\s+/);
                    if(!promise){
                      promise = deferred.promise;
                    }
                    angular.forEach(srcs, function(src) {
                      promise = promise.then( function(){
                        angular.forEach(MODULE_CONFIG, function(module) {
                          if( module.name == src){
                            if(!module.module){
                              name = module.files;
                            }else{
                              name = module.name;
                            }
                          }else{
                            name = src;
                          }
                        });
                        return $ocLazyLoad.load(name);
                      } );
                    });
                    deferred.resolve();
                    return callback ? promise.then(function(){ return callback(); }) : promise;
                }]
            }
          }
      }
    ]
  );
