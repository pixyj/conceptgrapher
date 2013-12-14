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
	models = ['Auth']
	models += ['Topic', 'Concept', 'ConceptRelationship', 'ConceptResource']
	models += ['Quiz', 'Choice'] 
	#models += ['UserQuizAttempt', 'AnonQuizAttempt']
	

	for m in models:
		fixture_file = "{}.json".format(m)
		load_table(fixture_file)

	#graph.build_graph(ConceptRelationship.objects.all())
		
def clear_all():
	graph.delete_graph()
	base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	db_path = os.path.join(base_dir, "cg/sqlite3.db")
	os.remove(db_path)

def dumpdata():
	uber_dir = os.path.dirname(os.path.realpath(__file__))
	path = "{}/fixtures/all.json".format(uber_dir)
	with open(path, "w") as f:
		management.call_command("dumpdata", stdout=f)
	

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

from django.contrib.auth.models import User
from quiz.models import Quiz, AnonQuizAttempt

def attempts():
	for session_key in ["x", "y"]:
		for j in range(1, 81):
			for x in [1, 2]:
				q = Quiz.objects.get(pk=j)
				a = AnonQuizAttempt.objects.create(quiz=q, guess=str(x), 
					session_key=session_key, result=False)
				if x == 2:
					a.result = True
					a.save()
