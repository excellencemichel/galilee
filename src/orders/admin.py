from django.contrib import admin

from .models import Order, ProductPurshase

# Register your models here.

admin.site.register(Order)

admin.site.register(ProductPurshase)
