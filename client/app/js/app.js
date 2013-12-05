'use strict';

angular.module("cgApp", ['ngResource', 'ngRoute', 'ngCookies']).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/', {templateUrl: "/static/partials/topic-concepts.html", controller: 'TopicCtrl'});
  //$routeProvider.when('/view2', {templateUrl: 'partials/partial2.html', controller: 'MyCtrl2'});
  //$routeProvider.otherwise({redirectTo: '/view1'});
}])
// .config(['$httpProvider', '$cookies', function($httpProvider, $cookies) {
// 	$httpProvider.defaults.xsrfCookieName = 'csrftoken';
// 	$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
// }]);

