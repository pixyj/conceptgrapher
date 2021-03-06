import simplejson

from django.core.cache import cache
from django.conf import settings

from topo.models import Topic
from topo.serializers import ConceptSerializer

from .serializers import QuizSerializer


def get_quiz_by_topic_cache_key(topic):
	return "quiz:topic:{}".format(topic.slug)

def get_serialized_quizzes_by_topic(topic):
	cache_key = get_quiz_by_topic_cache_key(topic)
	result = cache.get(cache_key)
	if not result:
		result = get_quizzes_by_topic(topic)
		result = simplejson.dumps(result)
		cache.set(cache_key, result)
	return result

def clear_quizzes_by_topic_cache(topic):
	cache_key = get_quiz_by_topic_cache_key(topic)
	cache.delete(cache_key)

def get_quizzes_by_topic(topic):
	concept_serializer = ConceptSerializer()
	quiz_serializer = QuizSerializer() 

	concepts = topic.get_top_sorted_concepts()
	serialized_concepts = []
	for concept in concepts:
		quiz = concept.quiz_set.all()[0]
		if not quiz:
			if settings.DEBUG:
				assert(False) #At least one quiz per concept must be present
			else:
				continue
		quiz = quiz_serializer.to_dict(quiz)
		concept_dict = concept_serializer.to_dict(concept)
		concept_dict['quiz'] = quiz
		serialized_concepts.append(concept_dict)

	return serialized_concepts	

def set_topic_as_attempted(user_key, topic_id):
	attemped_key = "user_{}:quizattempt:topic:{}".format(user_key, topic_id)
	if not cache.get(attemped_key):
		cache.set(attemped_key, True)

	return attemped_key

	

		