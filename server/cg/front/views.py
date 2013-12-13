import simplejson
from django.shortcuts import render, get_object_or_404

from topo.models import Topic, Concept
from topo.serializers import ConceptPlusQuizCountSerializer

from quiz.models import Quiz, get_unique_user_key, get_topic_stats_by_user
from quiz.diagnose import get_serialized_quizzes_by_topic
from quiz.serializers import AggregateConceptAttemptSerializer

def render_concept(request, topic_slug, concept_slug):
	topic = get_object_or_404(Topic, slug=topic_slug)
	concept = get_object_or_404(Concept, topic=topic, slug=concept_slug)
	quizzes = Quiz.objects.filter(concept=concept).all()
	if request.user.is_authenticated():
		user = request.user
		attrs = [quiz.to_dict_with_user_attempts(user) for quiz in quizzes]
	else:

		attrs = [quiz.to_dict_with_session_attempts(request.session.session_key) 
				for quiz in quizzes]


	json_attrs = simplejson.dumps(attrs)	
	return render(request, "concept.html", 
		{"json_attrs": json_attrs, "topic": topic, "concept": concept})


def render_topic(request, topic_slug):
	topic = get_object_or_404(Topic, slug=topic_slug)

	if request.user.is_authenticated():
		user_key = get_unique_user_key(user=request.user)
	else:
		if not request.session.session_key:
			user_key = ""
		else:
			user_key = get_unique_user_key(session_key=request.session.session_key)

	#Do the joining on the client.
	concepts, stats = get_topic_stats_by_user(topic=topic, user_key=user_key)

	analysis_test_taken = len(stats) > 0
	if analysis_test_taken:
		concept_serializer = ConceptPlusQuizCountSerializer()
		aggregate_serializer = AggregateConceptAttemptSerializer()
		#heavy duty query. Cache if necesssary
		concepts = [concept_serializer.to_dict(c) for c in concepts]
		stats = [aggregate_serializer.to_dict(a) for a in stats]
		concepts_with_quizzes = []
	else:
		concepts_with_quizzes = get_serialized_quizzes_by_topic(topic)
		concepts, stats = [], []	


	return render(request, "topic.html", {
		"concepts": simplejson.dumps(concepts), 
		"topic": topic, 
		"concepts_with_quizzes": concepts_with_quizzes,
		"stats": simplejson.dumps(stats)
	});

