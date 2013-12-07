var BaseView = Backbone.View.extend({
	initialize: function() {
		this.$compileTemplate();
		this.init();
		this.render();
	},
	$compileTemplate: function() {
		if(this.template) {
			if(!$(this.template).length) {
				console.error("Invalid template", this.template);
			}
			this.compiledTemplate = _.template($(this.template).html());			
		}
	},
	init: function() {
		//console.log("init: implement in subclass if needed");
	},
	render: function() {
		var html = this.compiledTemplate(this.model.toJSON());
		this.$el.html(html);
	}
});

var ListView = BaseView.extend({
	init: function() {
		this.collection.on("add", this.addView, this);
		this.views = [];
	},
	addView: function(model) {
		var view = new this.SingleView({model: model});
		this.views.push(view);
		this.$el.append(view.$el);
	},
	render: function() {
		var self = this;
		this.collection.models.forEach(function(m) {
			self.addView(m);
		});
	}
});

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
})

var QuizView = BaseView.extend({
	template: "#single-quiz-template",
	events: {
		"click .quiz-submit": "checkAnswer",
		"keyup .quiz-guess": "submitAnswerOnEnter"
	},

	render: function() {
		BaseView.prototype.render.call(this);
		if(this.model.get("isMCQ")) {
			this.renderChoices(this.model.choices.models);
		}
	},
	renderChoices:function(choices) {
		this.choices = [];
		var self = this;
		choices.forEach(function(c) {
			var view = new ChoiceView({model: c});
			self.choices.push(view);
			self.$el.find(".choices").append(view.$el);
		});
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
	},

	checkMCQAnswer: function() {
		var result = true;
		var guesses = "";
		var data;
		for(i = 0; i<this.choices.length; i++) {
			data = this.choices[i].checkAnswer();
			if(data.guess) {
				guesses += data.guess + ";";
			}
			if(!data.result) {
				result = false;
			}
		}
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

var QuizListView = ListView.extend({
	SingleView: QuizView
});


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

});

var AttemptCollection = Backbone.Collection.extend({
	model: Attempt
});

var mk = new Markdown.Converter();

var Quiz = Backbone.Model.extend({
	parse: function(attrs) {
		console.log(attrs);
		this.attempts = new AttemptCollection(attrs.attempts)
		delete attrs.attempts;
		attrs.question = mk.makeHtml(attrs.question);
		attrs.isMCQ = attrs.choices.length !== 0;

		this.choices = new ChoiceCollection(attrs.choices, {parse:true});
		delete attrs.choices;
		return attrs;
	},
	addAttempt: function(attempt) {
		var attempt = new Attempt(attempt);
		this.attempts.add(attempt);
		if(attempt.result) {
			this.set("answered", true);
		}
		//attempt.save();
	}
});


var QuizCollection = Backbone.Collection.extend({
	model: Quiz
});

var init = function() {
	qc = new QuizCollection();
	qc.add(quizData, {parse: true});
	qv = new QuizListView({collection: qc})
	$("#quiz-list").append(qv.$el);
}

$(document).ready(init);
