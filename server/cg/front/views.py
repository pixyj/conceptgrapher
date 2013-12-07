import simplejson

from django.shortcuts import render, get_object_or_404
from topo.models import Topic, Concept
from quiz.models import Quiz

def render_concept(request, topic_slug, concept_slug):
	topic = get_object_or_404(Topic, slug=topic_slug)
	concept = get_object_or_404(Concept, topic=topic, slug=concept_slug)
	
	quizzes = Quiz.objects.filter(concept=concept).all()
	if request.user.is_authenticated():
		user = request.user
		attrs = [quiz.to_dict_with_user_attempts(user) for quiz in quizzes]
	else:
		attrs = [quiz.to_dict_with_session_attempts() for quiz in quizzes]


	json_attrs = simplejson.dumps(attrs)	
	return render(request, "concept.html", 
		{"json_attrs": json_attrs, "topic": topic, "concept": concept})


