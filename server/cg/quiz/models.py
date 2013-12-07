from django.db import models
from django.contrib.auth.models import User

from uber.models import TimestampedModel
from topo.models import Concept

from .serializers import QuizSerializer

class Quiz(TimestampedModel):
	concept = models.ForeignKey(Concept)
	question = models.TextField(unique=True)
	answer = models.CharField(max_length=50, blank=True)

	def to_dict(self):
		return QuizSerializer().to_dict()

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



class QuizAttempt(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	quiz = models.ForeignKey(Quiz)
	user = models.ForeignKey(User)
	guess = models.TextField()
	result = models.BooleanField()	
	
	def __unicode__(self):
		return "{} attempted {} - {}".format(self.user, self.quiz, self.result)

	class Meta:
		unique_together = (
			("quiz", "user", "guess"), #For logged in users
		)


