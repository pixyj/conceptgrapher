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

AnalysisQuizView = QuizView.extend({
	onSubmit: function(evt) {
		var attempt = this.createAttempt(evt);
		this.options.analysis.analyzeAttempt(attempt);
	}
});

var AnalysisQuizContainerView = BaseView.extend({
	template: "#quiz-container-template",
	init: function() {
		this.model.on("change:nowConcept", this.updateConcept, this);
		this.model.on("change:nowQuiz", this.updateQuiz, this);
	},
	updateConcept: function(model, concept) {
		this.$el.find("#now-concept").html(concept.get("name"));
	},
	updateQuiz: function(model, quiz) {
		if(this.quiz) {
			this.quiz.remove();
			this.quiz.unbind();
		}
		this.quiz = new AnalysisQuizView({model: quiz, analysis: this.model});
		this.quiz.render();
		this.$el.find(".now-quiz").html(this.quiz.$el);
	}

});

var ConceptStatsView = BaseView.extend({
	template: "#concept-stats-template",
	tagName: "tr"
});

var StatsTableView = TableView.extend({
	columns: ["Concept", "Total Questions", "Answered Correctly"],
	SingleView: ConceptStatsView,
	afterRender: function() {
		this.$el.addClass("table table-striped table-bordered");
	}
});

var StatsDashboardContainerView = BaseView.extend({
	template: "#topic-dashboard-template",
	init: function() {
		this.statsTable = new StatsTableView({collection: this.collection});
	},
	render: function() {
		var html = this.compiledTemplate();
		this.$el.html(html);
		this.statsTable.render();
		this.$el.find("#stats-table").html(this.statsTable.$el);
		return this;
	}
});

/******************************************************************************
* Models
******************************************************************************/

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

var ConceptPlusStats = Backbone.Model.extend({
	defaults: {
		results: {
			correct: 0,
			wrong: 0
		}
	},
	parse: function(attrs) {
		if(!attrs.topicSlug) {
			throw new Error("TopicSlug not found");
		}
		return attrs;
	},
	getUrl: function() {
		return "/" + this.get("topicSlug") + "/" + this.get("slug") + "/";
	},
	getProgress: function() {
		var results = this.get("results");
		return (results.correct) / this.get("quiz_count");
	},
	toJSON: function() {
		var attrs = Backbone.Model.prototype.toJSON.call(this);
		attrs.url = this.getUrl();
		attrs.progress = this.getProgress();
		return attrs;
	}
});

var ConceptPlusStatsCollection = Backbone.Collection.extend({
	model: ConceptPlusStats
});

/******************************************************************************
* Analysis
******************************************************************************/
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
	analyzeAttempt: function(result) {
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



/******************************************************************************
* Router And Initialization
******************************************************************************/
var AppRouter = BaseRouter.extend({
	routes: {
		"analysis": "setAnalysis",
		"dashboard": "setDashboard",
	},
	setAnalysis: function() {
		var view = this.setCurrentView("analysis");
		$("#content-wrapper").html(view.$el);
		this.options.model.start();
	},
	setDashboard: function() {
		var view = this.setCurrentView("dashboard");
		$("#content-wrapper").html(view.$el);
	}

});

var init = function() {
	var statsByConcept = {}
	stats.forEach(function(s) {
		statsByConcept[s.concept_id] = s;
	});

	concepts.forEach(function(c) {
		c.topicSlug = topicSlug;
		var stat = statsByConcept[c.id];
		if(stat) {
			c.results = stat;
		}
	});
	cc = new ConceptPlusStatsCollection();
	cc.add(concepts);
	
	v = new StatsDashboardContainerView({collection: cc});
	v.render();
	$("#content-wrapper").html(v.$el);
	return concepts;



}

var init2 = function() {
	cc = new ConceptPlusCollection();
	cc.add(conceptsPlusQuizzes, {parse: true});
	a = new TopicSkillAnalysis({collection: cc});

	var views = {
		analysis: {
			constructor: AnalysisQuizContainerView,
			options: {model: a}
		}
	}

	App.router = new AppRouter({views: views, model: a});
	Backbone.history.start();
	App.router.navigate("#analysis", {trigger: true});

}


var testRun = function() {
	a = new TopicSkillAnalysis({collection: cc});
	v = new TestAnalysisView({model: a});
	a.start();
	v.run();
	console.log(a.toJSON().name);

}


$(document).ready(init);

