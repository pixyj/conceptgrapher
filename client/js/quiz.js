/******************************************************************************
*App -> Container object. 
******************************************************************************/
var App = {

}

/******************************************************************************
*	Views -> More ParentViews, see lift.js
******************************************************************************/

var ChoiceView = BaseView.extend({
	template: "#choice-template",
	checkAnswer: function() {
		var guess = this.$el.find("input").is(":checked");
		var store = {
			guess: ""
		};
		store.result = (guess === this.model.get("is_correct"));
		if(guess) {
			store.guess = this.model.get("text");
		}
		return store;
	}
});

var BasicAttemptView = BaseView.extend({
	tagName: "tr",
	template: "#quiz-basic-attempt-template"
});

var BasicAttemptListView = ListView.extend({
	SingleView: BasicAttemptView
});

var QuizView = BaseView.extend({
	template: "#single-quiz-template",
	events: {
		"click .quiz-submit": "checkAnswer",
		"keyup .quiz-guess": "submitAnswerOnEnter",
		"click .quiz-next": "showNext"
	},
	render: function() {
		BaseView.prototype.render.call(this);
		if(this.model.get("isMCQ")) {
			this.renderChoices(this.model.choices.models);
		}
		this.attemptListView = new BasicAttemptListView({
			collection: this.model.attempts,
			el: this.$el.find("tbody")
		});
		this.attemptListView.render();
	},
	afterRender: function() {
		window.scrollTo(0, 0);
		this.$el.find(".quiz-guess").focus();
		this.$el.find(".quiz-wrong-submit").hide();
		this.setQuizGuessStatus();
	},
	renderChoices:function(choices) {
		this.choices = [];
		var self = this;
		choices.forEach(function(c) {
			var view = new ChoiceView({model: c});
			view.render();
			self.choices.push(view);
			self.$el.find(".choices").append(view.$el);
		});
	},
	showNext: function(evt) {
		this.options.parent.showNext(this.model);
	},
	setQuizGuessStatus: function() {
		this.$el.find(".quiz-guess").attr("disabled", this.model.get("answered"));
	},

	checkAnswer: function(evt) {
		var i;
		var attempt = {};
		if(!this.model.get("isMCQ")) {
			attempt.guess = $.trim(this.$el.find(".quiz-guess").val());
			attempt.result = (attempt.guess === String(this.model.get("answer")));
		}
		else {
			attempt = this.checkMCQAnswer();
		}
		console.log(attempt);
		this.model.addAttempt(attempt);
		if(attempt.result) {
			this.options.parent.showNext(this.model);	
		}
		else {
			this.$el.find(".quiz-wrong-submit").show();
		}
		this.setQuizGuessStatus();
	},

	checkMCQAnswer: function() {
		var result = true;
		var guesses = "";
		var data;
		var length = this.choices.length;
		for(i = 0; i<length; i++) {
			data = this.choices[i].checkAnswer();
			if(data.guess) {
				guesses += data.guess + ", ";
			}
			if(!data.result) {
				result = false;
			}
		}
		guesses = guesses.slice(0, guesses.length - 2);
		return {
			result: result,
			guess: guesses
		}

	},
	submitAnswerOnEnter: function(evt) {
		if(evt.keyCode == 13) {
			this.checkAnswer();
		}
	}

});

var QuizSnippetView = BaseView.extend({
	template: "#quiz-snippet-template",
	tagName: "tr",
	init: function() {
		this.model.on("change:answered", this.render, this);
	}
});

var QuizListView = ListView.extend({
	SingleView: QuizSnippetView,
	tagName: "tbody"
});

