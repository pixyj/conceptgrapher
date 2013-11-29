'use strict';

/* Services */

angular.module("cgApp").factory("TopicConcepts", ['$resource', 
function($resource) {
	return $resource("/api/topo/topic/:topicSlug/concepts/");
}]);

