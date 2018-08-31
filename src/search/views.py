from django.shortcuts import render
from django.db.models import Q
from django.views.generic import ListView

from products.models import Product
from carts.models import Cart 
# Create your views here.



class SearchProductView(ListView):
	# queryset = Product.objects.all()
	template_name = "search/view.html"


	def get_context_data(self, *args, **kwargs):
		context = super(SearchProductView, self).get_context_data(*args, **kwargs)
		context["query"] = self.request.GET.get("q")
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context["cart"] = cart_obj

		return context



	def get_queryset(self, *args, **kwargs):
		"""
		__icontains = field contains this: Si le champ contient le mot
		__iexact = field is exactly this: Si le champ contient exactement le mot

		"""
		request = self.request
		method_dict = request.GET
		query = method_dict.get("q", None)
		if query is not None:
			return Product.objects.search(query)
		return Product.objects.featured()

