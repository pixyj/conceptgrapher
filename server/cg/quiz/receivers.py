from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver


from .models import AggregateConceptAttempt, UserQuizAttempt, AnonQuizAttempt

@receiver(post_save, sender=UserQuizAttempt)
def add_user_aggregate_attempt(sender, **kwargs):
	if not kwargs['created']:
		return
	create_aggregate_attempt(kwargs['instance'])

@receiver(post_save, sender=AnonQuizAttempt)
def add_anon_aggregate_attempt(sender, **kwargs):
	if not kwargs['created']:
		return
	create_aggregate_attempt(kwargs['instance'])

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



