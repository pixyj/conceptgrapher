from django.contrib import admin

from .models import Topic, Concept, ConceptRelationship, ConceptResource, ConceptQuiz

class ConceptResourceInline(admin.StackedInline):
	model = ConceptResource
	extra = 1


admin.site.register(Topic)
admin.site.register(ConceptRelationship)
admin.site.register(ConceptQuiz)

class ConceptAdmin(admin.ModelAdmin):
	inlines = [ConceptResourceInline]
	prepopulated_fields = {"slug": ("name",)}




admin.site.register(Concept, ConceptAdmin)


