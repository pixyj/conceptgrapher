from uber.serializers import ModelSerializer

class QuizSerializer(ModelSerializer):

	class Meta:
		fields = ['id', 'question', 'answer']

	def to_dict(self, model):
		attrs = super(QuizSerializer, self).to_dict(model)
		choices = []
		for choice in model.choice_set.all():
			choice = {
				'text': choice.text,
				'is_correct': choice.is_correct
			}
			choices.append(choice)
		attrs['choices'] = choices
		return attrs


class QuizAttemptSerializer(ModelSerializer):

	class Meta:
		fields = ['created', 'guess', 'result']

	

class AggregateConceptAttemptSerializer(ModelSerializer):

	class Meta:
		fields = ['correct', 'wrong']

	def to_dict(self, aggregate):
		attrs = super(AggregateConceptAttemptSerializer, self).to_dict(aggregate)
		attrs['concept_id'] = aggregate.concept_id
		return attrs



