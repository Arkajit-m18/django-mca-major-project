from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q

from ecommerce.utils import unique_key_generator

from random import randint
from datetime import timedelta

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, full_name = None, password = None, is_staff = False, is_admin = False, is_active = True):
        if not email:
            raise ValueError("Users must have an email")
        if not password:
            raise ValueError("Users must have a password")
        # if not full_name:
        #     raise ValueError("Users must have a full name")
        user_obj = self.model(
            email = self.normalize_email(email),
            full_name = full_name,
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using = self._db)
        return user_obj

    def create_staffuser(self, email, full_name = None, password = None):
        user = self.create_user(
            email = email,
            full_name = full_name,
            password = password,
            is_staff = True
        )
        return user
    
    def create_superuser(self, email, full_name = None, password = None):
        user = self.create_user(
            email = email,
            full_name = full_name,
            password = password,
            is_staff = True,
            is_admin = True
        )
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique = True, max_length = 255)
    full_name = models.CharField(max_length = 255, blank = True, null = True)
    active = models.BooleanField(default = True)
    is_active = models.BooleanField(default = True)
    staff = models.BooleanField(default = False)
    admin = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add = True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # username and password are required by default

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj = None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff
    
    @property
    def is_admin(self):
        return self.admin
    
    # @property
    # def is_active(self):
    #     return self.active

class EmailActivationQuerySet(models.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days = DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(activated = False, force_expired = False).filter(timestamp__gt = start_range, timestamp__lte = end_range)

class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using = self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        return self.get_queryset().filter(Q(email = email) | Q(user__email = email)).filter(activated = False)

class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    email = models.EmailField()
    key = models.CharField(max_length = 120, blank = True, null = True)
    activated = models.BooleanField(default = False)
    force_expired = models.BooleanField(default = False)
    expires = models.IntegerField(default = 7)
    timestamp = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk = self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            # pre activation user signal
            user = self.user
            user.is_active = True
            user.save()
            # post activation signal for user
            self.activated = True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.force_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', '127.0.0.1:8000')
                key_path = reverse('accounts:email_activate', kwargs = {'key': self.key})
                path = f'http://{base_url}{key_path}'
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template('registration/emails/verify.txt').render(context)
                html_ = get_template('registration/emails/verify.html').render(context)
                subject = 'One-click email verification'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]

                sent_mail = send_mail(
                    subject = subject,
                    message = txt_,
                    from_email = from_email,
                    recipient_list = recipient_list,
                    html_message = html_,
                    fail_silently = False 
                )
                return sent_mail
        return False

def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.force_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation, sender = EmailActivation)

def post_save_user_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user = instance, email = instance.email)
        obj.send_activation()

post_save.connect(post_save_user_created_receiver, sender = User)

class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default = True)
    updated = models.DateTimeField(auto_now = True)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.email