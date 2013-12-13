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
		attrs = self.to_dict_with_filter(AnonQuizAttempt, session_key=session_key)
		return attrs

	def to_dict_with_filter(self, klass, **kwargs):
		attrs = self.to_dict()
		attempts = klass.objects.filter(**kwargs).filter(quiz=self).all()
		attempts = [attempt.to_dict() for attempt in attempts]
		attrs['attempts'] = attempts
		attrs['answered'] = False #Initialization. Will be overriden if answered
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


"""
Todo: Extend django.contrib.auth.User
"""
def get_unique_user_key(**kwargs):
	if kwargs.get("user"):
		return str(kwargs['user'].id)
	elif kwargs.get("session_key"):
		return kwargs['session_key'][0:5]

	assert(False)


class BaseQuizAttempt(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	quiz = models.ForeignKey(Quiz)
	guess = models.TextField()
	result = models.BooleanField()	
	
	def get_unique_user_key(self):
		raise Exception("Subclass must implement this method")

	def to_dict(self):
		return QuizAttemptSerializer().to_dict(self)


	class Meta:
		abstract = True

class UserQuizAttempt(BaseQuizAttempt):
	user = models.ForeignKey(User)	
	
	def get_unique_user_key(self):
		return get_unique_user_key(user=self.user)

	def __unicode__(self):
		return "{} attempted {} - {}".format(self.user, self.quiz, self.result)

	class Meta:
		unique_together = (
			("quiz", "user", "guess"), #For logged in users
		)

class AnonQuizAttempt(BaseQuizAttempt):
	session_key = models.CharField(max_length=40)

	def get_unique_user_key(self):
		return get_unique_user_key(session_key=self.session_key)

	def __unicode__(self):
		return "{} attempted {} - {}".format(self.session_key, self.quiz, self.result)
		
	class Meta:
		unique_together = (
			("quiz", "session_key", "guess"), #For logged in users
		)


class AggregateConceptAttempt(models.Model):
	concept = models.ForeignKey(Concept)
	user_key = models.CharField(max_length=5)
	correct = models.IntegerField(default=0)
	wrong = models.IntegerField(default=0)

	def __unicode__(self):
		return "{}'s attempts in {}: correct:{} wrong:{}".format(
			self.user_key, self.concept, self.correct, self.wrong)


def get_topic_stats_by_user(topic, user_key):
	concepts = topic.get_top_sorted_concepts()
	stats = AggregateConceptAttempt.objects.filter(user_key=user_key).filter(
		concept__in=concepts)
	return (concepts, stats)


#signals
from . import receivers

