/******************************************************************************
*	App -> Container object. 
******************************************************************************/
var App = {

}

/******************************************************************************
*	Views
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
		"click .quiz-submit": "onSubmit",
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
	onSubmit: function(evt) {
		var attempt = this.createAttempt();
		if(attempt.result) {
			this.options.parent.showNext(this.model);	
		}
		else {
			this.$el.find(".quiz-wrong-submit").show();
		}
		this.setQuizGuessStatus();
	},
	createAttempt: function(evt) {
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
		return attempt;
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
			this.onSubmit();
		}
	}

});


/******************************************************************************
* Models and Collections
******************************************************************************/

var Choice = Backbone.Model.extend({
	defaults: {
		hasMultipleAnswers: false,
	},
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
		Backbone.trigger("quizzes:completed");
		
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
	defaults: {
		answered: false,
		hasMultipleAnswers: false,
	},
	parse: function(attrs) {
		this.attempts = new AttemptCollection(attrs.attempts)
		delete attrs.attempts;
		attrs.question = App.mk.makeHtml(attrs.question);
		attrs.isMCQ = attrs.choices.length !== 0;
		if(attrs.isMCQ) {
			attrs.hasMultipleAnswers = this.hasMultipleAnswers(attrs.choices);
		}
		if(attrs.hasMultipleAnswers) {
			attrs.choices.forEach(function(c) {
				c.hasMultipleAnswers = true;
			});
		}
		attrs.choices.forEach(function(c) {
			c.quizId = attrs.id;
		});

		this.choices = new ChoiceCollection(attrs.choices, {parse:true});
		delete attrs.choices;
		return attrs;
	},
	hasMultipleAnswers: function(choices) {
		var i, length;
		var answers = 0;
		for(i = 0, length = choices.length; i < length; i++) {
			if(choices[i].is_correct) {
				answers += 1;
			}
		}
		return answers > 1;
	},

	addAttempt: function(attempt) {
		if(attempt.result) {
			this.set("answered", true);
		}
		attempt.quizId = this.get("id");
		attempt = new Attempt(attempt, {parse: true});
		attempt.save();
		this.attempts.add(attempt);
		
	},
	isAttempted: function() {
		return this.attempts.length > 0; 
	}
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


