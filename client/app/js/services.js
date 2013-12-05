'use strict';

/* Services */

angular.module("cgApp").factory("TopicConcepts", ['$resource', 
function($resource) {
	return $resource("/api/topo/topic/:topicSlug/concepts/");
}]);

angular.module("cgApp").service("QuizAttemptCreateService", 
function($cookies, $http) {
	$http.defaults.xsrfCookieName = 'csrftoken';
	$http.defaults.xsrfHeaderName = 'X-CSRFToken';

	var service = {};
	var url = "/api/quant/attempt/create"
	service.create = function(attrs) {
		$http.post(url, attrs)
	}
	return service;

});

