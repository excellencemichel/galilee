
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required


from django.views.generic import DetailView, ListView

from django.shortcuts import render
from django.http import Http404

#Local import

from billing.models import BillingProfile

from .models import Order

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
