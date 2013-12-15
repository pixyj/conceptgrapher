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
		this.latestAttempt = this.createAttempt(evt);
		this.setQuizGuessStatus();
		if(!this.latestAttempt.result) {
			this.$el.find(".quiz-next").removeClass("btn-success").
			addClass("btn-primary").show().focus();
			this.$el.find(".quiz-submit").hide();
		}
		$(this.$el.find(".quiz-guess")).attr("disabled", true);
	},
	showNext: function() {
		if(!this.latestAttempt) {
			throw new Error("latestAttempt not found");
		}
		this.options.analysis.analyzeAttempt(this.latestAttempt);
	}
});

var GetStartedView = BaseView.extend({

});

var AnalysisQuizContainerView = BaseView.extend({
	template: "#quiz-container-template",
	init: function() {
		this.model.on("change:conceptNow", this.updateConcept, this);
		this.model.on("change:conceptRedirect", this.redirectToConcept, this);
	},
	updateConcept: function(model, concept) {
		this.$el.find("#now-concept").html(concept.get("name"));
		this.updateQuiz(concept.quiz);
	},
	updateQuiz: function(quiz) {
		if(this.quiz) {
			this.quiz.remove();
			this.quiz.unbind();
		}
		this.quiz = new AnalysisQuizView({model: quiz, analysis: this.model});
		this.quiz.render();
		this.$el.find(".now-quiz").html(this.quiz.$el);
	},
	redirectToConcept: function(model, concept) {
		console.log("Get Started at ", concept.toJSON());
		this.quiz.remove();
		this.quiz.unbind();
		this.$el.html("Get Started at " + concept.get("name"));
	}

});

var ConceptStatsView = BaseView.extend({
	template: "#concept-stats-template",
	tagName: "tr"
});

var StatsTableView = TableView.extend({
	columns: ["Concept", "Quizzes", "Answered Correctly"],
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

var ConceptPlusQuiz = Backbone.Model.extend({
	parse: function(attrs) {
		attrs.quiz.showAttempts = false;
		this.quiz = new Quiz(attrs.quiz, {parse: true});
		return attrs;
	}
});

var ConceptPlusQuizCollection = Backbone.Collection.extend({
	model: ConceptPlusQuiz
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
* 1. Fetch all concepts in topic with one quiz each.
* 2. Start off with quiz in median concept.
* 3. If quiz is answered correctly, go to next concept
*    	Continue until quiz is answered incorrectly.
* 4. If not, got to previous concept.
* 5. 	Continue until quiz is answered correctly.
* 6. Direct user to current concept.

Lots of work to be done in routing student to the concept according 
to the level of expertise without wasting time answering known stuff or in 
directing to a concept too advanced. 

Immediate Todo # Speed up when answering streak improves and vice versa.

******************************************************************************/
//Too fancy a name?
var TopicSkillAnalysis = Backbone.Model.extend({
	defaults: {
		done: false
	},

	initialize: function(options) {
		this.concepts = options.collection;
		this.streak = 0;
	},
	start: function() {
		var index = this.concepts.length / 2;
		this.setNextConcept(index);
	},
	setNextConcept: function(index) {
		var concept = this.concepts.at(index);
		this.set("conceptNow", concept);
		
	},
	analyzeAttempt: function(attempt) {
		var conceptNow = this.get("conceptNow");
		var indexNow = this.concepts.indexOf(conceptNow);
		var next;
		var done = false;
		if(attempt.result) {
			next =  indexNow + 1;
			if(this.streak == -1) {
				done = true;
			}
		}
		else {
			if(this.streak == 1) {
				next = indexNow;
				done = true;
			}
			else {
				next = indexNow - 1;
			}
		}
		//Boundary conditions
		//next = this.concepts.length;
		if(next < 0) {
			next = 0;
			done = true;
		}
		else if(next >= this.concepts.length) {
			next = this.concepts.length - 1;
			done = true;
		}
		if(done) {
			this.set("conceptRedirect", this.concepts.at(next));
			return;
		}
		console.log("Done? ", done);
		this.streak = attempt.result ? 1 : -1;
		this.setNextConcept(next);
		this.set("done", done);
	},

});



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
	var testTaken = stats.length > 0;
	//var navigation
	initAnalysis();
	return;
	if(testTaken) {
		initDashboard();
	} else {
		initAnalysis();
	}
}

var initDashboard = function() {
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
	var cc = new ConceptPlusStatsCollection();
	cc.add(concepts);
	
	var v = new StatsDashboardContainerView({collection: cc});
	v.render();
	$("#content-wrapper").html(v.$el);
	var r = new Backbone.Router();
	Backbone.history.start();
	r.navigate("dashboard");
	return concepts;

}

var initAnalysis = function() {
	var cc = new ConceptPlusQuizCollection();
	cc.add(conceptsPlusQuizzes, {parse: true});
	var a = new TopicSkillAnalysis({collection: cc});

	var v = new AnalysisQuizContainerView({model: a});
	v.render();
	$("#content-wrapper").html(v.$el);
	a.start();
	var r = new Backbone.Router();
	Backbone.history.start();
	r.navigate("analysis");
}


var testRun = function() {
	a = new TopicSkillAnalysis({collection: cc});
	v = new TestAnalysisView({model: a});
	a.start();
	v.run();
	console.log(a.toJSON().name);

}


$(document).ready(init);

