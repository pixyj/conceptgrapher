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
	uber_dir = os.path.dirname(os.path.realpath(__file__))
	fixture_path = "{}/fixtures/{}".format(uber_dir, "all.json")
	management.call_command("loaddata", fixture_path)
		
def clear_all():
	graph.delete_graph()
	base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	db_path = os.path.join(base_dir, "cg/sqlite3.db")
	os.remove(db_path)

def dumpdata():
	uber_dir = os.path.dirname(os.path.realpath(__file__))
	path = "{}/fixtures/all.json".format(uber_dir)
	with open(path, "w") as f:
		management.call_command("dumpdata", exclude=['quiz.UserQuizAttempt', 
			'quiz.AnonQuizAttempt', 'quiz.AggregateConceptAttempt'], stdout=f)
	

import simplejson
def ok():
	uber_dir = os.path.dirname(os.path.realpath(__file__))
	def fixture_to_json(model):
		path = "{}/fixtures/{}.json".format(uber_dir, model)
		with open(path, "r") as f:
			s = f.read()
			ok = simplejson.loads(s)
		return ok

	cqs = fixture_to_json("ConceptQuiz")
	quizzes = fixture_to_json("Quiz")
	quiz_dict = {}
	for q in quizzes:
		quiz_dict[q['pk']] = q
	
	for cq in cqs:
		q_id = cq['fields']['quiz']
		q = quiz_dict[q_id]
		q['fields']['concept'] = cq['fields']['concept']

	q2s = simplejson.dumps(quizzes)	
	q2_path = "{}/fixtures/{}.json".format(uber_dir, "Quiz2")
	with open(q2_path, "w") as f:
		f.write(q2s)

	return quizzes
