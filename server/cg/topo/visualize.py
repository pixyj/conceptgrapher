from . import graph
from models import Concept
import ipdb

def to_d3():
    dg = graph.load_graph()

    graph_dict = {"nodes": [], "links": []}
    nodes = [];
    links = [];
    concept_dict = {}
    for index, pk in enumerate(dg.nodes()):
        concept = Concept.objects.get(pk=pk)
        concept_dict[pk] = index
        node = {"name": concept.name, "group": 1}
        nodes.append(node)


    for before_pk, after_pk in dg.edges():
        try:
            link = {"source": concept_dict[before_pk], "target": concept_dict[after_pk], "value": 5}
        except KeyError:
            ipdb.set_trace()
        links.append(link)

    return {"nodes": nodes, "links": links}

import simplejson

def to_d3_json():
    return simplejson.dumps(to_d3())


from uber.cache import memoized
from topo.models import ConceptRelationship, Concept
import ipdb

@memoized
def depth(concept_id):
    if concept_id == 1:
        return 0

    #ipdb.set_trace()
    print "Calculating prereq for ", concept_id, Concept.objects.get(pk=concept_id)    
    rels = ConceptRelationship.objects.filter(after_id=concept_id)
    print "prereqs for ", concept_id, rels

    prereq_ids = [rel.before.id for rel in rels]
    print "prereq_ids: ", prereq_ids
    depths = [depth(prereq_id) for prereq_id in prereq_ids]
    
    print "depths", depths
    return max(depths) + 1


from collections import defaultdict

def all_concept_depths():
    depths = defaultdict(list)
    for concept in Concept.objects.all():
        d = depth(concept.id)
        depths[d].append(concept)

    return depths



    




    




