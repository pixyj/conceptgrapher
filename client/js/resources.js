var ConceptResourceView = BaseView.extend({
	template: "#concept-resource-template",
	tagName: "li"
});

var ConceptResourceListView = ListView.extend({
	el: "#resources-list",
	SingleView: ConceptResourceView
});

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

var initResources = function() {
	resources = new ConceptResourceCollection();
	resources.conceptId = conceptId;
	resourceView = new ConceptResourceListView({collection: resources});
	resources.fetch();
	return resourceView;
}

