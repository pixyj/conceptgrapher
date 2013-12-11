import simplejson

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.cache import cache

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
