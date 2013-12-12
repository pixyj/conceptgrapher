/******************************************************************************
*App -> Container object. 
******************************************************************************/
var App = {

}

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


