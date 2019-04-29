from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login

from .models import EmailActivation, GuestEmail
from .signals import user_logged_in

User = get_user_model()

class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label = 'Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Password confirmation', widget = forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit = True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit = False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserDetailUpdateForm(forms.ModelForm):
    full_name = forms.CharField(label = 'Name', required = False)
    class Meta:
        model = User
        fields = ['full_name',]

class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class LoginForm(forms.Form):
    email = forms.EmailField(widget = forms.EmailInput(attrs = {
        'class': 'form-control',
        'placeholder': 'Your username'
    }), label = 'Email')
    password = forms.CharField(widget = forms.PasswordInput(attrs = {
        'class': 'form-control',
        'placeholder': 'Your Password'
    }))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        return super().__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get('email')
        password = data.get('password')

        qs = User.objects.filter(email = email)
        if qs.exists():
            # User email is registered
            not_active = qs.filter(is_active = False)
            if not_active.exists():
                # check email 
                resend_link = reverse('accounts:resend-activation')
                reconfirm_msg = f"""
                    <a href="{resend_link}">Resend Confirmation Email</a>
                """
                confirm_email = EmailActivation.objects.filter(email = email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    msg1 = 'Activation email already sent. Check your email. ' + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg1))
                email_confirm_qs = EmailActivation.objects.email_exists(email = email)
                email_confirm_exists = email_confirm_qs.exists()
                if email_confirm_exists:
                    msg2 = 'You need to confirm your email. ' + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg2))
                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError('This user is inactive.')

        user = authenticate(username = email, password = password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")
        login(request, user)
        self.user = user
        user_logged_in.send(sender = user.__class__, instance = user, request = request)
        try:
            del request.session['guest_email_id']
        except:
            pass
        return data


    # def form_valid(self, form):
    #     next_ = self.request.GET.get('next')
    #     next_post = self.request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #     email = form.cleaned_data.get('email')
    #     password = form.cleaned_data.get('password')
    #     user = authenticate(username = email, password = password)
    #     if user:
    #         if not user.is_active:
    #             messages.error(self.request, "This user is inactive")
    #             return super(LoginView, self).form_invalid(form)
    #         login(self.request, user)
    #         user_logged_in.send(sender = user.__class__, instance = user, request = self.request)
    #         try:
    #             del self.request.session['guest_email_id']
    #         except:
    #             pass
    #         if is_safe_url(redirect_path, self.request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect('/')
    #     return super(LoginView, self).form_invalid(form)

class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label = 'Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Password confirmation', widget = forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit = True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit = False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False # send confirmation email
        if commit:
            user.save()
        return user

# class GuestForm(forms.Form):
#     email = forms.EmailField(widget = forms.EmailInput(attrs = {
#         'class': 'form-control',
#         'placeholder': 'Your email'
#     }))

class GuestForm(forms.ModelForm):
    class Meta:
        model = GuestEmail
        fields = ['email',]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        return super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit = True):
        obj = super(GuestForm, self).save(commit = False)
        if commit:
            obj.save()
            self.request.session['guest_email_id'] = obj.id
        return obj

class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email = email)
        if not qs.exists():
            register_link = reverse('register')
            msg = f"""
                Your email does not exist. Do you want to <a href="{register_link}">register</a>?
            """
            raise forms.ValidationError(mark_safe(msg))
        return email

# class RegisterForm(forms.Form):
#     username = forms.CharField(widget = forms.TextInput(attrs = {
#         'class': 'form-control',
#         'placeholder': 'Your username'
#     }))
#     email = forms.EmailField(widget = forms.EmailInput(attrs = {
#         'class': 'form-control',
#         'placeholder': 'Your email'
#     }))
#     password = forms.CharField(widget = forms.PasswordInput(attrs = {
#         'class': 'form-control',
#         'placeholder': 'Your password'
#     }))
#     password2 = forms.CharField(widget = forms.PasswordInput(attrs = {
#         'class': 'form-control',
#         'placeholder': 'Confirm password'
#     }), label = 'Confirm Password')

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         qs = User.objects.filter(username = username)
#         if qs.exists():
#             raise forms.ValidationError('Username is already taken!')
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         qs = User.objects.filter(email = email)
#         if qs.exists():
#             raise forms.ValidationError('Email is already taken!')
#         return email

#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password != password2:
#             raise forms.ValidationError('Passwords must match!')
#         return data
