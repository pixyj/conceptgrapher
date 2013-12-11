from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^api/topo/', include('topo.urls')),
    url(r'^api/quiz/', include('quiz.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include("front.urls")),
)

