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
