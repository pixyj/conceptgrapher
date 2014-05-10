/******************************************************************************
*	Views -> More ParentViews, see lift.js
******************************************************************************/


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
		this.showNextUnanswered(true);
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
		App.router.navigate("quiz/" + model.get("id") + "/");
	},
	setNowViewByIndex: function(index) {
		var model = this.collection.at(index);
		if(!model) {
			this.allDone();
			return;
		}
		this.setNowViewById(model.get("id"));
	},
	showNextUnanswered: function(navigate) {
		var length = this.collection.models.length;
		var i, model;
		for(i = 0; i < length; i++) {
			model = this.collection.at(i);
			if(model.get("answered") === false) {
				this.setNowViewById(model.get("id"));
				return;
			}
		}
		if(navigate) {
			App.router.navigate("#done", {trigger: true});
		}

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
		this.$el.prop("id", "stats-table");
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
* Router and Initialization
******************************************************************************/
var AppRouter = BaseRouter.extend({
	routes: {
		"quiz/:id/": "setQuiz",
		"quiz/:id": "redirectToSetQuiz",
		"resources/": "setResources",
		"stats/": "showStats",
		"done": "showDone",
		"": "setFirstQuiz",

	},
	setFirstQuiz: function() {	
		var view = this.setCurrentView("quiz");
		view.showNextUnanswered(false);
	},
	
	setQuiz: function(id) {
		this.setCurrentView("quiz");
		this.currentView.setNowViewById(id);
	},

	redirectToSetQuiz: function(id) {
		this.setQuiz(id);
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
	return resources;
};


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

	var rootUrl = function() {
		return "/" + App.topicSlug + "/" + App.conceptSlug + "/";
	}();

	App.router = new AppRouter({views: views});
	Backbone.history.start({pushState: true, root: rootUrl});
	App.routeWithoutReload(App.router, rootUrl);

	progressView = new ConceptProgressView({model: qc.detailedAttemptCollection.aggregateStats});
	progressView.render();

	Backbone.on("quizzes:completed", function() {
		App.router.navigate("#done", {trigger: true});	
	});
	

	App.isIniting = false;



};

$(document).ready(init);