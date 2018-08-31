import os
import random
from django.conf import settings

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save

from django.core.files.storage import FileSystemStorage

from django.urls import reverse

from ecommerce.utils import unique_slug_generator, get_filename
from ecommerce.aws.utils import ProtectedS3Storage
from ecommerce.aws.download.utils import AWSDownload
# Create your models here.

def get_filename_ext(filepath):
	base_name = os.path.basename(filepath)
	name, ext = os.path.splitext(base_name)
	return name, ext


def upload_image_path(instance, filename):
	print(instance)
	print(filename)

	new_filename = random.randint(1, 11337712127)

	name, ext =get_filename_ext(filename)
	final_filename = "{new_filename}{ext}".format(new_filename=new_filename, ext=ext)

	return "products/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)



TYPES_PRODUCT = (

		("phone", "Phone"),
		("electronique", "Electronique"),
		("luxe", "Luxe"),
		("tablette", "Tablette"),
		("computer", "Computer"),
		("cloths", "Cloths"),
		("shoe", "Shoe"),
		("food", "Food"),
		("fourniture", "Fourniture"),
		("materiel", "Materiel"),
		("pants", "Pants"),
		("electromenager", "Electroménager"),




	)



class ProductQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)
	def featured(self):
		return self.filter(featured=True)


	def search(self, query):
		lookups =( 
				 Q(title__icontains=query)|
				 Q(slug__icontains=query)|
				 Q(description__icontains=query)|
				 Q(price__icontains=query)|
				 Q(tag__title__icontains=query)
				)
		return self.filter(lookups).distinct()


	def is_phone(self):
		return self.filter(types_product="phone")


	def is_tablette(self):
		return self.filter(types_product="tablette")

	def is_cloths(self):
			return self.filter(types_product="cloths")


	def is_pants(self):
			return self.filter(types_product="pants")


	def is_food(self):
			return self.filter(types_product="food")


	def is_fourniture(self):
			return self.filter(types_product="fourniture")




	def is_materiel(self):
			return self.filter(types_product="materiel")



	def is_computer(self):
			return self.filter(types_product="computer")



	def is_shoe(self):
			return self.filter(types_product="shoe")



	def is_electromenager(self):
		return self.filter(types_product="electromenager")







class ProductManager(models.Manager):

	def get_queryset(self):
		return ProductQuerySet(self.model, using=self._db)


	# def all(self):
	# 	return self.get_queryset().active()

	def featured(self):
		return self.get_queryset().featured()

	def get_by_id(self, id):

		qs = self.get_queryset().filter(id=id)
		if qs.count() ==1:
			return qs.first()

		return None


	def get_by_slug_id(self, slug, id):

		qs = self.get_queryset().filter(slug=slug, id=id)
		if qs.count() ==1:
			return qs.first()

		return None

		# return self.get_queryset().filter(id=id)


	def search(self, query):
		return self.get_queryset().active().search(query)




	def is_phone(self):
		return self.get_queryset().active().is_phone()


	def is_tablette(self):
		return self.get_queryset().active().is_tablette()

	def is_cloths(self):
			return self.get_queryset().active().is_cloths()


	def is_pants(self):
			return self.get_queryset().active().is_pants()


	def is_food(self):
			return self.get_queryset().active().is_food()


	def is_fourniture(self):
			return self.get_queryset().active().is_fourniture()




	def is_materiel(self):
			return self.get_queryset().active().is_materiel()



	def is_computer(self):
			return self.get_queryset().active().is_computer()



	def is_shoe(self):
			return self.get_queryset().active().is_shoe()



	def is_electromenager(self):
		return self.get_queryset().active().is_electromenager()







class Product(models.Model):


	title  				= models.CharField(max_length= 250)
	slug 				= models.SlugField(blank=True, unique=True)
	pseudo_name 		= models.CharField(max_length=250)
	product_marque      = models.CharField(max_length=250)
	product_model		= models.CharField(max_length=250, null=True, blank=True)
	types_product  		= models.CharField(max_length=250, choices=TYPES_PRODUCT)
	description			= models.TextField()
	price 				= models.DecimalField(decimal_places=2, max_digits=20, default=39.99)
	image 				= models.ImageField(upload_to=upload_image_path, null=True, blank=False)

	featured			= models.BooleanField(default=False)

	active 				= models.BooleanField(default=True)
	timestamp			= models.DateTimeField(auto_now_add=True)
	is_digital 			= models.BooleanField(default=False)


	objects = ProductManager()




	def get_absolute_url(self):
		# return "/products/{slug}".format(slug=self.slug)

		return reverse("products:detail", kwargs={ "slug": self.slug, "pk": self.id })



	def __str__(self):
		return str(self.title)


	def get_downloads(self):
		qs = self.productfile_set.all()
		return qs


def product_pre_save_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = unique_slug_generator(instance)



pre_save.connect(product_pre_save_receiver, sender=Product)




def upload_product_file_loc(instance, filename):
	slug = instance.product.slug
	id_ = 0
	print(instance.id)
	id_ = instance.id
	if id_ is None:
		Klass = instance.__class__
		qs = Klass.objects.all().order_by("-pk")
		if qs.exists():
			id_ = qs.first().id + 1
		else:
			id_ = 0

	if not slug:
		slug = unique_slug_generator(instance.product)
	location = "product_media/{slug}/{id}/".format(slug=slug, id=id_)


	return location + filename #path/to/file/filename.mp4

stockage = FileSystemStorage(location=settings.PROTECTED_ROOT)

class ProductFile(models.Model):
	product 		= models.ForeignKey(Product, on_delete=models.CASCADE)
	name 			= models.CharField(max_length=120, null=True, blank=True)
	image 			= models.ImageField(
					upload_to=upload_product_file_loc,
					)


	free 			= models.BooleanField(default=False) #purshase required
	user_required   = models.BooleanField(default=False) #user doesn't matter (doesn't matter : Peut importe)



	def __str__(self):
		return str(self.image.name)

	@property
	def display_name(self):
		og_name = get_filename(self.image.name)
		if self.name:
			return self.name
		return og_name


	def get_default_url(self):
		return self.product.get_absolute_url()


	def generate_download_url(self):
		bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME")
		region = getattr(settings,"S3DIRECT_REGION")
		access_key = getattr(settings,"AWS_ACCESS_KEY_ID")
		secret_key = getattr(settings,"AWS_SECRET_ACCESS_KEY")
		if not secret_key or not access_key or not bucket or not region:
			print("Ca ne marche pas")
			return "/product-not-found/"
		PROTECTED_DIR_NAME = getattr(settings, "PROTECTED_DIR_NAME", "protected" )
		path ="{base}/{file_path}".format(base=PROTECTED_DIR_NAME, file_path=str(self.file))
		print(path)

		aws_dl_object =  AWSDownload(access_key=access_key, secret_key=secret_key, bucket=bucket, region=region)
		file_url = aws_dl_object.generate_url(path, self.display_name) #,new_filename='New awesome file')
		return file_url


	def get_dowload_url(self):
		return reverse("products:download", kwargs={"slug":self.product.slug, "pk":self.pk})
