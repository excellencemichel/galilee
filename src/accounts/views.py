import warnings

from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, QueryDict

from django.template.response import TemplateResponse

from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from django.shortcuts import render, redirect, resolve_url

from django.urls import reverse, reverse_lazy

from django.utils.deprecation import RemovedInDjango21Warning
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import  ( 
                    authenticate,
                    login, get_user_model,
                    logout, 
                    update_session_auth_hash,

                    )
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache




#Local import

from ecommerce.mixins import NextUrlMixin, RequestFormAttachMixin

from .signals import user_logged_in

from .models import GuestEmail, EmailActivation

from .forms import (

			LoginForm,
			RegisterForm,
			GuestForm,

			PasswordChangeForm,
			PasswordResetForm,
			SetPasswordForm,
            ReactivateEmailForm,
            UserDetailUpdateForm,

	)



User =get_user_model()


# Create your views here.






@login_required
def account_home_view(request):
	return render(request, "accounts/home.html", {})


@method_decorator(login_required, name='dispatch') # ça peut marcher si on veux rediriger l'utilisateur sur la page de connexion
class AccountHomeView(DetailView):
	template_name = "accounts/home.html"

	def get_objet(self):
		return self.request.user



class AccountEmailActivateView(FormMixin,View):
    success_url = reverse_lazy("accounts:login")
    form_class = ReactivateEmailForm
    key = None
    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, _("Your email has been confirmed. Please login"))
                return redirect ("accounts:login")

            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("passwords:password_reset")
                    msg = _("""
                            Your email has already confirmed;
                            Do you need to <a href="{link}"> reset your password </a>?

                          """.format(link=reset_link))
                    messages.success(request, mark_safe(msg))
                    return redirect ("accounts:login")


        context= {"form": self.get_form(), "key":key}
        #if activated
        #retrurn redirect
        # if already activated
        # return redirect
        # if error return this 
        return render(request, "accounts/registration/activation_error.html", context)


    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        msg = _(""" Activation link sent, please check your email.""")
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation_email()
        return super(AccountEmailActivateView, self).form_valid(form)



    def form_invalid(self, form):
        context = {"form": form, "key": self.key}
        return render(self.request, "accounts/registration/activation_error.html", context)


def guest_register_view(request):

	form = GuestForm(request.POST or None)
	context = {

		"form": form,
	}

	next_	= request.GET.get("next")
	next_post	= request.POST.get("next")
	redirect_path = next_ or next_post or None
	if form.is_valid():
		email	 = form.cleaned_data.get("email")

		new_guest_email 	= GuestEmail.objects.create(email=email)
		request.session["guest_email_id"] = new_guest_email.id 

		if is_safe_url(redirect_path, request.get_host()):
			return redirect(redirect_path)
		else:
			return redirect ("accounts:register")


	return redirect("/register/")




class RegisterView(CreateView):
	form_class = RegisterForm
	template_name = "accounts/register.html"
	success_url = reverse_lazy("accounts:login")





class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    print("GuestRegisterView est executé")
    form_class = GuestForm
    default_next = "/register/"

    def form_invalid(self, form):
        return redirect(self.default_next)

    def get_success_url(self):
        return self.get_next_url()



class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = "/"
    template_name = "accounts/login.html"

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)     



@method_decorator(login_required, name='dispatch') # ça peut marcher si on veux rediriger l'utilisateur sur la page de connexion
class UserDetailUpdateView(UpdateView):
    form_class = UserDetailUpdateForm
    template_name = "accounts/detail_update_view.html"

    def get_object(self):
        return self.request.user



    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context["title"] = _("Change your account details")
        return context


    def get_success_url(self):
        return reverse("accounts:home")


# 4 views for password reset:
# - password_reset sends the mail
# - password_reset_done shows a success message for the above
# - password_reset_confirm checks the link the user clicked and
#   prompts for a new password
# - password_reset_complete shows a success message for the above

@csrf_protect
def password_reset(request,
                   template_name='accounts/registration/password_reset_form.html',
                   email_template_name='accounts/registration/password_reset_email.html',
                   subject_template_name='accounts/registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   extra_context=None,
                   html_email_template_name=None,
                   extra_email_context=None):
    warnings.warn("The password_reset() view is superseded by the "
                  "class-based PasswordResetView().",
                  RemovedInDjango21Warning, stacklevel=2)
    if post_reset_redirect is None:
        post_reset_redirect = reverse('passwords:password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
                'extra_email_context': extra_email_context,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def password_reset_done(request,
                        template_name='accounts/registration/password_reset_done.html',
                        extra_context=None):
    warnings.warn("The password_reset_done() view is superseded by the "
                  "class-based PasswordResetDoneView().",
                  RemovedInDjango21Warning, stacklevel=2)
    context = {
        'title': _('Password reset sent'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='accounts/registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    Check the hash in a password reset link and present a form for entering a
    new password.
    """
    warnings.warn("The password_reset_confirm() view is superseded by the "
                  "class-based PasswordResetConfirmView().",
                  RemovedInDjango21Warning, stacklevel=2)
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('passwords:password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def password_reset_complete(request,
                            template_name='accounts/registration/password_reset_complete.html',
                            extra_context=None):
    warnings.warn("The password_reset_complete() view is superseded by the "
                  "class-based PasswordResetCompleteView().",
                  RemovedInDjango21Warning, stacklevel=2)
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': _('Password reset complete'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)





@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request,
                    template_name='accounts/registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    extra_context=None):
    warnings.warn("The password_change() view is superseded by the "
                  "class-based PasswordChangeView().",
                  RemovedInDjango21Warning, stacklevel=2)
    if post_change_redirect is None:
        post_change_redirect = reverse('passwords:password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one.
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': _('Password change'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
def password_change_done(request,
                         template_name='accounts/registration/password_change_done.html',
                         extra_context=None):
    warnings.warn("The password_change_done() view is superseded by the "
                  "class-based PasswordChangeDoneView().",
                  RemovedInDjango21Warning, stacklevel=2)
    context = {
        'title': _('Password change successful'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)