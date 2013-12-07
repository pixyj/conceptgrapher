from django.db import models
from django.contrib.auth.models import User

from uber.models import TimestampedModel
from topo.models import Concept

from .serializers import QuizSerializer, QuizAttemptSerializer

class Quiz(TimestampedModel):
	concept = models.ForeignKey(Concept)
	question = models.TextField(unique=True)
	answer = models.CharField(max_length=50, blank=True)

	def to_dict(self):
		return QuizSerializer().to_dict(self)

	def to_dict_with_user_attempts(self, user):
		attrs = self.to_dict_with_filter(UserQuizAttempt, user=user)
		return attrs

	def to_dict_with_session_attempts(self, session_key):
		attrs = self.to_dict()
		attrs['attempts'] = []
		return attrs

	def to_dict_with_filter(self, klass, **kwargs):
		attrs = self.to_dict()
		attempts = klass.objects.filter(**kwargs).filter(quiz=self).all()
		attempts = [attempt.to_dict() for attempt in attempts]
		attrs['attempts'] = attempts
		for attempt in attempts:
			if attempt['result']:
				attrs['answered'] = True
				break
		return attrs


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


class BaseQuizAttempt(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	quiz = models.ForeignKey(Quiz)
	guess = models.TextField()
	result = models.BooleanField()	
	
	def to_dict(self):
		return QuizAttemptSerializer().to_dict(self)

	class Meta:
		abstract = True

class UserQuizAttempt(BaseQuizAttempt):
	user = models.ForeignKey(User)	

	def __unicode__(self):
		return "{} attempted {} - {}".format(self.user, self.quiz, self.result)

	class Meta:
		unique_together = (
			("quiz", "user", "guess"), #For logged in users
		)

class AnonQuizAttempt(BaseQuizAttempt):
	session_key = models.CharField(max_length=40)

	def __unicode__(self):
		return "{} attempted {} - {}".format(self.session_key, self.quiz, self.result)
		
	class Meta:
		unique_together = (
			("quiz", "session_key", "guess"), #For logged in users
		)
