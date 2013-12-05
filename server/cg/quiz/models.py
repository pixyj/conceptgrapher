from django.db import models


from uber.models import TimestampedModel

class Quiz(TimestampedModel):
	question = models.TextField(unique=True)
	answer = models.CharField(max_length=50, blank=True)

	def __unicode__(self):
		return self.question


class Choice(models.Model):
	quiz = models.ForeignKey(Quiz)
	text = models.TextField()
	is_correct = models.BooleanField(default=False)

	def __unicode__(self):
		return "{} - {}".format(self.quiz, self.text)


	class Meta:
		unique_together = ("quiz", "text")



