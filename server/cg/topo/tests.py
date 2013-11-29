from django.test import TestCase
from django.db import IntegrityError

from topo.models import Topic, Concept, ConceptRelationship

class ConceptSlugTestCase(TestCase):
	def setUp(self):
		topic = Topic.objects.create(name="topic")
		Concept.objects.create(topic=topic, name="Concept One")

	def test_slug(self):
		c = Concept.objects.get(name="Concept One")
		self.assertEqual(c.slug, "concept-one")
		c.name = "Concept Two"
		c.save()
		#Check if slug updates on edit
		#This tests uber's on_save method
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


