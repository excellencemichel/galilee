
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


from django.http import Http404
from django.shortcuts import render, get_object_or_404

from django.utils.decorators import method_decorator


from django.contrib.auth.decorators import login_required




#Local import
from analytics.mixins import ObjectViewedMixin
from carts.models import Cart
from .models import Product

# Create your views here.


class ProductFeaturedListView(ListView):
	template_name = "products/list.html"


	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.featured()


class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
	queryset = Product.objects.featured()
	template_name = "products/featured_detail.html"

	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.all()


class ProductListView(ListView):
	# queryset = Product.objects.all()
	template_name = "products/list.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductListView,self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context["cart"] = cart_obj
		return context



	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.all()




@method_decorator(login_required, name='dispatch') # ça peut marcher si on veux rediriger l'utilisateur sur la page de connexion
class UserProductHistoryView(ListView):
	template_name = "products/user_history.html"


	def get_context_data(self, *args, **kwargs):
		context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context["cart"] = cart_obj
		return context



	def get_queryset(self, *args, **kwargs):
		request = self.request
		views 	= request.user.objectviewed_set.by_model(Product, model_queryset=True) #all().filter(content_type__name="product")

		
		return views #Product.objects.filter(pk__in=viewed_ids)




def product_list_view(request):


	queryset = Product.objects.all()

	context = {
	"qs" :queryset,
	}


	return render(request, "products/product_list_view.html", context)





class ProductDetailView(ObjectViewedMixin, DetailView):
	queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context["cart"] = cart_obj
		return context


	# def get_context_data(self, *args, **kwargs):

	# 	#Ici on charge le contexte par défaut
	# 	context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
	# 	print(context)
	# 	return context



	def get_object(self, *args, **kwargs):
		request = self.request
		pk = self.kwargs.get("pk")
		instance = Product.objects.get_by_id(pk)
		if instance is None:
			raise Http404("Product doesn't exist")

		return instance


	def get_queryset(self, *args, **kwargs):
		request = self.request
		pk = self.kwargs.get("pk")
		return Product.objects.filter(pk=pk)




def product_detail_view(request, pk=None, *args, **kwargs):


	# instance = Product.objects.get(pk=pk)
	# instance = get_object_or_404(Product, pk=pk)

	instance = Product.objects.get_by_id(pk)

	context = {
	"object" : instance,
	}


	return render(request, "products/detail.html", context)





class ProductDetailSlugView(ObjectViewedMixin, DetailView):
	# queryset = Product.objects.all()
	template_name = "products/detail.html"


	def get_object(self, *args, **kwargs):

		request = self.request
		slug = self.kwargs.get("slug")


		# instance = get_object_or_404(Product, slug=slug, active=True)
		try:

			instance = Product.objects.get(slug=slug, active=True)
		except Product.DoesNotExist:
			raise Http404("Product doesn't exist")

		except Product.MultipleObjectsReturned:
			qs = Product.objects.filter(slug=slug, active=True)
			instance = qs.first()

		except:
			raise Http404("Uhhhhh")

		# object_viewed_signal.send(instance.__class__, instance=instance, request=request)
		return instance