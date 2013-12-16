from django.test import TestCase, TransactionTestCase, Client
from django.db import IntegrityError

from networkx import NetworkXUnfeasible
from topo.graph import initialize_graph

from topo.models import Topic, Concept, ConceptRelationship
from quiz.models import Quiz, Choice

import simplejson

class ConceptSlugTestCase(TransactionTestCase):
	"""
	Check if slug updates on edit
	This tests uber's on_save method
	"""

	def setUp(self):
		initialize_graph()
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
		initialize_graph()
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
		initialize_graph()
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

			

