var ConceptResourceView = BaseView.extend({
	template: "#concept-resource-template",
	tagName: "li"
});

var ConceptResourceListView = ListView.extend({
	tagName: "ul",
	SingleView: ConceptResourceView,
	navLi: "#resources-li"
});

_.extend(ConceptResourceListView.prototype, ContainerMixin);

var ConceptResource = Backbone.Model.extend({

});

var ConceptResourceCollection = Backbone.Collection.extend({
	model: ConceptResource,
	url: function() {
		if(!this.conceptId) {
			console.log("conceptId not set");
		}
		return "/api/topo/concept/" + String(this.conceptId) + "/resources";
	}
});


