import simplejson
from django.core.cache import cache

from topo.models import Topic
from topo.serializers import ConceptSerializer

from .serializers import QuizSerializer

def get_serialized_quizzes_by_topic(topic):
	cache_key = "quiz:topic:{}".format(topic.slug)
	result = cache.get(cache_key)
	if not result:
		result = get_quizzes_by_topic(topic)
		result = simplejson.dumps(result)
		cache.set(cache_key, result, 60*15)
	return result

def get_quizzes_by_topic(topic):
	concept_serializer = ConceptSerializer()
	quiz_serializer = QuizSerializer() 

	concepts = topic.get_top_sorted_concepts()
	serialized_concepts = []
	for concept in concepts:
		quiz = concept.quiz_set.all()[0]
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

	

		