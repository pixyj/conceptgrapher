from django.contrib import admin
from django.db import models

from pagedown.widgets import AdminPagedownWidget


from .models import Quiz, Choice
from topo.models import ConceptQuiz


class ChoiceInline(admin.StackedInline):
	model = Choice
	extra = 2

class ConceptQuestionInline(admin.StackedInline):
	model = ConceptQuiz
	extra = 0

class QuizAdmin(admin.ModelAdmin):
	inlines = [ChoiceInline, ConceptQuestionInline]
	formfield_overrides = {
	    models.TextField: {'widget': AdminPagedownWidget },
	}



admin.site.register(Quiz, QuizAdmin)

from django.contrib import admin

# Register your models here.
