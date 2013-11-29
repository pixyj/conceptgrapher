from django.test import TestCase, TransactionTestCase, Client
from django.db import IntegrityError

from networkx import NetworkXUnfeasible

from topo.models import Topic, Concept, ConceptRelationship, ConceptQuiz
from quiz.models import Quiz, Choice

import simplejson

class ConceptSlugTestCase(TransactionTestCase):
	"""
	Check if slug updates on edit
	This tests uber's on_save method
	"""

	def setUp(self):
		topic = Topic.objects.create(name="topic")
		Concept.objects.create(topic=topic, name="Concept One")

	def test_slug(self):
		c = Concept.objects.get(name="Concept One")
		self.assertEqual(c.slug, "concept-one")
		c.name = "Concept Two"
		c.save()

		self.assertEqual(c.slug, "concept-two") 


class ModelIntegrityTestCase(TestCase):
	"""
	Ensure that meta unique_together stuff is right
	"""

	def setUp(self):
		self.topic = Topic.objects.create(name="1")
		self.c1 = Concept.objects.create(topic=self.topic, name="2")
		self.c2 = Concept.objects.create(topic=self.topic, name="3")
		ConceptRelationship.objects.create(before = self.c1, after = self.c2)


	def test_topic_concept_unique(self):
		try:
			Concept.objects.create(topic=self.topic, name="2")
		except IntegrityError:
			return
		
		raise IntegrityError


	def test_concept_rel_unique(self):
		try:
			ConceptRelationship.objects.create(before=self.c1, after=self.c2)
		except IntegrityError:
			return

		raise IntegrityError


class TopologyTest(TransactionTestCase):
	"""
	Ensures if Error is raised when the concept graph becomes cyclic.
	"""
	def setUp(self):
		self.t = Topic.objects.create(name="one")
		self.c1 = Concept.objects.create(topic=self.t, name="1")
		self.c2 = Concept.objects.create(topic=self.t, name="2")
		r = ConceptRelationship.objects.create(before=self.c1, after=self.c2)
		

	def test_immediate_top_error(self):
		try:
			r2 = ConceptRelationship.objects.create(before=self.c2, after=self.c1)
		except NetworkXUnfeasible:
			return

		print "NetworkXUnfeasible must have been raised"	
		raise NetworkXUnfeasible	

	def create_relationship_from_ids(self, before_id, after_id):
		before = Concept.objects.get(name=str(before_id))
		after = Concept.objects.get(name=str(after_id))
		ConceptRelationship.objects.create(before=before, after=after)
		
	def test_generic_cyclic_error(self):
		concepts = [str(i) for i in xrange(10, 20)]
		for c in concepts:
			Concept.objects.create(topic=self.t, name=c)
		initial_relations = [(10, 11), (11, 12), (12, 13)]
		for before_id, after_id in initial_relations:
			self.create_relationship_from_ids(before_id, after_id)

		try:
			self.create_relationship_from_ids(13, 10)
		except NetworkXUnfeasible:
			return

		raise NetworkXUnfeasible

			

class ConceptByTopicTest(TestCase):
	def setUp(self):
		self.t = Topic.objects.create(name="One Two Three")
		self.CONCEPT_COUNT = 10
		for i in xrange(self.CONCEPT_COUNT):
			Concept.objects.create(topic=self.t, name=str(i))


	def test_json_response(self):
		c = Client()
		response = c.get("/api/topo/topic/one-two-three/concepts/")
		
		self.assertEqual(response.status_code, 200)
		concepts = simplejson.loads(response.content)
		print concepts
		self.assertEqual(len(concepts), self.CONCEPT_COUNT)


	def test_404(self):
		c = Client()
		response = c.get("/api/topo/topic/asdfasdf/concepts/")
		self.assertEqual(response.status_code, 404)


class QuizzesByConceptTest(TestCase):
	def setUp(self):
		self.QUIZ_COUNT = 10
		self.CHOICE_COUNT = 4
		self.topic = Topic.objects.create(name="1")
		self.c1 = Concept.objects.create(topic=self.topic, name="2")

		for i in xrange(self.QUIZ_COUNT):
			q = Quiz.objects.create(question="question:{}".format(i))
			ConceptQuiz.objects.create(concept=self.c1, quiz=q)
			for i in xrange(self.CHOICE_COUNT):
				Choice.objects.create(quiz=q, text="yep {}".format(i), is_correct=True)



	def test_quiz_by_concept(self):
		c = Client()
		response = c.get("/api/topo/concept/1/quizzes/")
		self.assertEqual(response.status_code, 200)
		quizzes = simplejson.loads(response.content)
		self.assertEqual(len(quizzes), self.QUIZ_COUNT)
		for q in quizzes:
			self.assertEqual(len(q['choices']), self.CHOICE_COUNT)


	def test_404(self):
		response = Client().get("/api/topo/concept/10000/quizzes/")
		self.assertEqual(response.status_code, 404)

