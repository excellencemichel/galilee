from math import fsum

from django.conf import settings

from django.db import models
from django.db.models.signals import pre_save, post_save

from django.urls import reverse

from ecommerce.utils import unique_order_id_generator

from billing.models import BillingProfile 
from carts.models import Cart
from addresses.models import Address
from products.models import Product 

# Create your models here.
User = settings.AUTH_USER_MODEL



ORDER_STATUS_CHOICES = (

		("created", "Created"),
		("paid", "Paid"),
		("shipped", "Shipped"),
		("refunded", "Refunded"),

	)


class OrderManagerQuerySet(models.query.QuerySet):

	def by_request(self, request):
		billing_profile, created = BillingProfile.objects.new_or_get(request)
		return self.filter(billing_profile=billing_profile)



	def not_created(self):
		return self.exclude(status="created")

class OrderManager(models.Manager):

	def get_queryset(self):
		return OrderManagerQuerySet(self.model, using=self._db)



	def by_request(self, request):
		return self.get_queryset().by_request(request)


	def new_or_get(self, billing_profile, cart_obj):
		created = False
		qs	= self.get_queryset().filter(
				billing_profile=billing_profile,
				cart=cart_obj,
				active=True, status="created")
		if qs.count() == 1:
			obj = qs.first()

		else:
			obj = self.model.objects.create(
						billing_profile=billing_profile,
						cart=cart_obj
						)
			created = True

		return obj, created


class Order(models.Model):
	billing_profile 	= models.ForeignKey(BillingProfile,  null=True, blank=True, on_delete=models.CASCADE)
	order_id			= models.CharField(max_length=120, blank=True) # Maybe AB18DE#
	shipping_address 	= models.ForeignKey(Address, related_name="shipping_address", null =True, blank=True, on_delete=models.CASCADE)
	billing_address		= models.ForeignKey(Address, related_name="billing_address", null=True, blank=True, on_delete=models.CASCADE) 
	cart 				= models.ForeignKey(Cart, on_delete=models.CASCADE)
	status  			= models.CharField(max_length=250, default="created", choices=ORDER_STATUS_CHOICES)
	shipping_total		= models.DecimalField(default=5.999, max_digits=100, decimal_places=3)
	total				= models.DecimalField(default=0.000, max_digits=100, decimal_places=3)
	active				= models.BooleanField(default=True)

	update 				= models.DateTimeField(auto_now=True)
	timestamp 			= models.DateTimeField(auto_now_add=True)



	objects	= OrderManager()

	class Meta:
		ordering = ["-timestamp", "-update"]


	def get_absolute_url(self):
		return reverse("orders:detail", kwargs={"order_id": self.order_id})



	def get_status(self):
		if self.status == "shipped":
			return "Shipped"

		elif self.status == "refunded":
			return "Refunded order"

		return "Shipped soon"

	def __str__(self):
		return self.order_id



	def update_total(self):
		cart_total = self.cart.total
		shipping_total = self.shipping_total
		new_total = fsum([cart_total, shipping_total])
		formatted_total = format(new_total, ".3f")
		print(type(new_total))
		self.total = formatted_total
		self.save()
		return new_total


	def check_done(self):
		shipping_address_required = not self.cart.is_digital
		shipping_done = False
		if  shipping_address_required and self.shipping_address:
			shipping_done = True

		elif shipping_address_required and not self.shipping_address:
			shipping_done = False
		else:
			shipping_done = True

		billing_profile 	= self.billing_profile
		billing_address		= self.billing_address

		total = self.total


		if billing_profile and billing_address and shipping_done and total > 0:
			return True

		return False


	def update_purshases(self):
		for p in self.cart.products.all():
			obj, created  = ProductPurshase.objects.get_or_create(
				order_id = self.order_id,
				product=p,
				billing_profile=self.billing_profile
				)

		return ProductPurshase.objects.filter(order_id=self.order_id).count()


	def mark_paid(self):
		if self.status != "paid":
			if self.check_done():
				self.status = "paid"
				self.save()
				self.update_purshases()
		return self.status




def pre_save_create_order_id(sender, instance, *args, **kwargs):
	if not instance.order_id:
		instance.order_id = unique_order_id_generator(instance)

	qs	= Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
	if qs.exists():
		qs.update(active=False)





pre_save.connect(pre_save_create_order_id,sender=Order)



def post_save_cart_total(sender, instance, created, *args, **kwargs):
	if not created:
		cart_obj = instance
		cart_total = cart_obj.total
		cart_id = cart_obj.id 
		qs = Order.objects.filter(cart__id=cart_id)
		if qs.count() == 1:
			order_obj = qs.first()
			order_obj.update_total()



post_save.connect(post_save_cart_total, sender=Cart)



def post_save_order(sender, instance, created, *args, **kwargs):
	print("Running")
	if created:
		print("Updating ... first")
		instance.update_total()



post_save.connect(post_save_order, sender=Order)


class ProductPurshaseQuerySet(models.query.QuerySet):

	def active(self):
		return self.filter(refunded=False)


	def digital(self):
		return self.filter(product__is_digital=True)


	def by_request(self, request):
		billing_profile, created = BillingProfile.objects.new_or_get(request)
		return self.filter(billing_profile=billing_profile)



class ProductPurshaseManager(models.Manager):

	def get_queryset(self):
		return ProductPurshaseQuerySet(self.model, using=self._db)

	def all(self):
		return self.get_queryset().active()


	def digital(self):
		return self.get_queryset().digital()


	def by_request(self, request):
		return self.get_queryset().by_request(request)


	def products_by_id(self, request):
		qs = self.by_request(request).digital()
		ids_ = [x.product.id for x in qs]
		return ids_



	def products_by_request(self, request):
		ids_ = self.products_by_id(request)
		product_qs  = Product.objects.filter(id__in=ids_).distinct()
		return product_qs

class ProductPurshase(models.Model): #Purshase veut dire achat
	order_id			= models.CharField(max_length=120)
	billing_profile 	= models.ForeignKey(BillingProfile,on_delete=models.CASCADE)
	product 			= models.ForeignKey(Product, on_delete=models.CASCADE)
	refunded 			= models.BooleanField(default=False)
	update 				= models.DateTimeField(auto_now=True)
	timestamp 			= models.DateTimeField(auto_now_add=True)


	objects = ProductPurshaseManager()

	def __str__(self):
		return self.product.title


