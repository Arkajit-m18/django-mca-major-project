from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.http import is_safe_url
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import FormMixin

from . import forms
from .models import GuestEmail, EmailActivation
from django.utils.safestring import mark_safe
from ecommerce.mixins import NextUrlMixin, RequestFormAttachMixin

# Create your views here.

class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = forms.LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    default_next = '/'

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)

    # def get_form_kwargs(self):
    #     kwargs = super(LoginView, self).get_form_kwargs()
    #     kwargs['request'] = self.request
    #     return kwargs

    # def get_next_url(self):
    #     next_ = self.request.GET.get('next')
    #     next_post = self.request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #     if is_safe_url(redirect_path, self.request.get_host()):
    #         return redirect_path
    #     else:
    #         return '/'


# def login_page(request):
#     form = forms.LoginForm(request.POST or None)
#     context = {'form': form}
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(username = username, password = password)
#         if user:
#             login(request, user)
#             try:
#                 del request.session['guest_email_id']
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect('/')
#         else:
#             print('Error')
#     return render(request, 'accounts/login.html', context)

class RegisterView(CreateView):
    form_class = forms.RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'

# User = get_user_model()
# def register_page(request):
#     form = forms.RegisterForm(request.POST or None)
#     context = {'form': form}
#     if form.is_valid():
#         form.save()
#         # username = form.cleaned_data.get('username')
#         # email = form.cleaned_data.get('email')
#         # password = form.cleaned_data.get('password')
#         # new_user = User.objects.create_user(username, email, password)
#     return render(request, 'accounts/register.html', context)

# def guest_register_view(request):
#     form = forms.GuestForm(request.POST or None)
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         email = form.cleaned_data.get('email')
#         new_guest_email = GuestEmail.objects.create(email = email)
#         request.session['guest_email_id'] = new_guest_email.id
#         if is_safe_url(redirect_path, request.get_host()):
#             return redirect(redirect_path)
#         else:
#             return redirect('/register/')
#     return redirect('/register/')

class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = forms.UserDetailUpdateForm
    template_name = 'accounts/detail_update_view.html'

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Change Your Details'
        return context
    
    def get_success_url(self):
        return reverse('accounts:accounts_home')


class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = forms.GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)

    # def form_valid(self, form):
    #     email = form.cleaned_data.get('email')
    #     new_guest_email = GuestEmail.objects.create(email = email)
    #     self.request.session['guest_email_id'] = new_guest_email.id
    #     return redirect(self.get_next_url())

# @login_required
# def account_home_view(request):
#     return(request, 'accounts/home.html', {})

# class LoginRequiredMixin(object):
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         return super(AccountHomeView, self).dispatch(request, *args, **kwargs)

class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'
    def get_object(self, queryset=None):
        return self.request.user

class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = forms.ReactivateEmailForm
    key = None
    def get(self, request, key = None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact = key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, 'Your email has been confirmed. Continue login.')
                return redirect('login')
            else:
                activated_qs = qs.filter(activated = True)
                if activated_qs.exists():
                    reset_link = reverse('password_reset')
                    msg = f"""
                        Your email has already been confirmed. Do you want to <a href="{reset_link}">reset your password</a>?
                    """
                    messages.success(request, mark_safe(msg))
                    return redirect('login')
        context = {'form': self.get_form(), 'key': key}
        return render(request, 'registration/activation_error.html', context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = f"""
                Activation link sent. Please check your email.
            """
        email = form.cleaned_data.get('email')
        obj = EmailActivation.objects.email_exists(email = email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user = user, email = email)
        new_activation.send_activation()
        messages.success(self.request, msg)
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation_error.html', context)