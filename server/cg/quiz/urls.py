from django.conf.urls import patterns, include, url

urlpatterns = patterns('quiz.views',
	url(r'^attempt/create/$', 'create_attempt'),	
)


