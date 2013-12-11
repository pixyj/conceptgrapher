import simplejson

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from .models import Quiz, UserQuizAttempt, AnonQuizAttempt


def create_attempt(request):

	attrs = simplejson.loads(request.body)
	quiz = get_object_or_404(Quiz, pk=attrs.get("quizId"))
	attrs['quiz'] = quiz
	del attrs['quizId']

	if request.user.is_authenticated():
		attrs['user'] = request.user
		model_class = UserQuizAttempt
	else:
		#import pdb;pdb.set_trace()
		model_class = AnonQuizAttempt
		if not request.session.session_key:
			print 'creating session_key'
			request.session.save()
			request.session.modified = True
		attrs['session_key'] = request.session.session_key

	try:
		model_class.objects.create(**attrs)
	except IntegrityError:
		return HttpResponse(status=400)

	return HttpResponse("OK")
