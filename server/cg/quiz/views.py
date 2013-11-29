from django.shortcuts import render

from uber.serializers import model_to_jsonable_dict

# Create your views here.
def quiz_to_jsonable_dict(quiz):
	jsonable_quiz = model_to_jsonable_dict(quiz)
	choices = []
	for choice in quiz.choice_set.all():
		choices.append({"text": choice.text, "is_correct": choice.is_correct})

	jsonable_quiz['choices'] = choices
	return jsonable_quiz

