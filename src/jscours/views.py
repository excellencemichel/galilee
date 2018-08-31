from django.shortcuts import render

# Create your views here.


def jscours(request):
	context = {}
	return render(request, "jscours/jscours.html", context)






def testajax(request):

	context = {
	"nom": "Michel",
	"prenom": "Pépé Michel",
	"query": request.POST.get("q")
	}


	return render(request, "jscours/testajax.html", context)