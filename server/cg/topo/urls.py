from django.conf.urls import patterns, include, url

urlpatterns = patterns('topo.views',
	url(r'topic/(?P<topic_slug>[\w\d\-]+)/concepts$', 'get_concepts_by_topic'),	
	url(r'concept/(?P<concept_id>[\d]+)/quizzes$', 'get_quizzes_by_concept_id'),	
)


