from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^api/topo/', include('topo.urls')),
    url(r'^api/quant/', include('quant.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('ang.urls')),
)
