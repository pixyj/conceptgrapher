from django.db import models
from django.contrib.auth.models import User

from topo.models import ConceptQuiz

class ConceptQuizAttempt(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	concept_quiz = models.ForeignKey(ConceptQuiz)
	user = models.ForeignKey(User, blank=True, null=True)
	session_key = models.CharField(max_length=40)
	guess = models.TextField()
	result = models.BooleanField()
	
	def __unicode__(self):
		return "{} attempted {} - {}".format(self.user, self.concept_quiz, self.result)

	class Meta:
		unique_together = (
			("concept_quiz", "user", "guess"), #For logged in users
			("concept_quiz", "session_key", "guess") #For anon users
		)


def convert_anon_attempt_to_user_attempt(user, session_key):
	attempts = ConceptQuizAttempt.objects.filter(session_key=session_key).all()
	for attempt in attempts:
		attempt.user = user
		attempt.session_key = ""
		attempt.save()

	return ConceptQuizAttempt.objects.filter(user=user)








