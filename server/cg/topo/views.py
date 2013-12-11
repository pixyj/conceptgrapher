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


def get_next_concept(request, concept_id):
	concept_id = int(concept_id)

	concept = get_object_or_404(Concept, pk=concept_id)
	concepts_by_id = get_top_sorted_concept_id_dict()
	concept_list = get_top_sorted_concept_id_list()
	current_index = concepts_by_id[concept_id]
	next_index = current_index + 1
	try:
		next_id = concept_list[next_index]
	except IndexError:
		return HttpResponse(status=404)

	next_concept = Concept.objects.get(pk=next_id)
	response = ConceptSerializer().to_json(next_concept)
	return HttpResponse(response, content_type="application/json")



