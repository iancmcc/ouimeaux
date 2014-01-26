'use strict';

angular.module('Ouimeaux', ['Ouimeaux.controllers', 'btford.socket-io'])
.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {
      $routeProvider
        .when('/', {
          templateUrl: 'static/partials/landing.html',
          controller: 'IndexCtrl'
        });
      $locationProvider.html5Mode(true);
    }
]);