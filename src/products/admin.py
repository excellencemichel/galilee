from django.contrib import admin


from .models import Product, ProductFile

# Register your models here.


class ProductFileInline(admin.TabularInline):
	model = ProductFile
	extra = 1




class ProductAdmin(admin.ModelAdmin):
	list_display = ["__str__", "slug", "is_digital"]
	prepopulated_fields = {"slug": ("title",),}
	inlines = [ProductFileInline]


	class Meta:
		model = Product





admin.site.register(Product, ProductAdmin)


class ProductFileAdmin(admin.ModelAdmin):
	list_display = ["__str__", "id"]

admin.site.register(ProductFile, ProductFileAdmin)



