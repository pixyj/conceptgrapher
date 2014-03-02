from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import AggregateConceptAttempt
from .models import Quiz
from .diagnose import clear_quizzes_by_topic_cache

"""
@receiver(post_save, sender=UserQuizAttempt)
def add_user_aggregate_attempt(sender, **kwargs):
	return on_attempt_created(sender, **kwargs)


@receiver(post_save, sender=AnonQuizAttempt)
def add_anon_aggregate_attempt(sender, **kwargs):
	return on_attempt_created(sender, **kwargs)


def on_attempt_created(sender, **kwargs):
	if not kwargs['created']:
		return
	instance = kwargs['instance']
	create_aggregate_attempt(instance)

"""

def create_aggregate_attempt(attempt):
	user_key = attempt.get_unique_user_key();
	aggregate, was_created = AggregateConceptAttempt.objects.get_or_create(
		user_key=user_key, concept=attempt.quiz.concept)
	if attempt.result:
		aggregate.correct += 1
	else:
		aggregate.wrong += 1
	aggregate.save()
	print "Aggregate saved: ", aggregate
	return aggregate

@receiver(post_save, sender=Quiz)
def clear_cache(sender, **kwargs):
	topic = kwargs['instance'].concept.topic
	clear_quizzes_by_topic_cache(topic=topic)



