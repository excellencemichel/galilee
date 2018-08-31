"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""


from django.conf import settings
from django.conf.urls.static import static


from django.contrib import admin

from django.views.generic import TemplateView

from django.urls import include, path, re_path
from .views import  ( 
        home, about_page, 
        contact_page,


        )

from orders.views import LibraryView





urlpatterns = [
    path('admin/', admin.site.urls),

    path("", home, name="home"),

    path('about', about_page, name="about"),
    path('contact', contact_page, name="contact"),
    path('bootstrap', TemplateView.as_view(template_name="bootstrap/example.html")),
    path('retour', TemplateView.as_view(template_name="bootstrap/retour.html")),

    path('library', LibraryView.as_view(), name="library"),









    path('analytics/', include("analytics.urls", namespace="analytics")),
    path('products/', include("products.urls", namespace="products")),
    path('search/', include("search.urls", namespace="search")),
    path('cart/', include("carts.urls", namespace="carts")),

    path('account/', include("accounts.urls", namespace="accounts")),
    path('accounts/', include("accounts.passwords.urls", namespace="passwords")),

    path('addresses/', include("addresses.urls", namespace="addresses")),
    path('billing/', include("billing.urls", namespace="billing")),
    path('marketing/', include("marketing.urls", namespace="marketing")),
    path('orders/', include("orders.urls", namespace="orders")),


    path('jscours/', include("jscours.urls", namespace="jscours")),












]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.PROTECTED_ROOT)