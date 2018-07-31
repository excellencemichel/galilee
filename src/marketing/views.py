from django.conf import settings

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from django.urls import reverse, reverse_lazy


from django.views.generic import UpdateView, View

from django.http import HttpResponse

from django.shortcuts import render



from .models import MarketingPreference

from .forms import MarketingPreferenceForm

from .utils import Mailchimp

from .mixins import CsrfExemptMixin



MALCHIMP_EMAIL_LIST_ID = getattr(settings, "MALCHIMP_EMAIL_LIST_ID")



# Create your views here.


@method_decorator(login_required, name='dispatch') # ça peut marcher si on veux rediriger l'utilisateur sur la page de connexion
class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
	form_class = MarketingPreferenceForm
	template_name = "base/forms.html"
	success_url  = reverse_lazy("marketing:marketing_pref")
	success_message = _("Your email prefereces have been updated. Thank you !")



	# def dispatch(self, *args, **kwargs):
	# 	""" Cette fonction est définie c'est pour afficher le message à l'utilisateur sinon le
	# 	décorateur fait déjà la protection de login
	# 	"""
	# 	user = self.request.user
	# 	if not user.is_authenticated():
	# 		return HttpResponse("Not allowed", status = 400)
	# 	return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)


	def get_object(self):

		user = self.request.user
		obj, created 	= MarketingPreference.objects.get_or_create(user=user)
		return obj



	def get_context_data(self, *args, **kwargs):
		context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
		context["title"] = "Update email Prefereces"
		return context









def mailchimp_webhook_view(request):
	data = request.POST
	list_id = get("data[list_id]")
	if str(list_id) == str(MALCHIMP_EMAIL_LIST_ID):
		hook_type = data.get("type")
		email 	= data.get("data[email]")
		response_status, response = Mailchimp().check_subscription_status(email)
		sub_status 	= response["status"]
		is_subbeb = None
		mailchimp_subbed = None
		if sub_status == "subscribed":
			is_subbeb, mailchimp_subbed = (True, True)
			
		elif sub_status == "unsubscribed":
			is_subbeb, mailchimp_subbed = (False, False)

		if is_subbeb is not None and mailchimp_subbed is not None:
			qs = MarketingPreference.objects.filter(user__email__iexact=email_address)
			if qs.exists():
				qs.update(
						subscribed=is_subbeb,
						mailchimp_subscribed=mailchimp_subbed,
						mailchimp_msg= str(data)
						)



	return HttpResponse("Thank you", status=200)






class MailchimpWebhookView(CsrfExemptMixin, View):
	print("mailchimp_webhook_view running")

	# def get(request, *args, **kwargs):
	# 	return HttpResponse("Thank you brother", status=200)
	
	def post(self, request, *args, **kwargs):
		data = request.POST
		list_id = data.get("data[list_id]")
		if str(list_id) == str(MALCHIMP_EMAIL_LIST_ID):
			hook_type 			= data.get("type")
			email 		 		= data.get("data[email]")
			response_status, response = Mailchimp().check_subscription_status(email)
			sub_status  = response["status"]
			is_subbeb   = None
			mailchimp_subbed = None
			if sub_status == "subscribed":
				is_subbeb, mailchimp_subbed = (True, True)
			elif sub_status == "unsubscribed":
				is_subbeb, mailchimp_subbed = (False,False)
			if is_subbeb is not None and mailchimp_subbed is None:
				qs = MarketingPreference.objects.filter(user__email__iexact=email)
				if qs.exists():
					qs.update(
							subscribed = is_subbeb,
							mailchimp_subscribed = mailchimp_subbed,
							mailchimp_msg = str(data)
						)


		return HttpResponse("Thank you", status=200)