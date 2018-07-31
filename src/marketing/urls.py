from django.urls import re_path

from .views import (

	MarketingPreferenceUpdateView,
	MailchimpWebhookView,
			)









app_name = "marketing"




urlpatterns = [

		
		re_path(r'^settings/email/$', MarketingPreferenceUpdateView.as_view(), name="marketing_pref"),
		re_path(r'^webhook/mailchimp/$', MailchimpWebhookView.as_view(), name="webhook_mailchimp"),

		









		]