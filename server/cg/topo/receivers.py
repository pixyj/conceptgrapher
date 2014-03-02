"""
Concepts map to nodes
ConceptRelationships map to relationships
"""
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms import model_to_dict

from .models import Concept, ConceptRelationship
import graph


@receiver(post_save, sender=Concept)
def add_node(sender, **kwargs):
	if not kwargs['created']:
		return
		
	instance = kwargs['instance']
	graph.add_concept(instance)

@receiver(post_delete, sender=Concept)
def remove_node(sender, **kwargs):
	instance = kwargs['instance']
	graph.remove_concept(instance)


@receiver(post_save, sender=ConceptRelationship)
def add_relationship(sender, **kwargs):
	instance = kwargs['instance']
	print "Adding relationship", instance
	graph.add_concept_relationship(instance.before, instance.after)


@receiver(pre_save, sender=ConceptRelationship)
def remove_old_relationship(sender, **kwargs):
	"""
	If a ConceptRelationship instance is updated, the older relationship must be removed
	from the graph database. On post_save, the new relationship is added
	"""
	instance = kwargs['instance']
	try:
		old = ConceptRelationship.objects.get(pk=instance.id)
	except ConceptRelationship.DoesNotExist:
		return

	graph.remove_concept_relationship(old.before, old.after)



@receiver(post_delete, sender=ConceptRelationship)
def remove_relationship(sender, **kwargs):
	instance = kwargs['instance']
	graph.remove_concept_relationship(instance.before, instance.after)


