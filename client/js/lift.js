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
		var html = this.compiledTemplate(this.model.toJSON());
		this.$el.html(html);
	},
	afterRender: function() {
		//Any focus stuff
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
		view.render();
		this.$el.append(view.$el);
	},
	render: function() {
		var self = this;
		this.collection.models.forEach(function(m) {
			self.addView(m);
		});
	}
});