var QuizContainerView = BaseView.extend({
	template: "#quiz-container-template",
	navLi: "#quiz-li",
	init: function() {
		this.listView = new QuizListView({collection: this.collection});
	},
	render: function() {
		var html = this.compiledTemplate({});
		this.$el.html(html);
		this.listView.render();
		this.$el.find("table").html(this.listView.$el);
		this.afterRender();
	},
	showNext:function(model) {
		this.showNextUnanswered(model);
		//this.setNowViewByIndex(model.get("index") + 1);
	},
	setNowViewById: function(id) {
		var model = this.collection.get(id);
		if(!model) {
			this.allDone();
			return;
		}
		if(this.nowView) {
			this.nowView.unbind();
			this.nowView.remove();
			delete this.nowView;
		}
		this.nowView = new QuizView({
		model: model,
		parent: this
		});
		this.nowView.render();
		$("#quiz-now").html(this.nowView.$el);
		this.nowView.afterRender();
		App.router.navigate("quiz/" + model.get("id"));
	},
	setNowViewByIndex: function(index) {
		var model = this.collection.at(index);
		if(!model) {
			this.allDone();
			return;
		}
		this.setNowViewById(model.get("id"));
	},
	showNextUnanswered: function() {
		var length = this.collection.models.length;
		var i, model;
		for(i = 0; i < length; i++) {
			model = this.collection.at(i);
			if(model.get("answered") === false) {
				this.setNowViewById(model.get("id"));
				return;
			}
		}
		App.router.navigate("#done", {trigger: true});

	},

	allDone: function() {

	}
});

_.extend(QuizContainerView.prototype, ContainerMixin);

var ConceptProgressView = ProgressBaseView.extend({
	progressAttr: "progress" 
});

/******************************************************************************
	STATS
******************************************************************************/

var AttemptDetailedView = BaseView.extend({
	template: "#attempt-detailed-single-view",
	tagName: "tr"
});

var AttemptDetailedTableView = TableView.extend({
	columns: ['Quiz', 'Guess', 'Result'],
	SingleView: AttemptDetailedView,
	afterRender: function() {
		this.$el.addClass("table table-striped table-bordered table-hover");
	}
});

var StatsContainerView = BaseView.extend({
	navLi: "#stats-li",
	init: function() {
		this.attempts = new AttemptDetailedTableView({
			collection: this.collection.detailedAttemptCollection
		});
	},
	render: function() {
		this.attempts.render();
		this.$el.append(this.attempts.$el);
		this.afterRender();
	}
});
_.extend(StatsContainerView.prototype, ContainerMixin);


/******************************************************************************
* Done!
******************************************************************************/
var DoneView = BaseView.extend({
	template: "#done-template"
});

/******************************************************************************
* Models and Collections
******************************************************************************/

var Choice = Backbone.Model.extend({
	parse: function(attrs) {
		attrs.cid = this.cid;
		return attrs;
	}
});

var ChoiceCollection = Backbone.Collection.extend({
	model: Choice
});

var Attempt = Backbone.Model.extend({
	parse: function(attrs) {
		if(!attrs.created) {
			attrs.created = new Date();
		}
		else {
			attrs.created = new Date(attrs.created);
		}
		return attrs;
	},
	url: function() {
		return "/api/quiz/attempt/create/"
	}
});

var AttemptCollection = Backbone.Collection.extend({
	model: Attempt
});

var DetailedAttempt = Backbone.Model.extend({
});

var AggregateStats = Backbone.Model.extend({
	defaults: {
		correctAttempts: 0,
		wrongAttempts: 0,
		totalQuizzes: 0,
		progress: 0
	},
	initialize: function(options) {
		this.options = options;
		this.options.collection.on("add", this.update, this);
		this.on("change:progress", this.onProgressCompleted, this);
	},
	getTotalAttempts: function() {
		return this.correctAttempts + this.wrongAttempts;
	},
	updateProgress: function() {
		var totalQuizzes = this.options.quizModels.length;
		if(totalQuizzes === 0) {
			return 0;
		}
		var progress = this.get("correctAttempts") / totalQuizzes;
		this.set("progress", progress);
		return progress;
	},

	update: function(attempt) {
		attempt = attempt.toJSON();
		if(attempt.result) {
			this.incr("correctAttempts");
		} else {
			this.incr("wrongAttempts");
		}
		this.updateProgress();
	},
	onProgressCompleted: function() {
		if(App.isIniting) {
			return;
		}

		if(this.get("progress") != 1) {
			return;
		}
		App.router.navigate("#done", {trigger: true});
	}
});
_.extend(AggregateStats.prototype, UpdateModelMixin);

var DetailedAttemptCollection = Backbone.Collection.extend({
	model: DetailedAttempt,
	initialize: function(models, options) {
		this.aggregateStats = new AggregateStats({
			collection: this, 
			quizModels: options.quizCollection.models
		});
	}
});

App.mk = new Markdown.Converter();

