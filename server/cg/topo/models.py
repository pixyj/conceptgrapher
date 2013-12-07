from django.db import models
from uber.models import SluggedTimeStampedModel, TimestampedModel


class Topic(SluggedTimeStampedModel):
	name = models.CharField(max_length=128, unique=True)

	def to_be_slugged(self):
		return self.name	

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






