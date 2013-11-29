'use strict';

angular.module("cgApp", ['ngResource', 'ngRoute']).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/', {templateUrl: "/static/partials/topic-concepts.html", controller: 'TopicCtrl'});
  //$routeProvider.when('/view2', {templateUrl: 'partials/partial2.html', controller: 'MyCtrl2'});
  //$routeProvider.otherwise({redirectTo: '/view1'});
}]);
