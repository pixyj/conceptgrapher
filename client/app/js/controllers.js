'use strict';

/* Controllers */

angular.module("cgApp").controller('TopicCtrl', ['$scope', 'TopicConcepts', 
	'QuizAttemptCreateService', 
function($scope, TopicConcepts, QuizAttemptCreateService) {
	$scope.concepts = TopicConcepts.query({topicSlug: "python"});
	window.x = $scope;
	window.attempt = QuizAttemptCreateService;
}]);

