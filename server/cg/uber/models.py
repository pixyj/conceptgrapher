from django.db import models

from django.template.defaultfilters import slugify


class TimestampedModel(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class SlugFieldNotFoundError(Exception):
	pass

class SluggedTimeStampedModel(TimestampedModel):
	"""
	Abstract Class to add a slugify method.
	Declare a to_be_slugged method in the model class and you're done 
	"""
	slug = models.SlugField()

	def save(self, *args, **kwargs):
		try:
			attr = getattr(self, "to_be_slugged")
		except AttributeError:
			raise SlugFieldNotFoundError

		to_be_slugged = self.to_be_slugged()
		self.slug = slugify(to_be_slugged)
		super(SluggedTimeStampedModel, self).save(*args, **kwargs)

	class Meta:
		abstract = True



