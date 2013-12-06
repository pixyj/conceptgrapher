from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError

from uber.serializers import model_to_jsonable_dict, ModelSerializer
from .models import ConceptQuizAttempt
from .forms import ConceptQuizAttemptForm
from topo.serializers import ConceptQuizSerializer
from topo.models import Concept, ConceptQuiz

import simplejson


def create_attempt(request):
	if request.method != 'POST':
		return HttpResponse(status=403)

	attrs = simplejson.loads(request.body)
	if request.user.is_authenticated():
		print 'user is authenticated'
		attrs['user_id'] = request.user.id
		attrs['session_key'] = request.session.session_key
		assert(attrs['session_key'])
	else:
		if not request.session.session_key:
			print 'creating session_key'
			request.session.save()
			request.session.modified = True
		attrs['session_key'] = request.session.session_key

	form = ConceptQuizAttemptForm(attrs)
	if not form.is_valid():
		return HttpResponse("{}".format(form.errors), status=400)
	
	try:
		attempt = ConceptQuizAttempt.objects.create(**attrs)
	except IntegrityError as e:
		return HttpResponse("{}".format(e), status=400)
	
	print attempt

	return HttpResponse("OK")

class QuizAttemptSerializer(ModelSerializer):
	class Meta:
		fields = ['created', 'guess', 'result']

def get_all_attempts(request):
	"""
	Returns all attempts by user including quiz details.
	For the dashboard page
	"""
	if request.method != 'GET':
		return HttpResponse(status=403)


	if request.user.is_authenticated():	
		attempts = ConceptQuizAttempt.objects.filter(user=request.user).all()

	else:
		session_key = request.session.session_key
		if not session_key:
			attempts = []
		else:
			attempts = ConceptQuizAttempt.objects.filter(session_key=session_key).all()

	
	serializer = QuizAttemptSerializer()
	json_attempts = []
	for attempt in attempts:
		attrs = serializer.to_dict(attempt)
		attrs['concept_quiz'] = ConceptQuizSerializer().to_dict(attempt.concept_quiz)
		json_attempts.append(attrs)
		
	response = simplejson.dumps(json_attempts)
	return HttpResponse(response, content_type="application/json")


def get_attempts_by_concept_id(request, concept_id):
	"""
	Returns only attempts. Doesn't join with concept_quiz 
	unlike get_all_attempts. Used in concept-quiz page
	"""
	if request.method != 'GET':
		return HttpResponse(status=403)

	concept = get_object_or_404(Concept, pk=concept_id)
	concept_quiz_ids = [cq.id for cq in concept.conceptquiz_set.all()]


	if request.user.is_authenticated():
		user_filter = ConceptQuizAttempt.objects.filter(user=request.user)
	else:
		session_key = request.session.session_key
		if not session_key:
			user_filter = []
		else:
			user_filter = ConceptQuizAttempt.objects.filter(session_key=session_key)


	concept_quiz_filter = user_filter.filter(concept_quiz_id__in=concept_quiz_ids)		


	serializer = QuizAttemptSerializer()
	json_attempts = []		
	for attempt in concept_quiz_filter.all():
		attrs = serializer.to_dict(attempt)
		json_attempts.append(attrs)

	response = simplejson.dumps(json_attempts)
	return HttpResponse(response, content_type="application/json")



