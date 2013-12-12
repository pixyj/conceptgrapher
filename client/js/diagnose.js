var init = function() {
	cc = new ConceptPlusCollection();
	cc.add(conceptsPlusQuizzes, {parse: true});
}

$(document).ready(init);

