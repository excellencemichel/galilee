from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth import (
    authenticate, login, get_user_model, password_validation,
)

from django import forms

from django.utils.safestring import mark_safe
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import pgettext, ugettext, ugettext_lazy as _

from django.template import loader

from django.core.mail import EmailMultiAlternatives

from django.urls import reverse

#Local import
from .models import EmailActivation, GuestEmail

from .signals import user_logged_in



User =get_user_model()



class UserDetailUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First name"), required=False, widget=forms.TextInput(attrs = {"class": "form-control input-xs",}) )
    last_name = forms.CharField(label=_("Last name"), required=False, widget=forms.TextInput(attrs = {"class": "form-control input-xs",}))
    mobile  = forms.CharField(label=_("Phone number"), required=True, widget=forms.TextInput(attrs = {"class": "form-control input-xs",}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "mobile"]

class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label= _("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',"password", "first_name", "last_name", "mobile",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'admin', "first_name", "last_name", "mobile",)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]



class GuestForm(forms.ModelForm):
	# email 	= forms.EmailField()
    class Meta:
        model = GuestEmail
        fields  =  ["email"]


    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)



    def save(self, commit=True):
        obj = super(GuestForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session["guest_email_id"] = obj.id 

        return obj


class LoginForm(forms.Form):
    email = forms.EmailField(label = _("Email address"), widget=forms.TextInput(attrs = {"class": "form-control input-xs",}))
    password = forms.CharField(label = _("Password"), widget=forms.PasswordInput(attrs = {"class": "form-control input-xs",}))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)




    def clean(self):
        request      = self.request
        data         = self.cleaned_data
        email        = data.get("email")
        password     = data.get("password")


        qs      = User.objects.filter(email=email)
        if qs.exists():
            # print(qs)
            #That email is registered, chech active
            not_active = qs.filter(is_active=False)
            if not_active.exists():
                ## not active, check email activation
                link = reverse("accounts:resend_activation")

                reconfirm_msg = """ Go here to
                            <a href="{resend_link}"> resend confirmation email</a>
                            """.format(resend_link = link)


                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    msg1 = "Please check your email to confirm your account or" + reconfirm_msg.lower()
                    raise forms.ValidationError(mark_safe(_(msg1)))

                email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
                if email_confirm_exists:
                    msg2 = "Email not confirmed" + reconfirm_msg
                    raise forms.ValidationError(mark_safe(_(msg2)))

                if not is_confirmable and not email_confirm_exists:
                    msg3 = "This user is inactive" + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg3))


        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalide credentials")

        login(request, user)
        self.user = user
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            del request.session["guest_email_id"]
        except:
            pass
    
        return data








class ReactivateEmailForm(forms.Form):
    email       =  forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("accounts:register")
            msg = _(""" This email does not exists, would you like to <a href="{link}">register</a>""".format(link=register_link))
            raise forms.ValidationError(mark_safe(msg))

        return email






class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    email = forms.EmailField(label = _("Email address"), widget=forms.TextInput(attrs = {"class": "form-control input-xs",}))
    mobile  = forms.CharField(label=_("Phone number"), required=True, widget=forms.TextInput(attrs = {"class": "form-control input-xs",}))
    password1 = forms.CharField(label= _("Password"), widget=forms.PasswordInput(attrs = {"class": "form-control input-xs","id": "controleMdpSaisi"}))
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput(attrs = {"class": "form-control input-xs"}))

    class Meta:
        model = User
        fields = ('email',"mobile",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False #we'll send confirmation email via signals
        # obj = EmailActivation.objects.create(user=user)
        # obj.send_activation_email()
        if commit:
            user.save()
        return user







class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = User._default_manager.filter(**{
            '%s__iexact' % User.get_email_field_name(): email,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                email, html_email_template_name=html_email_template_name,
            )


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    })
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password