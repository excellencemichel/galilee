from django.contrib import admin

from django.contrib.auth import get_user_model

from .forms import UserAdminCreationForm, UserAdminChangeForm

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



from .models import GuestEmail, EmailActivation

# Register your models here.


User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin', "first_name", 'last_name', "mobile")
    list_filter = ('admin', "is_staff", "is_active")
    fieldsets = (
        (None, {'fields': ('email', 'password', "mobile")}),
        ('Personal info', {'fields': ("first_name","last_name")}),
        ('Permissions', {'fields': ('admin', "is_staff", "is_active",)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', "mobile", 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)



# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)




class GuestEmailAdmin(admin.ModelAdmin):
	search_fields = ["email"]
	class Meta:
		model = GuestEmail


admin.site.register(GuestEmail, GuestEmailAdmin)




class EmailActivationAdmin(admin.ModelAdmin):
    search_fields = ["email"]
    class Meta:
        model = EmailActivation


admin.site.register(EmailActivation,  EmailActivationAdmin)