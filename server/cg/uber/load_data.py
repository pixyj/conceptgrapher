import os
from django.core import serializers, management

def load_table(fixture_file):
	uber_dir = os.path.dirname(os.path.realpath(__file__))
	fixture_path = "{}/fixtures/{}".format(uber_dir, fixture_file)

	management.call_command("loaddata", fixture_path)



def load_all():
	models = ['Topic', 'Concept', 'ConceptQuiz', 'ConceptRelationship', 'ConceptResource']
	models += ['Quiz', 'Choice']

	for m in models:
		fixture_file = "{}.json".format(m)
		load_table(fixture_file)





