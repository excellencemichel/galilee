
from django.urls import path, re_path

from .views import SalesView, SalesAjaxView


app_name = "analytics"



urlpatterns = [




		path("sales/", SalesView.as_view(), name="sales_analytics"),
		path("sales/data", SalesAjaxView.as_view(), name="sales_analytics_data"),















]
