
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _


from django.contrib.auth.decorators import login_required


from django.views.generic import DetailView, ListView, View

from django.shortcuts import render
from django.http import Http404, JsonResponse

#Local import

from billing.models import BillingProfile

from .models import Order, ProductPurshase

# Create your views here.

@method_decorator(login_required, name='dispatch') # ça peut marcher si on veux rediriger l'utilisateur sur la page de connexion
class OrderListView(ListView):

	def get_queryset(self):
		return Order.objects.by_request(self.request).not_created()




@method_decorator(login_required, name='dispatch') 
class OrderDetailView(DetailView):

	def get_object(self):
		# return Order.objects.get(id=self.kwargs.get("id"))
		# return Order.objects.get(slug=self.kwargs.get("slug"))
		qs = Order.objects.by_request(
			self.request
				).filter(
				order_id=self.kwargs.get("order_id"
					))
		if qs.count() == 1:
			return qs.first()

		raise Http404

@method_decorator(login_required, name='dispatch') 
class LibraryView(ListView):
	template_name = "orders/library.html"
	def get_queryset(self):
		return ProductPurshase.objects.products_by_request(self.request)



# @method_decorator(login_required, name='dispatch') # ça peut marcher si on veux rediriger l'utilisateur sur la page de connexion
class VerifyOwnership(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			data = request.GET 
			product_id = request.GET.get("product_id", None)
			print(int(product_id))
			if product_id is not None:
				product_id = int(product_id)
				ownership_ids  = ProductPurshase.objects.products_by_id(request)
				if product_id in ownership_ids:
					return JsonResponse({"owner":True})

			return JsonResponse({"owner": False})

		raise Http404