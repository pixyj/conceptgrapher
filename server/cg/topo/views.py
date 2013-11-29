from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

from uber.serializers import models_to_json
from .models import Topic

def get_concepts_by_topic(request, topic_slug):
	print 'request for', topic_slug
	topic = get_object_or_404(Topic, slug=topic_slug)
	print "got topic", topic
	json_concepts = models_to_json(topic.concept_set.all())
	return HttpResponse(json_concepts, content_type="application/json")



