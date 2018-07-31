from django.urls import re_path

from .views import (

		payment_method_view,
		payment_method_create_view,

			)








app_name = "billing"





urlpatterns = [

		
		re_path(r'^payment-method/$', payment_method_view, name="billing_payment_method"),
		re_path(r'^payment-method/create/$', payment_method_create_view, name="billing_payment_method_endpoint"),

		









		]