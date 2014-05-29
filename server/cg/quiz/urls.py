from django.conf.urls import patterns, include, url

urlpatterns = patterns('quiz.views',
	url(r'^attempt/create/$', 'create_attempt'),	
	url(r'^concept/(?P<concept_id>[\d]+)/next$', 'get_next_concept'),
    url(r'^attempts/quiz/(?P<quiz_id>[\d]+)/$', 'get_first_attempts'),
)


