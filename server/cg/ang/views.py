from django.shortcuts import render
from django.http import Http404

def show_angular_index(request, *args, **kwargs):
	import pdb
	pdb.set_trace()
	if request.path.find("/api/") != -1:
		raise Http404

	return render(request, 'index.html')