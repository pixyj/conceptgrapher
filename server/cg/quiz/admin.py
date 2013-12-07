from django.contrib import admin
from django.db import models

from pagedown.widgets import AdminPagedownWidget


from .models import Quiz, Choice, UserQuizAttempt, AnonQuizAttempt

class ChoiceInline(admin.StackedInline):
	model = Choice
	extra = 2



class QuizAdmin(admin.ModelAdmin):
	inlines = [ChoiceInline]
	formfield_overrides = {
	    models.TextField: {'widget': AdminPagedownWidget },
	}



admin.site.register(Quiz, QuizAdmin)

admin.site.register(UserQuizAttempt)
admin.site.register(AnonQuizAttempt)

from django.contrib import admin

# Register your models here.
