from django.urls import re_path, path

from .views import (


			ProductListView,
			product_list_view,
			ProductDetailView,
			product_detail_view,
			ProductFeaturedListView,
			ProductFeaturedDetailView,
			# ProductDetailSlugView,
			UserProductHistoryView,
			ProductDownloadView,


			)









app_name = "products"




urlpatterns = [


			path("products-fbv", product_list_view, name="product_list_view"),
			path("", ProductListView.as_view(), name="list"),


			re_path(r'^(?P<slug>[\w-]+)-(?P<pk>\d+)/detail/$', product_detail_view, name="detail"),			

			re_path(r'^featured/(?P<pk>\d+)/$', ProductFeaturedDetailView.as_view(), name="product_detail_featured_class"),
			path("featured", ProductFeaturedListView.as_view(), name="product_featured_list_class"),

			# re_path(r'^(?P<slug>[\w-]+)-(?P<pk>\d+)/detail/$', ProductDetailView.as_view(), name="detail"),
			# re_path(r'^(?P<slug>[\w-]+)/detail/$', ProductDetailSlugView.as_view(), name="product_detail_class"), #product_detail_class
			path('history/products', UserProductHistoryView.as_view(), name="user_product_history"),
			re_path(r'^(?P<slug>[\w-]+)/(?P<pk>\d+)/$', ProductDownloadView.as_view(), name="download"),

















		]