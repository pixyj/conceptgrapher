import os
from django.core import serializers, management
from topo import graph
from topo.models import ConceptRelationship


def load_table(fixture_file):
	uber_dir = os.path.dirname(os.path.realpath(__file__))
	fixture_path = "{}/fixtures/{}".format(uber_dir, fixture_file)

	management.call_command("loaddata", fixture_path)



def load_all():
	management.call_command("syncdb")
	graph.initialize_graph()	
	models = ['Topic', 'Concept', 'ConceptQuiz', 'ConceptRelationship', 'ConceptResource']
	models += ['Quiz', 'Choice']

	for m in models:
		fixture_file = "{}.json".format(m)
		load_table(fixture_file)

	#graph.build_graph(ConceptRelationship.objects.all())
		
def clear_all():
	graph.delete_graph()
	base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	db_path = os.path.join(base_dir, "cg/sqlite3.db")
	os.remove(db_path)






