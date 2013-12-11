from django.conf.urls import patterns, include, url

urlpatterns = patterns('front.views',
	url(r'^(?P<topic_slug>[\w\d\-]+)/(?P<concept_slug>[\w\d\-]+)/$', 'render_concept'),
	url(r'^(?P<topic_slug>[\w\d\-]+)/$', 'render_topic'),	
)


