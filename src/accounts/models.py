from datetime import timedelta

from django.conf import settings

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save

from django.core.mail import send_mail


from django.urls import reverse


from django.contrib.auth.models import (
				AbstractBaseUser, BaseUserManager,
			)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from django.template.loader import get_template




#Local import
from ecommerce.utils import random_string_generator, unique_key_generator



# Create your models here.


#Def variable global
DEFAULT_ACTIVATION_DAYS = getattr(settings, "DEFAULT_ACTIVATION_DAYS", 7)


class UserManager(BaseUserManager):
	def create_user(self, email, mobile, password=None, is_active=True, is_staff=False, is_admin=False):
		if not email:
			raise ValueError("Users must have an email address")

		if not password:
			raise ValueError("Users must have a password")

		if not mobile:
			raise (_("Users must be have a mobile number"))
		user_obj	= self.model(
				email = self.normalize_email(email),
				mobile = mobile
			)
		user_obj.set_password(password)
		user_obj.is_staff = is_staff
		user_obj.admin = is_admin
		user_obj.is_active = is_active
		user_obj.save(using=self._db)
		return user_obj



	def create_staffuser(self, email, mobile, password):
		user 	 = self.create_user(
			email,
			mobile,
			password=password,
			is_staff = True)

		return user

	def create_superuser(self, email, mobile, password):
		user 	 = self.create_user(
			email,
			mobile,
			password=password,
			is_staff = True,
			is_admin = True
			)
		return user

class User(AbstractBaseUser):
	email 	= models.EmailField(max_length=255, unique=True)
	is_active	= models.BooleanField(default=True) #Can login
	is_staff 	= models.BooleanField(default=False) #staff user non superuser but can access at administrator
	admin 	= models.BooleanField(default=False) #superuser
	timestamp	= models.DateTimeField(auto_now_add=True)

	first_name = models.CharField(_("first name"), max_length=250, blank=True)
	last_name = models.CharField(_("last name"), max_length=250, blank=True)
	mobile	= models.CharField(max_length=250)


	USERNAME_FIELD = "email" #username
	REQUIRED_FIELDS = ["mobile"]

	objects	= UserManager()

	def __str__(self):
		return str(self.email)


	def get_full_name(self):
		full_name = "%s %s" %(self.first_name, self.last_name)
		return full_name



	def get_short_name(self):
		return self.first_name


	def get_mobile(self):
		return self.mobile


	def has_perm(self, per, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True
		

	@property
	def is_staff_user(self):
		if self.is_admin:
			return True
		return self.is_staff


	# @property
	# def is_active(self):
	# 	return self.active


	@property
	def is_admin(self):
		return self.admin



class EmailActivationQuerySet(models.query.QuerySet):
	def confirmable(self):
		now = timezone.now()
		start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
		end_range = now
		return self.filter(

				activated = False,
				forced_expered = False,
			).filter(
				timestamp__gt=start_range,
				timestamp__lte=end_range
			)



class EmailActivationManager(models.Manager):
	def get_queryset(self):
		return EmailActivationQuerySet(self.model, using=self._db)


	def confirmable(self):
		return self.get_queryset().confirmable()


	def email_exists(self, email):
		return self.get_queryset().filter(
				Q(email=email)|
				Q(user__email=email)
			  	).filter(
				 activated=False
				 )


class EmailActivation(models.Model):
	user 			= models.ForeignKey(User, on_delete=models.CASCADE)
	email 			= models.EmailField()
	key 			= models.CharField(max_length=120, blank=True, null=True)
	activated 		= models.BooleanField(default=False)
	forced_expered  = models.BooleanField(default=False)
	expires         = models.IntegerField(default=7)
	timestamp 		= models.DateTimeField(auto_now_add=True)
	update 			= models.DateTimeField(auto_now=True)


	objects = EmailActivationManager()

	def __str__(self):
		return str(self.email)


	def can_activate(self):
		qs = EmailActivation.objects.filter(pk=self.pk).confirmable()

		if qs.exists():
			return True
		return False


	def activate(self):
		if self.can_activate():
			user = self.user
			user.is_active = True
			user.save()
			self.activated =True
			self.save()
			return True
		return False


	def regerate(self):
		self.key = None
		self.save()
		if self.key is not None:
			return True

		return False



	def send_activation_email(self):
		print("Debut fonction send_activation_email")
		if not self.activated and not self.forced_expered:
			print("forced_expered")
			if self.key:
				print("Key")
				base_url = getattr(settings, "BASE_URL")
				key_path = reverse("accounts:email_activate", kwargs ={"key":self.key })#use reverse
				path = "{base}{path_}".format(base=base_url, path_=key_path)
				context = {
				"path": path,
				"email": self.email
				}
				txt_ = get_template("accounts/emails/verify.txt").render(context)
				html_ = get_template("accounts/emails/verify.html").render(context)
				subject = _("For activate your account in Sylimarket place")
				from_email = settings.DEFAULT_FROM_EMAIL
				recipient_list = [self.email]
				print("Dans la fonction d'envoi")
				sent_mail = send_mail(
						subject,
						txt_,
						from_email,
						recipient_list,
						html_message=html_,
						fail_silently=False,
					)

				return sent_mail
		return False


def pre_save_email_activation(sender, instance, *args, **kwargs):
	if not instance.activated and not instance.forced_expered :
		if not instance.key:
			instance.key = unique_key_generator(instance)


pre_save.connect(pre_save_email_activation, sender=EmailActivation)

def post_save_email_activate(sender, instance, created, *args, **kwargs):
	print("Ici a été executé")
	if created:
		print("A été created")
		obj = EmailActivation.objects.create(user=instance, email=instance.email)
		obj.send_activation_email()


post_save.connect(post_save_email_activate, sender=User)





class GuestEmail(models.Model):
	email 		= models.EmailField()
	active 		= models.BooleanField(default=True)
	update		= models.DateTimeField(auto_now=True)
	timestamp	= models.DateTimeField(auto_now_add = True)




	def __str__(self):
		return str(self.email)
