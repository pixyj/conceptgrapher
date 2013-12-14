import simplejson

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import ConceptResource, Concept
from .graph import get_top_sorted_concept_id_dict, get_top_sorted_concept_id_list
from .serializers import ConceptSerializer

def get_resources(request, concept_id):
	concept = get_object_or_404(Concept, pk=concept_id)
	urls = [{"url":resource.url} for resource in concept.conceptresource_set.all()]
	print urls
	return HttpResponse(simplejson.dumps(urls), content_type="application/json")


