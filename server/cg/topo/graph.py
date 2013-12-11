import simplejson
import networkx as nx
import redis

REDIS_KEYS = {
	"top_sorted_list": "graph:top_sorted_list",
	"full": "graph:full"
}

def initialize_graph():
	build_graph([])

def delete_graph():
	client = redis.StrictRedis()
	for graph_key, redis_key in REDIS_KEYS.iteritems():
		client.delete(redis_key)


def build_graph(relationships):
	"""
	Initial storing of graph into redis.
	This is a one time only operation to be carried out if the 
	ConceptRelationship table already contains rows
	"""

	dg = nx.DiGraph()
	for relation in relationships:
		dg.add_edge(relation.before.id, relation.after.id)
	dump_graph(dg)
	return dg

def dump_graph(dg):
	"""
	Serialize DiGraph object(dg) into JSON and store in redis
	"""
	
	data = {"edges": dg.edges(), "nodes":dg.nodes()}
	json_data = simplejson.dumps(data)
	client = redis.Redis()
	client.set(REDIS_KEYS["full"], json_data)
	top_sort_and_store(dg)
	return data

def load_graph():
	"""
	JSONed graph in redis to DiGraph object (dg)
	"""

	client = redis.Redis()
	data = client.get(REDIS_KEYS["full"])
	data = simplejson.loads(data)
	dg = nx.DiGraph()
	dg.add_nodes_from(data['nodes'])
	dg.add_edges_from(data['edges'])
	return dg


def top_sort_and_store(dg):
	"""
	Store Topologically sorted concepts  as separate key for fast access
	#Todo. If there's a cycle, an error will be raised. Handle it.
	"""
	
	top_sorted_concepts = nx.topological_sort(dg)
	client = redis.StrictRedis()
	pipeline = client.pipeline()
	pipeline.set(REDIS_KEYS["top_sorted_list"], simplejson.dumps(top_sorted_concepts))
	pipeline.execute()
	return dg

def get_top_sorted_concept_id_list():
	client = redis.StrictRedis()
	json_ids = client.get(REDIS_KEYS['top_sorted_list'])
	return simplejson.loads(json_ids)

def get_top_sorted_concept_id_dict():
	client = redis.StrictRedis()
	json_data = client.get(REDIS_KEYS['top_sorted_list'])
	concept_list = simplejson.loads(json_data)
	concept_dict = {}
	for index, pk in enumerate(concept_list):
		concept_dict[pk] = index
	return concept_dict

def load_modify_dump(fn):
	"""
	Decorator to perform loading and dumping of the graph object
	so that the function can focus on the operations
	"""

	def wrapper(*args, **kwargs):
		dg = load_graph()
		print "Loaded graph"
		result = fn(dg, *args, **kwargs)
		print "Modified graph"
		data = dump_graph(dg)
		print "Graph data: ", data
		return result
		
	return wrapper

@load_modify_dump
def add_concept(dg, concept):
	assert(concept.id !=  None)
	dg.add_node(concept.id)

@load_modify_dump
def remove_concept(dg, concept):
	"""Also removes concept relations"""
	dg.remove_node(concept.id)


@load_modify_dump
def add_concept_relationship(dg, before, after):
	dg.add_edge(before.id, after.id)

@load_modify_dump	
def remove_concept_relationship(dg, before, after):
	dg.remove_edge(before.id, after.id)

