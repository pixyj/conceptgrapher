import simplejson
from datetime import datetime
from django.forms import model_to_dict


def model_to_jsonable_dict(model):
	attrs = model_to_dict(model)
	for key, value in attrs.iteritems():
		if isinstance(value, datetime):
			attrs[key] = value.isoformat()

	return attrs


def models_to_json(models):
	jsonable_models = [model_to_jsonable_dict(model) for model in models]
	return simplejson.dumps(jsonable_models)



class ModelSerializer(object):
	"""
	Very Basic serializer. 
	Doesn't serialize foreign keys/one to one and stuff.
	Using it because model_to_dict skips datetime fields
	"""
	class Meta:
		fields = [] 

	def to_json(self, model):
		return simplejson.dumps(self.to_dict(model))

	def to_dict(self, model):
		attrs = {}
		fields = self.Meta.fields
		for field in fields:
			value = getattr(model, field)
			if isinstance(value, datetime):
				value = value.isoformat()
			attrs[field] = value

		return attrs	
