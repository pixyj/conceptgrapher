'use strict';

/* Controllers */

angular.module("cgApp").controller('TopicCtrl', ['$scope', 'TopicConcepts', 
function($scope, TopicConcepts) {
	$scope.concepts = TopicConcepts.query({topicSlug: "python"});
	window.x = $scope;
}]);

