from django.urls import re_path, path

from .views import (


			ProductListView,
			product_list_view,
			ProductDetailView,
			product_detail_view,
			ProductFeaturedListView,
			ProductFeaturedDetailView,
			ProductDetailSlugView,
			UserProductHistoryView,


			)









app_name = "products"




urlpatterns = [


			path("products-fbv", product_list_view, name="product_list_view"),
			path("", ProductListView.as_view(), name="list"),


			re_path(r'^detail-fbv/(?P<pk>\d+)/$', product_detail_view, name="product_detail_view"),			

			re_path(r'^featured/(?P<pk>\d+)/$', ProductFeaturedDetailView.as_view(), name="product_detail_featured_class"),
			path("featured", ProductFeaturedListView.as_view(), name="product_featured_list_class"),

			re_path(r'^(?P<slug>[\w-]+)/detai/$', ProductDetailSlugView.as_view(), name="detail"),
			re_path(r'^detail/(?P<pk>\d+)/$', ProductDetailView.as_view(), name="product_detail_class"),
			path('history/products', UserProductHistoryView.as_view(), name="user_product_history"),















		]