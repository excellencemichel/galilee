from django.urls import re_path, path

from .views import (
			jscours,
			testajax
			)









app_name = "jscours"




urlpatterns = [

		
		path("", jscours, name="jscours"),
		path("testajax", testajax, name="testajax"),


		









		]