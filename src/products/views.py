import os
from wsgiref.util import FileWrapper
from mimetypes import guess_type 

from django.conf import settings
from django.views.generic import ListView, View, DetailView


from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _



from django.contrib.auth.decorators import login_required
from django.contrib import messages



#Local import
from analytics.mixins import ObjectViewedMixin
from carts.models import Cart
from orders.models import ProductPurshase
from .models import Product, ProductFile

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




	def get_object(self, *args, **kwargs):
		request = self.request
		pk = self.kwargs.get("pk")
		slug = self.kwargs.get("slug")
		instance = Product.objects.get_by_slug_id(slug, pk)
		if instance is None:
			raise Http404("Product doesn't exist")

		return instance


	def get_queryset(self, *args, **kwargs):
		request = self.request
		pk = self.kwargs.get("pk")
		slug = self.kwargs.get("slug")
		# return Product.objects.filter(pk=pk)
		return Product.objects.filter(slug=slug, pk=pk)






def product_detail_view(request, pk=None, *args, **kwargs):


	# instance = Product.objects.get(pk=pk)
	# instance = get_object_or_404(Product, pk=pk)

	instance = Product.objects.get_by_id(pk)
	cart_obj, new_obj = Cart.objects.new_or_get(self.request)


	context = {
	"object" : instance,
	"cart": cart_obj,
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


class ProductDownloadView(View):
	def get(self,request, *args, **kwargs):
		slug = kwargs.get("slug")
		pk = kwargs.get("pk")
		downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)
		if downloads_qs.count() != 1:
			raise Http404(_("Download not found"))
		download_obj = downloads_qs.first()
		#Permission checks
		can_download = False
		user_ready = True

		if download_obj.user_required:
			if not request.user.is_authenticated:
				user_ready = False
			

		purshase_products = Product.objects.none()
		if download_obj.free:
			can_download = True
			user_ready = True
		else:
			purshase_products = ProductPurshase.objects.products_by_request(request)
			if download_obj.product in purshase_products:
				can_download = True

		if not can_download or not user_ready:
			messages.error( request,_("You do not have access to download this item"))
			return redirect(download_obj.get_default_url())

		# aws_filepath = download_obj.generate_download_url()
		# print(aws_filepath)
		# return HttpResponseRedirect(aws_filepath)

		file_root = settings.PROTECTED_ROOT
		filepath  = download_obj.file.path # .url /media/..
		final_filepath = os.path.join(file_root, filepath) #Where the is stored
		with open(final_filepath, "rb") as f:
			wrapper = FileWrapper(f)
			mimetype = "application/force-download"
			guess_mimetype = guess_type(filepath)[0] #filene.mp4
			if guess_mimetype:
				mimetype = guess_mimetype


			response = HttpResponse(wrapper, content_type=mimetype)
			response["Content-Disposition"] = "attachment;filename=%s"%(download_obj.name)
			response["X-SendFile"] = str(download_obj.name)
			return response

		return redirect(download_obj.ge_default_url())
