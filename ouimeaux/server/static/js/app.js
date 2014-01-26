'use strict';

angular.module('WemoServer', ['wemoServices'])
  .config(['$routeProvider', '$locationProvider',
      function($routeProvider, $locationProvider) {
        $routeProvider
    .when('/', {
      templateUrl: 'static/partials/landing.html',
    controller: IndexController
    })
  .when('/about', {
    templateUrl: 'static/partials/about.html',
  controller: AboutController
  })
  .otherwise({
    redirectTo: '/'
  });

$locationProvider.html5Mode(true);
}]);