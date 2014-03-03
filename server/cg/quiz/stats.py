from redis_cache import get_redis_connection

from collections import namedtuple

Counts = namedtuple("Counts", "correct wrong")

QUIZ_CORRECT_COUNT_FORMAT = "quiz:{id}:correct"
QUIZ_WRONG_COUNT_FORMAT = "quiz:{id}:wrong"

CONCEPT_CORRECT_COUNT_FORMAT = "concept:{id}:correct"
CONCEPT_WRONG_COUNT_FORMAT = "concept:{id}:wrong"



def update_quiz_and_concept_attempt_counts(attempt):
    keys = []
    quiz_id = attempt.quiz.id
    concept_id = attempt.quiz.concept.id

    #import ipdb; ipdb.set_trace()
    if attempt.result:
        keys = [QUIZ_CORRECT_COUNT_FORMAT.format(id=quiz_id), 
                CONCEPT_CORRECT_COUNT_FORMAT.format(id=concept_id)]
    else:
        keys = [QUIZ_WRONG_COUNT_FORMAT.format(id=quiz_id), 
                CONCEPT_WRONG_COUNT_FORMAT.format(id=concept_id)]

    r = get_redis_connection()
    pipeline = r.pipeline()

    for key in keys:
        pipeline.incr(key)
    

    result = pipeline.execute()
    return result


def get_counts(keys):
    r = get_redis_connection()
    pipeline = r.pipeline()

    for key in keys:
        pipeline.get(key)

    counts = pipeline.execute()

    #Hopefully, int(count) will overflow
    counts = [int(count) if count else 0 for count in counts]
    assert(len(counts) == 2)
    named_counts = Counts(correct=counts[0], wrong=counts[1])
    return named_counts


#Possible to make this more DRY. But it might decrease readability

def get_quiz_counts(quiz):
    keys = [QUIZ_CORRECT_COUNT_FORMAT.format(id=quiz.id), 
            QUIZ_WRONG_COUNT_FORMAT.format(id=quiz.id)]

    return get_counts(keys)


def get_concept_counts(concept):
    keys = [CONCEPT_CORRECT_COUNT_FORMAT.format(id=concept.id), 
            CONCEPT_WRONG_COUNT_FORMAT.format(id=concept.id)]

    return get_counts(keys)



