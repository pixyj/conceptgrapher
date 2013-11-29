from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import ConceptRelationship

from .graph import validate_concept_relationship_acyclic

def add_relationship(sender, **kwargs):
	instance = kwargs['instance']
	validate_concept_relationship_acyclic(instance)
	#print instance


pre_save.connect(add_relationship, sender=ConceptRelationship)

