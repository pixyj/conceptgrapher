from uber.serializers import ModelSerializer

from quiz.serializers import QuizSerializer


class ConceptQuizSerializer(ModelSerializer):

	def to_dict(self, instance):
		attrs = {}
		attrs['quiz'] = QuizSerializer().to_dict(instance.quiz)
		attrs['concept'] = {
			'name': instance.concept.name,
			'topic': instance.concept.topic.name
		}
		return attrs


class ConceptSerializer(ModelSerializer):
	class Meta:
		fields = ['id', 'name', 'slug']



class ConceptPlusQuizCountSerializer(ConceptSerializer):
	def to_dict(self, instance):
		attrs = super(ConceptPlusQuizCountSerializer, self).to_dict(instance)
		attrs['quiz_count'] = instance.quiz_set.count()
		return attrs
	
