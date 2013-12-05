from django.conf.urls import patterns, include, url

urlpatterns = patterns('quant.views',
	url(r'attempt/create$', 'create_attempt'),	
	#url(r'attempt/all$', 'get_all_attempts'),	
	#url(r'attempt/(?P<concept_id>[\d]+)$', 'get_attempts_by_concept_id'),	
)



