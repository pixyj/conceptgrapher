import simplejson

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.cache import cache

from topo.models import ConceptResource, Concept
from topo.graph import get_top_sorted_concept_id_dict, get_top_sorted_concept_id_list
from topo.serializers import ConceptSerializer

from .models import Quiz, QuizAttempt
from .diagnose import set_topic_as_attempted


def get_unique_user_key_from_request(request):

	if request.user.is_authenticated():
		user_key = QuizAttempt.objects.get_unique_user_key({"user": request.user})
	else:
		#continue Here
		#import ipdb;ipdb.set_trace()
		session_key = request.session.session_key
		if not session_key:
			session_key = request.session._get_or_create_session_key()
			request.session.modified = True	
			request.session.save()
			

		user_key = QuizAttempt.objects.get_unique_user_key({"session_key": session_key})

	return user_key


def create_attempt(request):

	if request.method != 'POST':
		return HttpResponse(status=400)

	attrs = simplejson.loads(request.body)
	quiz = get_object_or_404(Quiz, pk=attrs.get("quizId"))
	attrs['quiz'] = quiz

	#Should delete this in client?
	del attrs['quizId']
	#import pdb;pdb.set_trace()
	attrs['user_key'] = get_unique_user_key_from_request(request)
	if request.user.is_authenticated():
		attrs['user'] = request.user

	try:
		#import ipdb;ipdb.set_trace()
		attempt = QuizAttempt.objects.create_quiz_attempt(**attrs)
		print attempt
	except IntegrityError:
		return HttpResponse(status=400)


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



def get_first_attempts(request, quiz_id):

	queryset = QuizAttempt.objects.filter(quiz_id=quiz_id).filter(attempt_number=1)
	attempts = [attempt.to_dict() for attempt in queryset]

	json_response = simplejson.dumps({"attempts": attempts})
	return HttpResponse(json_response, content_type="application/json")



