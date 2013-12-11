"""
Concepts map to nodes
ConceptRelationships map to relationships
"""
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import UserConceptProgress, AnonConceptProgress
