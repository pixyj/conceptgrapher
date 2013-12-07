from django.shortcuts import render, get_object_or_404
from topo.models import Topic, Concept

def render_concept(request, topic_slug, concept_slug):
	topic = get_object_or_404(Topic, slug=topic_slug)
	concept = get_object_or_404(Concept, topic=topic, slug=concept_slug)
	
	
