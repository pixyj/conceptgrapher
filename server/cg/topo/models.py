from django.db import models
from uber.models import SluggedTimeStampedModel, TimestampedModel
from uber.cache import cache_key_for

from .graph import get_top_sorted_concept_id_dict

class Topic(SluggedTimeStampedModel):
	name = models.CharField(max_length=128, unique=True)

	def to_be_slugged(self):
		return self.name	
	
	def get_top_sorted_concepts(self):
		concepts = [concept for concept in self.concept_set.all()]
		top_sorted_concepts = get_top_sorted_concept_id_dict()

		def compare(one, two):
			one = one.id
			two = two.id
			if top_sorted_concepts[one] < top_sorted_concepts[two]:
				return -1
			else:
				return 1
			
		concepts.sort(cmp=compare)
		return concepts


	def __unicode__(self):
		return self.name




class Concept(SluggedTimeStampedModel):
	topic = models.ForeignKey(Topic)
	name = models.CharField(max_length=128)

	def to_be_slugged(self):
		return self.name

	def __unicode__(self):
		return "{}: {}".format(self.topic, self.name)


	class Meta:
		unique_together = ("topic", "name")	


class ConceptResource(models.Model):
	concept = models.ForeignKey(Concept)
	url = models.URLField(max_length=256)

	def __unicode__(self):
		return self.url

	class Meta:
		unique_together = ("concept", "url")


class ConceptRelationship(TimestampedModel):
	before = models.ForeignKey(Concept, related_name="after_set")
	after = models.ForeignKey(Concept, related_name="before_set")

	class Meta:
		unique_together = ("before", "after")

	def __unicode__(self):
		return "{} --> {}".format(self.before, self.after)


#For signals
import receivers



