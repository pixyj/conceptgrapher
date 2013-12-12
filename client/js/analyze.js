/******************************************************************************
* Views
******************************************************************************/

//Mock for debugging
var TestAnalysisView = Backbone.View.extend({
	initialize: function() {
		this.model.on("change:nowConcept", this.updateConcept, this);
		this.model.on("change:nowQuiz", this.updateQuiz, this);
		this.model.on("change:done", this.onDone);
	},
	updateConcept: function() {
		console.log("nowConcept:", this.model.get("nowConcept").toJSON());
	},
	updateQuiz: function() {
		console.log("nowQuiz", this.model.get("nowQuiz").toJSON());
		console.log(this.model.get("nowQuiz").get("question"));
	},
	makeAttempt: function(result) {
		var attempt = {result: result, guess: Math.random(333)};
		this.model.get("nowQuiz").addAttempt(attempt);
		this.model.onAttempt(result);
		return this;
	},
	onDone: function() {
		console.log("done");
	},
	randomAttempt: function() {
		var result = Math.floor(Math.random() * 10000 % 2) == 0;
		console.log(result);
		this.makeAttempt(result);
	},
	run: function() {
		try {
			for(var i=0; i< 10; i++) {
				this.randomAttempt();
			}
		} catch(e) {
			console.log("error");
		}
	}
});


var ConceptResultsMixin = {
	incrementResults: function(totalResults, result) {
		if(result) {
			totalResults.correct += 1;
		} else {
			totalResults.wrong += 1;
		}
		return totalResults;	
	},
	resultsToString: function(results) {
		return String(results.correct) + String(results.wrong);
	},
	getCorrectRatio: function(results) {
		if(!results.correct && !results.wrong) {
			return 0;
		}
		return (results.correct)/(results.correct + results.wrong);
	},
	getTotalAttempts: function(results) {
		return (results.correct + results.wrong);
	}
}

var ConceptPlusQuizzes = Backbone.Model.extend({
	parse: function(attrs) {
		this.quizzes = new QuizCollection();
		this.quizzes.add(attrs.quizzes, {parse: true});
		delete attrs.quizzes;
		attrs.skill = 0;
		return attrs;
	},
	getAttemptResults: function() {
		var results = {"correct": 0, "wrong": 0};
		var self = this;
		this.quizzes.forEach(function(q) {
			if(q.attempts.length) {
				var result = q.attempts.at(0).get("result");
				self.incrementResults(results, result);
			}
		});
		return results;
	},
	allQuizzesAttemped: function() {
		for(var i=0; i < this.quizzes.length; i++) {
			if(!this.quizzes.at(i).isAttempted()) {
				return false;
			}
		}
	}
});

_.extend(ConceptPlusQuizzes.prototype, ConceptResultsMixin);

var ConceptPlusCollection = Backbone.Collection.extend({
	model: ConceptPlusQuizzes
});

//Too fancy a name?
var TopicSkillAnalysis = Backbone.Model.extend({
	defaults: {
		totalResults: {correct: 0, wrong: 0},
		done: false
	},

	initialize: function(options) {
		this.concepts = options.collection;
		var maxAttempts = this.concepts.length * 2 * 0.25;
		this.set("maxAttempts", maxAttempts);
	},
	start: function() {
		var index = this.concepts.length / 2;
		this.setNextConceptAndQuiz(index);
	},
	setNextConceptAndQuiz: function(index) {
		var concept = this.concepts.at(index);
		var quiz = concept.quizzes.at(0);

		if(quiz.isAttempted()) {
			quiz = concept.quizzes.at(1);
		}
		if(quiz.isAttempted()) {
			console.log("Quiz attempted already", concept, quiz);
		}
		this.set("nowConcept", concept);
		this.set("nowQuiz", quiz);
		console.log("Set next concept", index, concept.toJSON());
	},
	onAttempt: function(result) {
		this.incrementResults(this.get("totalResults"), result);
		var total = this.getTotalAttempts(this.get("totalResults"));
		
		if(total >= this.get("maxAttempts")) {
			this.set("done", true);
			return;
		}
		var results = this.get("nowConcept").getAttemptResults();
		pathMap = {
			"10": "setNextQuizInConcept",
			"20": "moveForward",
			"11": "moveBasedOnPreviousResults",
			"01": "moveBack",
			"02": "moveBack"
		};
		var key = this.resultsToString(results);
		var attemptHandler = pathMap[key];
		if(!attemptHandler) {
			console.error("Invalid result key", results, key);
		}
		this[attemptHandler]();
		return results;
	},
	setNextQuizInConcept: function() {
		var quiz = this.get("nowConcept").quizzes.at(1);
		if(!quiz) {
			//Only one quiz found in concept;
			this.moveForward();
		}
		this.set("nowQuiz", quiz);
	},
	moveForward: function(concept) {
		concept = concept || this.get("nowConcept");
		var index = this.concepts.indexOf(concept);
		if(index === this.concepts.length - 1) {
			this.set("done", true);
			return;
		}
		var ratio = this.getCorrectRatio(this.get("totalResults"));
		var step = ratio >= 0.75 ? 2 : 1;
		var next = index + step;
		if(next >= this.concepts.length) {
			next = this.concepts.length - 1;
		}
		var nextConcept = this.concepts.at(next);
		if(nextConcept.allQuizzesAttemped()) {
			this.moveForward(nextConcept);
		}
		else {
			this.setNextConceptAndQuiz(next);	
		}
	},
	moveBack: function(concept) {
		var concept = concept || this.get("nowConcept");
		var index = this.concepts.indexOf(concept);
		if(index === 0) {
			this.set("done", true);
			return;
		}
		var ratio = this.getCorrectRatio(this.get("totalResults"));
		var step = ratio <= 0.5 ? 2: 1;
		var next = index - step;
		if(next < 0) {
			next = 0;
		}
		var nextConcept = this.concepts.at(next);
		if(nextConcept.allQuizzesAttemped()) {
			this.moveForward(nextConcept);
		}
		else {
			this.setNextConceptAndQuiz(next);	
		}
	},
	moveBasedOnPreviousResults: function() {
		var concept = this.get("nowConcept");
		var index = this.concepts.indexOf(concept);
		var ratio = this.getCorrectRatio(this.get("totalResults"));
		if(ratio >= 0.75) {
			this.moveForward();
		}
		else {
			this.moveBack();
		}
	}


});

_.extend(TopicSkillAnalysis.prototype, ConceptResultsMixin);





var init = function() {
	cc = new ConceptPlusCollection();
	var copy = $.extend(true, conceptsPlusQuizzes, {});
	cc.add(copy, {parse: true});
	run();

}

var run = function() {
	a = new TopicSkillAnalysis({collection: cc});
	v = new TestAnalysisView({model: a});
	a.start();
	v.run();
	console.log(a.toJSON().name)
}


$(document).ready(init);

