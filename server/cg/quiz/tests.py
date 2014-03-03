from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from topo import graph
from topo.models import Topic, Concept

from .models import Quiz, QuizAttempt
from .diagnose import get_serialized_quizzes_by_topic

from uber.tests import UberTest
from uber.tests import UserClient

import simplejson


def json_decode(x):
    return simplejson.loads(x)





class QuizByTopicTest(UberTest):

    def test_get_quizzes_by_topic(self):
        t = Topic.objects.get(id=1)
        concept_count = t.concept_set.all().count()
        quizzes = get_serialized_quizzes_by_topic(t)
        quizzes = json_decode(quizzes)
        
        self.assertEqual(concept_count, len(quizzes))

        top_sorted_concepts = t.get_top_sorted_concepts()
        self.assertEqual(concept_count , len(top_sorted_concepts))

    
        
class QuizAttemptCreationTest(UberTest):

    def test_user_create(self):
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


        def test_anon_create(self):
            quiz = Quiz.objects.get(id=1)
            user_key = "34ssdfafdadfe"

            x = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user_key=user_key, result=False, guess="what")
            self.assertEqual(x.attempt_number, 1)
            y = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user_key=user_key, result=True, guess="yep")
            self.assertEqual(y.attempt_number, 2)

            duplicate = False
            try:
                z = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user_key=user_key, result=True, guess="yep")
            except IntegrityError:
                duplicate = True

            self.assertEqual(duplicate, True)


from . import stats

class QuizStatsTest(UberTest):

    def test_quiz_and_concept_count_with_one_quiz(self):
        quiz = Quiz.objects.get(id=1)
        user = User.objects.create(username="one", password="one")
        anon_user_key = "asdf"

        x = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user=user, result=True, guess="what")
        self.assertEqual(x.attempt_number, 1)
        y = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user_key=anon_user_key, result=False, guess="yep")
        self.assertEqual(y.attempt_number, 1)

        #import ipdb;ipdb.set_trace()
        named_counts = stats.get_quiz_counts(quiz)
        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)
        
        #concept = 
        quiz = Quiz.objects.get(id=2)

        x = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user=user, result=True, guess="what")
        self.assertEqual(x.attempt_number, 1)
        y = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, user_key=anon_user_key, result=False, guess="yep")
        self.assertEqual(y.attempt_number, 1)
        quiz = Quiz.objects.get(id=2)

        

        named_counts = stats.get_quiz_counts(quiz)
        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)
        #import ipdb;ipdb.set_trace()
        named_counts = stats.get_concept_counts(quiz.concept)
        
        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)


class QuizConceptStatsTest(UberTest):

    def test_concept_count_with_multiple_quizzes(self):
        concept = Concept.objects.get(topic_id=1, name="strings")
        quizzes = concept.quiz_set.all()

        user = User.objects.create(username="one", password="one")
        anon_user_key = "asdf"

        for index, quiz in enumerate(quizzes):
            result_user = index % 2 == 0
            result_anon = not result_user

            x = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, 
                user=user, result=result_user, guess="what")
            self.assertEqual(x.attempt_number, 1)
            y = QuizAttempt.objects.create_quiz_attempt(quiz=quiz, 
                user_key=anon_user_key, result=result_anon, guess="yep")
            self.assertEqual(y.attempt_number, 1)
            


        quiz_count = quizzes.count()

        named_counts = stats.get_concept_counts(concept)
        self.assertEqual(named_counts.correct, quiz_count)
        self.assertEqual(named_counts.wrong, quiz_count)



from django.test import Client
import simplejson

class QuizUserAttemptIntegrationTest(UberTest):
    
    def test_user_attempt(self):
        print "Testing test_user_attempt"
        user = User.objects.create(username="one", password="two")
        c = UserClient()
        c.login_user(user)
        quiz = Quiz.objects.get(id=1)

        payload = {"result":False,"guess":"//","quizId":quiz.id,"created":"2014-03-03T16:49:32.415Z"}
        json_payload = simplejson.dumps(payload)
        response = c.post("/api/quiz/attempt/create/", json_payload, content_type="application/json")

        payload['guess'] = "correct_guess"
        payload['result'] = True
        json_payload = simplejson.dumps(payload)
        response = c.post("/api/quiz/attempt/create/", json_payload, content_type="application/json")



        attempts = QuizAttempt.objects.filter(user=user)
        #import ipdb;ipdb.set_trace()
        self.assertEqual(attempts.count(), 2)

        concept = quiz.concept
        named_counts = stats.get_concept_counts(concept)

        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)

        named_quiz_counts = stats.get_quiz_counts(quiz)
        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)

        response = c.post("/api/quiz/attempt/create/", json_payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)



class QuizAnonAttemptIntegrationTest(UberTest):

    def test_anon_attempt(self):
        c = Client()
        quiz = Quiz.objects.get(id=1)

        payload = {"result":False,"guess":"//","quizId":quiz.id,"created":"2014-03-03T16:49:32.415Z"}
        json_payload = simplejson.dumps(payload)
        response = c.post("/api/quiz/attempt/create/", json_payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        payload['guess'] = "correct_guess"
        payload['result'] = True
        json_payload = simplejson.dumps(payload)
        response = c.post("/api/quiz/attempt/create/", json_payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        response = c.post("/api/quiz/attempt/create/", json_payload, content_type="application/json")
        self.assertEqual(response.status_code, 400)


        user_key = c.session.session_key
        assert(user_key)

        attempts = QuizAttempt.objects.filter(user_key=user_key)
        self.assertEqual(attempts.count(), 2)

        concept = quiz.concept
        named_counts = stats.get_concept_counts(concept)

        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)

        named_quiz_counts = stats.get_quiz_counts(quiz)
        self.assertEqual(named_counts.correct, 1)
        self.assertEqual(named_counts.wrong, 1)


