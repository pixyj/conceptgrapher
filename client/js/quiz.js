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
	template: "#choice-template"
})

var QuizView = BaseView.extend({
	template: "#single-quiz-template",
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
			self.$el.find(".choices").append(view.$el);
		});
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

var Quiz = Backbone.Model.extend({
	parse: function(attrs) {
		console.log(attrs);
		this.attempts = new AttemptCollection(attrs.attempts)
		delete attrs.attempts;
		
		attrs.isMCQ = attrs.choices.length !== 0;

		this.choices = new ChoiceCollection(attrs.choices, {parse:true});
		delete attrs.choices;
		return attrs;
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
