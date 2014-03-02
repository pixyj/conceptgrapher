from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from topo import graph
from topo.models import Topic, Concept

from .models import Quiz, QuizAttempt
from .diagnose import get_serialized_quizzes_by_topic

import simplejson


def json_decode(x):
    return simplejson.loads(x)



class QuizBaseTest(TestCase):
    fixtures = [
        'uber/fixtures/all.json'
    ]

    def _pre_setup(self):
        graph.initialize_graph()
        super(QuizBaseTest, self)._pre_setup()

class QuizByTopicTest(QuizBaseTest):

    def test_get_quizzes_by_topic(self):
        t = Topic.objects.get(id=1)
        concept_count = t.concept_set.all().count()
        quizzes = get_serialized_quizzes_by_topic(t)
        quizzes = json_decode(quizzes)
        
        self.assertEqual(concept_count, len(quizzes))

        top_sorted_concepts = t.get_top_sorted_concepts()
        self.assertEqual(concept_count , len(top_sorted_concepts))

    
        
class QuizCreationTest(QuizBaseTest):

    def test_create(self):
        quiz = Quiz.objects.get(id=1)
        user = User.objects.create(username="one", password="one")

        x = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user=user, result=False, guess="what")
        self.assertEqual(x.attempt_number, 1)
        y = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user=user, result=False, guess="yep")
        self.assertEqual(y.attempt_number, 2)

        duplicate = False
        try:
            z = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user=user, result=False, guess="what")
        except IntegrityError:
            duplicate = True

        self.assertEqual(duplicate, True)

