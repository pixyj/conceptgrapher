from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError

from uber.load_data import load_all
from topo.models import ConceptQuiz
from .models import ConceptQuizAttempt, convert_anon_attempt_to_user_attempt

class TestAttemptBase(TestCase):
	def setUp(self):
		load_all()
		self.u = User.objects.create(username="hi")
		cq = ConceptQuiz.objects.get(id=1)
		self.attrs = {
			'user': self.u,
			'guess': "x",
			'concept_quiz': cq,
			'result': True
		}


class TestCreateAttempt(TestAttemptBase):

	def test_user_duplicate_attempt(self):
		attrs = dict(self.attrs)
		one = ConceptQuizAttempt.objects.create(**attrs)
		try:
			dup = ConceptQuizAttempt.objects.create(**attrs)
		except IntegrityError as ie:
			return

		#Shouldn't hit here	
		self.assertEqual(False, True)	

	def test_user_proper_attempt(self):
		attrs = dict(self.attrs)
		one = ConceptQuizAttempt.objects.create(**attrs)	
		attrs['guess'] = "y"
		two = ConceptQuizAttempt.objects.create(**attrs)	



	def test_anon_duplicate_attempt(self):
		attrs = dict(self.attrs)
		del attrs['user']
		attrs['session_key'] = "sadfasdfiisdfjasdfasf"
		one = ConceptQuizAttempt.objects.create(**attrs)
		try:
			dup = ConceptQuizAttempt.objects.create(**attrs)
		except IntegrityError:
			return

		self.assertEqual(False, True)


	def test_anon_proper_attemp(self):
		attrs = dict(self.attrs)
		del attrs['user']
		attrs['session_key'] = "a"
		one = ConceptQuizAttempt.objects.create(**attrs)
		attrs['guess'] = "y"
		ConceptQuizAttempt.objects.create(**attrs)


class TestConvertAttempt(TestAttemptBase):

	def test_convert(self):
		attrs = dict(self.attrs)
		del attrs['user']
		attrs['session_key'] = "one"
		one = ConceptQuizAttempt.objects.create(**attrs)
		attrs['guess'] = "y"
		two = ConceptQuizAttempt.objects.create(**attrs)
		
		converted = convert_anon_attempt_to_user_attempt(user=self.u, 
			session_key=attrs['session_key'])
		print converted
		self.assertEqual(converted.count(), 2)
		for c in converted.all():
			self.assertEqual(c.user.id, self.u.id)


		



