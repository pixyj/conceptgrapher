from django.test import TestCase, Client
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


	def test_create_with_concept_quiz_id(self):
		"""
		Nothing special. Used during dev to check syntax/attrs
		"""
		attrs = dict(self.attrs)
		del attrs['user']
		del attrs['concept_quiz']
		attrs['concept_quiz_id'] = 1

		ConceptQuizAttempt.objects.create(**attrs)


import simplejson
#monkey patching self._encode_data in django/test/client
#becaue simplejson.dumps doesn't enclose keys in double quotes 
def force_bytes_patch(data, encoding):
	return simplejson.dumps(data)

class AttemptCreateApiTest(TestCase):
	def setUp(self):
		load_all()
		c = Client()
		global force_bytes_patch
		c._encode_data = force_bytes_patch
		self.c = c

	def tearDown(self):
		print 'done'

	def test_anon_create(self):
		c = self.c
		url = "/api/quant/attempt/create"

		response = c.get(url)
		self.assertEqual(response.status_code, 403)

		response = c.post(url, data={"xasdfasdf":1}, content_type="text")
		self.assertEqual(response.status_code, 400)

		attrs = {
			'concept_quiz_id': 1,
			'guess': "22",
			'result': False,
		}

		response = c.post(url, data=attrs, content_type="text")
		self.assertEqual(response.status_code, 200)

		response = c.post(url, data=attrs, content_type="text")
		print response
		self.assertEqual(response.status_code, 400)


	# TODO. Test Case for logged in user 
	# def test_user_create(self):
	# 	c = self.c
	# 	url = "/api/quant/attempt/create"
	# 	u = User.objects.create(username="hi", password="hi", is_staff=True)
	# 	ok = c.post('/admin/', {'username': "pramodliv1asdf", 'password': "a"})
	# 	import pdb
	# 	pdb.set_trace()
	# 	attrs = {
	# 		'concept_quiz_id': 1,
	# 		'guess': "22",
	# 		'result': False,
	# 	}

	# 	response = c.post(url, data=attrs, content_type="text")
	# 	self.assertEqual(response.status_code, 200)

	# 	response = c.post(url, data=attrs, content_type="text")
	# 	print response
	# 	self.assertEqual(response.status_code, 400)



		




