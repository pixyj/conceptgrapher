from django.shortcuts import render
from django.http import HttpResponse
from django.db import IntegrityError

from .models import ConceptQuizAttempt
from .forms import ConceptQuizAttemptForm

import simplejson


def create_attempt(request):
	if request.method != 'POST':
		return HttpResponse(status=403)

	attrs = simplejson.loads(request.body)
	if request.user.is_authenticated():
		print 'user is authenticated'
		attrs['user_id'] = request.user.id
		attrs['session_key'] = ''
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
