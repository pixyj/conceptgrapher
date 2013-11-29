from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from uber.serializers import models_to_json
from .models import Topic, Concept

from quiz.views import quiz_to_jsonable_dict

import simplejson

def get_concepts_by_topic(request, topic_slug):
	print 'request for', topic_slug
	topic = get_object_or_404(Topic, slug=topic_slug)
	print "got topic", topic
	json_concepts = models_to_json(topic.concept_set.all())
	return HttpResponse(json_concepts, content_type="application/json")


def get_quizzes_by_concept_id(request, concept_id):
	concept = get_object_or_404(Concept, pk=concept_id)
	quizzes = [concept_quiz.quiz for concept_quiz in concept.conceptquiz_set.all()]
	jsonable_quizzes = [quiz_to_jsonable_dict(quiz) for quiz in quizzes]
	json_quizzes = simplejson.dumps(jsonable_quizzes)
	return HttpResponse(json_quizzes, content_type="application/json")


