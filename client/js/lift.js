/******************************************************************************
*	App -> Container object. 
******************************************************************************/
var App = {

};


var BaseView = Backbone.View.extend({
	initialize: function() {
		this.$compileTemplate();
		this.init();
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
		var html;
		if(this.model) {
			html = this.compiledTemplate(this.model.toJSON());			
			this.$el.html(html);
		}
		this.afterRender();
	},
	afterRender: function() {
		//Any focus stuff
	},
	remove: function() {
		this.cleanup();
		this.unbind();
		Backbone.View.prototype.remove.call(this);
	},
	cleanup: function() {

	}
});

var ListView = BaseView.extend({
	init: function() {
		this.collection.on("add", this.addView, this);
		this.views = [];
	},
	renderSingleView: function(model) {
		var view = new this.SingleView({model: model});
		this.views.push(view);
		view.render();
		return view;
	},
	addView: function(model) {
		var view = this.renderSingleView(model);
		this.$el.append(view.$el);
	},
	render: function() {
		var self = this;
		this.collection.models.forEach(function(m) {
			self.addView(m);
		});
		this.afterRender();
	}
});

var TableView = ListView.extend({
	tagName: "table",
	columns: [],
	render: function() {
		var head = $("<thead>");
		var headRow = $("<tr>");
		this.columns.forEach(function(c) {
			headRow.append($("<th>").html(c));
		});
		$(head).append(headRow);
		this.tbody = $("<tbody>");
		this.$el.append(head);
		this.$el.append(this.tbody);
		ListView.prototype.render.call(this);
	},
	addView: function(model) {
		var view = this.renderSingleView(model);
		this.tbody.append(view.$el);
	}
});

var ContainerMixin = {
	afterRender: function() {
		var navLi = $(this.navLi);
		if(!navLi.length) {
			console.error("Error");
		}
		navLi.addClass("active");
	},
	cleanup: function() {
		$(this.navLi).removeClass("active");
	}			
};

var UpdateModelMixin = {
	incr: function(attr, by) {
		by = by || 1;
		var old = this.get(attr);
		this.set(attr, old + by);
		return this;
	},
	decr: function(attr, by) {
		by = by || 1;
		var old = this.get(attr);
		this.set(attr, old - by);
		return this;
	}
};

var ProgressBaseView = Backbone.View.extend({
	initialize: function() {
		var changeEvent = "change:" + this.progressAttr;
		this.model.on(changeEvent, this.render, this);
	},

	render: function() {
		var progress = this.model.get(this.progressAttr);
		progress *= 100;
		var progressPercentage = progress + "%";
		$('.progress .progress-bar').css("width", progressPercentage);
	}
});

var BaseRouter = Backbone.Router.extend({
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
	}
});

App.routeWithoutReload = function(router, rootUrl) {
	$(".route-without-reload").click(function(evt) {

		evt.preventDefault();
		
		var relativeUrlIndex = this.href.indexOf(rootUrl) + rootUrl.length;
		relativeUrl = this.href.slice(relativeUrlIndex);
		
		console.log("route-without-reload");
		router.navigate(relativeUrl, {trigger: true});


	});
};