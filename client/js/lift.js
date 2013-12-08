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
		this.columns.forEach(function(c) {
			head.append($("<th>").html(c))
		});
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
}

