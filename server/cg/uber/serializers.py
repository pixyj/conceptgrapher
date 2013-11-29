import simplejson
from datetime import datetime
from django.forms import model_to_dict


def model_to_jsonable_dict(model):
	attrs = model_to_dict(model)
	for key, value in attrs.items():
		if isinstance(value, datetime):
			attrs[key] = value.isoformat()

	return attrs


def models_to_json(models):
	jsonable_models = [model_to_jsonable_dict(model) for model in models]
	return simplejson.dumps(jsonable_models)