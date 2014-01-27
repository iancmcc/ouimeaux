'use strict';

/* Filters */

angular.module('wemoFilters', []).filter('uppercase', function() {
  return function(input) {
    return input.toUpperCase();
  }
});