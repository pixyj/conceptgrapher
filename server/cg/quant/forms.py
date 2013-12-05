from django.forms import ModelForm
from .models import ConceptQuizAttempt

class ConceptQuizAttemptForm(ModelForm):
	class Meta:
		model = ConceptQuizAttempt
		fields = ['guess', 'result']
