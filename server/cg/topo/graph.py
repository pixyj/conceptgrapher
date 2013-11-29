import networkx as nx

from .models import ConceptRelationship

def validate_concept_relationship_acyclic(instance):
	
	di_graph = nx.DiGraph()
	rels = ConceptRelationship.objects.all()
	for rel in rels:
		di_graph.add_edge(rel.before.id, rel.after.id)

	di_graph.add_edge(instance.before.id, instance.after.id)
	nx.topological_sort(di_graph)


