import simplejson
import requests
from redis_cache import get_redis_connection

API_URL = "http://api.stackexchange.com/2.2/questions?order=desc&sort=votes&tagged={tags}&site=stackoverflow"
CACHE_KEY = "stack:{topic}:{concept}"

def cache_questions(concepts):

    client = get_redis_connection()
    for concept in concepts:
        cache_concept_questions(concept, client)

import ipdb

def cache_concept_questions(concept, client):
    tags = "{};{}".format(concept.topic.name, concept.name)
    url = API_URL.format(tags=tags)
    print "Request: ", url
    response = requests.get(url)
    content = simplejson.loads(response.content)
    items = content.get("items")
    print "items: ", items
    cache_key = CACHE_KEY.format(topic=concept.topic.name, concept=concept.name)
    client.set(cache_key, items)









