var App = {

}

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
		} else {

		}
	},
	afterRender: function() {
		this.$el.find(".quiz-guess").focus();
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

var QuizSnippetView = BaseView.extend({
	template: "#quiz-snippet-template",
	tagName: "tr"
});

var QuizListView = ListView.extend({
	SingleView: QuizSnippetView,
	tagName: "tbody"
});

var QuizContainerView = BaseView.extend({
	template: "#quiz-container-template",
	init: function() {
		this.listView = new QuizListView({collection: this.collection});
	},
	render: function() {
		var html = this.compiledTemplate({});
		this.$el.html(html);
		this.listView.render();
		this.$el.find("table").html(this.listView.$el);
	},
	showNext:function(model) {
		this.setNowViewByIndex(model.get("index") + 1);
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
	allDone: function() {

	}
})


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
	}
});

var AppRouter = Backbone.Router.extend({
	routes: {
		"quiz/:id": "setQuiz",
		"": "setFirstQuiz",
		"resources": "setResources"
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
		return this.currentView;
	},

	setFirstQuiz: function() {	
		var view = this.setCurrentView("quiz");
		view.setNowViewByIndex(0);
	},
	setQuiz: function(id) {
		this.setCurrentView("quiz");
		this.currentView.setNowViewById(id);
	},
	setResources: function() {
		this.setCurrentView("resources");

	}

});

var initResources = function() {
	resources = new ConceptResourceCollection();
	resources.conceptId = conceptId;
	resourceView = new ConceptResourceListView({collection: resources});
	resources.fetch();
	return resourceView;
}

var init = function() {
	qc = new QuizCollection();
	qc.add(quizData, {parse: true});

	initResources();
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
		}
	}

	App.router = new AppRouter({views: views});
	Backbone.history.start();
}

$(document).ready(init);
