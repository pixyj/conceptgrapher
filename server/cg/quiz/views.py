import simplejson

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.cache import cache

from topo.models import ConceptResource, Concept
from topo.graph import get_top_sorted_concept_id_dict, get_top_sorted_concept_id_list
from topo.serializers import ConceptSerializer

from .models import Quiz, UserQuizAttempt, AnonQuizAttempt
from .diagnose import set_topic_as_attempted

def create_attempt(request):

	attrs = simplejson.loads(request.body)
	quiz = get_object_or_404(Quiz, pk=attrs.get("quizId"))
	attrs['quiz'] = quiz
	del attrs['quizId']


	if request.user.is_authenticated():
		attrs['user'] = request.user
		model_class = UserQuizAttempt
		user_cache_key = request.user.id
	else:
		#import pdb;pdb.set_trace()
		model_class = AnonQuizAttempt
		if not request.session.session_key:
			print 'creating session_key'
			request.session.save()
			request.session.modified = True
		attrs['session_key'] = request.session.session_key
		user_cache_key = attrs['session_key'][0:5]

	try:
		model_class.objects.create(**attrs)
	except IntegrityError:
		return HttpResponse(status=400)

	#import pdb;pdb.set_trace()	
	topic_id = quiz.concept.topic.id
	set_topic_as_attempted(user_cache_key, topic_id)	
	return HttpResponse("OK")


def get_next_concept(request, concept_id):
	concept_id = int(concept_id) #Is this safe?

	concept = get_object_or_404(Concept, pk=concept_id)
	concepts_by_id = get_top_sorted_concept_id_dict()
	concept_list = get_top_sorted_concept_id_list()
	current_index = concepts_by_id[concept_id]
	next_index = current_index + 1
	try:
		next_id = concept_list[next_index]
	except IndexError:
		return HttpResponse(status=404)

	next_concept = Concept.objects.get(pk=next_id)
	response = ConceptSerializer().to_json(next_concept)
	return HttpResponse(response, content_type="application/json")



