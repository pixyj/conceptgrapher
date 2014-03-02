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

	def user_attempts_to_dict(self, user_key):
		user_key = str(user_key)
		attrs = self.to_dict()
		attempts = QuizAttempt.objects.filter(user_key=user_key).filter(quiz=self).all()
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



class QuizAttemptManager(models.Manager):
	def create_quiz_attempt(self, **kwargs):
		user = kwargs.get("user")
		if user:
			user_key = str(user.id)
			kwargs['user_key'] = user_key
		else:
			assert(kwargs.get("user_key"))
        
        #How to follow PEP standards in below line?
		previous_attempts = self.filter(user_key=user_key, quiz=kwargs.get("quiz")).order_by("-attempt_number")[0:1]
		if previous_attempts:
			previous_attempt = previous_attempts[0]
			kwargs['attempt_number'] = previous_attempt.attempt_number + 1

		return self.create(**kwargs)

	def get_unique_user_key(self, args):
		if args.get("user"):
			return str(args['user'].id)
		elif args.get("session_key"):
			assert(args.get("session_key"))
			return args['session_key']

		assert(False)
		


USER_KEY_MAX_LENGTH = 40 #Equal to session_key max length

class QuizAttempt(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	quiz = models.ForeignKey(Quiz)
	guess = models.TextField()
	result = models.BooleanField()
	attempt_number = models.IntegerField(default=1)

	user = models.ForeignKey(User, null=True)

	#Used as proxy for either user or session_key so that data constraints are maintained
	#for both anon and logged in users. 
	#http://stackoverflow.com/questions/191421/how-to-create-a-unique-index-on-a-null-column
	
	user_key = models.CharField(max_length=USER_KEY_MAX_LENGTH)	
	
	objects = QuizAttemptManager()
	
	def to_dict(self):
		return QuizAttemptSerializer().to_dict(self)

	def __unicode__(self):
		return "{} attempted {} - {}".format(self.user or self.user_key, self.quiz, self.result)

	class Meta:
		unique_together = (
			("quiz", "user_key", "guess"),
		)



class AggregateConceptAttempt(models.Model):
	concept = models.ForeignKey(Concept)
	user_key = models.CharField(max_length=USER_KEY_MAX_LENGTH)
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



