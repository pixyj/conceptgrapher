from django.conf.urls import patterns, include, url

urlpatterns = patterns('topo.views',
	url(r'^concept/(?P<concept_id>[\d]+)/resources$', 'get_resources'),	

)