var Quiz = Backbone.Model.extend({
	parse: function(attrs) {
		this.attempts = new AttemptCollection(attrs.attempts)
		delete attrs.attempts;
		attrs.question = App.mk.makeHtml(attrs.question);
		attrs.isMCQ = attrs.choices.length !== 0;

		this.choices = new ChoiceCollection(attrs.choices, {parse:true});
		delete attrs.choices;
		return attrs;
	},
	addAttempt: function(attempt) {
		if(attempt.result) {
			this.set("answered", true);
		}
		attempt.quizId = this.get("id");
		attempt = new Attempt(attempt, {parse: true});
		this.attempts.add(attempt);
		attempt.save();
	},
});

var QuizCollection = Backbone.Collection.extend({
	model: Quiz,
	parse: function(models) {
		var i = 0;
		models.forEach(function(m) {
			m.index = i;
			i += 1;
		});
		return models;
	},
	initialize: function() {
		this.detailedAttemptCollection = new DetailedAttemptCollection([], {
			quizCollection: this
		});
		this.on("add", this.listenToQuizAttempts, this);

	},
	listenToQuizAttempts: function(quiz) {
		var self = this;
		quiz.attempts.on("add", function(attempt) {
			self.createDetailedAttempt(quiz, attempt);
		});
		quiz.attempts.forEach(function(m) {
			self.createDetailedAttempt(quiz, m);
		})
	},
	createDetailedAttempt: function(quiz, attempt) {
		var attrs = attempt.toJSON();
		attrs.question = quiz.get("question");
		attrs.quizId = quiz.get("id");
		this.detailedAttemptCollection.add(attrs, {parse: true});
	}
});

var NextConcept = Backbone.Model.extend({
	url: function() {
		return "/api/topo/concept/" + this.get("conceptId") + "/next"
	},
	parse: function(attrs) {
		attrs.url = "/" + this.get("topicSlug") + "/" + attrs.slug + "/"
		return attrs;
	}

});

/******************************************************************************
* Router and Initialization
******************************************************************************/
var AppRouter = Backbone.Router.extend({
	routes: {
		"quiz/:id": "setQuiz",
		"": "setFirstQuiz",
		"resources": "setResources",
		"stats": "showStats",
		"done": "showDone"
	},

	constructor: function(options) {
		this.options = options;
		Backbone.Router.call(this, options);
		this.currentView = undefined;
	},

	setCurrentView: function(view) {
		var obj = this.options.views[view];
		if(this.currentView) {
			if(obj.constructor === this.currentView.constructor) {
				return; //View already current;
			}
			this.currentView.remove();
			this.currentView.unbind();
		}
		this.currentView = new obj.constructor(obj.options);
		this.currentView.render();
		$("#content-wrapper").html(this.currentView.$el);
		window.scrollTo(0, 0);
		return this.currentView;
	},

	setFirstQuiz: function() {	
		var view = this.setCurrentView("quiz");
		view.showNextUnanswered();
	},
	setQuiz: function(id) {
		this.setCurrentView("quiz");
		this.currentView.setNowViewById(id);
	},
	setResources: function() {
		this.setCurrentView("resources");

	},
	showStats: function() {
		this.setCurrentView("stats");
	},
	showDone: function() {
		this.setCurrentView("done");
	}

});

var initResources = function() {
	var resources = new ConceptResourceCollection();
	resources.conceptId = conceptId;
	resources.fetch();
	return resources
}


var init = function() {
	App.isIniting = true;
	qc = new QuizCollection();
	resources = initResources();
	App.nextConcept = new NextConcept({topicSlug: topicSlug, conceptId: conceptId});
	App.nextConcept.fetch();
	var views = {
		quiz: {
			constructor: QuizContainerView,
			options: {
				collection: qc
			} 
		},
		resources: {
			constructor: ConceptResourceListView,
			options: {
				collection: resources
			}
		},
		stats: {
			constructor: StatsContainerView,
			options: {
				collection: qc
			}
		},
		done: {
			constructor: DoneView,
			options: {
				model: App.nextConcept
			}
		}
	};
	qc.add(quizData, {parse: true});
	App.router = new AppRouter({views: views});
	Backbone.history.start();

	progressView = new ConceptProgressView({model: qc.detailedAttemptCollection.aggregateStats});
	progressView.render();

	App.isIniting = false;

}

$(document).ready(init);
