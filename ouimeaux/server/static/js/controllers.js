'use strict';

/* Controllers */

angular.module('Ouimeaux.controllers', []).
  controller('IndexCtrl', function ($scope, socket) {
    $scope.data = {}

    $scope.toggleState = function(device) {
      socket.emit('statechange', {
        name:device.name, 
        state:device.state ? 0 : 1
      });
    }

    socket.on("send:devicestate", function(device) {
      $scope.data[device.name] = device;
    });

    socket.on('connect', function () {
      socket.emit('join');
    });

  });
