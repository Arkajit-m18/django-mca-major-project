from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.conf import settings
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.template.loader import get_template
from django.core.mail import send_mail

from carts.models import Cart
from ecommerce.utils import unique_order_id_generator
from billing.models import BillingProfile
from addresses.models import Address
from products.models import Product
from accounts.models import GuestEmail

import math, datetime

User = settings.AUTH_USER_MODEL

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)

class OrderQuerySet(models.QuerySet):
    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile = billing_profile)

    def not_created(self):
        return self.exclude(status = 'created')

    def by_status(self, status = 'shipped'):
        return self.filter(status = status)

    def by_date(self):
        now = timezone.now() # - datetime.timedelta(days = 7)
        return self.filter(updated__month__gte = now.month)

    def by_range(self, start_date, end_date = None):
        if end_date is None:
            return self.filter(updated__gte = start_date)
        return self.filter(updated__gte = start_date).filter(updated__lte = end_date)

    def by_weeks_range(self, weeks_ago = 1, number_of_weeks = 1):
        if number_of_weeks > weeks_ago:
            number_of_weeks = weeks_ago
        days_ago_start = weeks_ago * 7
        days_ago_end = days_ago_start - (number_of_weeks * 7)
        start_date = timezone.now() - datetime.timedelta(days = days_ago_start)
        end_date = timezone.now() - datetime.timedelta(days = days_ago_end)
        return self.by_range(start_date = start_date, end_date = end_date)

    def recent(self):
        return self.order_by('-updated', '-timestamp')

    def not_refunded(self):
        return self.exclude(status = 'refunded')

    def totals_data(self):
        return self.aggregate(Sum('total'), Avg('total'))

    def cart_data(self):
        return self.aggregate(Sum('cart__products__price'), Avg('cart__products__price'), Count('cart__products'))

    def get_sales_breakdown(self):
        recent = self.recent().not_refunded()
        recent_data = recent.totals_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.by_status(status = 'shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status = 'paid')
        paid_data = paid.totals_data()
        data = {
            'recent': recent,
            'recent_data': recent_data,
            'recent_cart_data': recent_cart_data,
            'shipped': shipped,
            'shipped_data': shipped_data,
            'paid': paid,
            'paid_data': paid_data,
        }
        return data

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using = self._db)

    def by_billing_profile(self, request):
        return self.get_queryset().by_billing_profile(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(cart = cart_obj, billing_profile = billing_profile, active = True, status = 'created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(cart = cart_obj, billing_profile = billing_profile)
            created = True
        return obj, created

# Create your models here.
class Order(models.Model):
    order_id = models.CharField(max_length = 120, blank = True)
    billing_profile = models.ForeignKey(BillingProfile, null = True, blank = True, on_delete = models.CASCADE)
    shipping_address = models.ForeignKey(Address, related_name = 'shipping_addresses', null = True, blank = True, on_delete = models.CASCADE)
    billing_address = models.ForeignKey(Address, related_name = 'billing_addresses', null = True, blank = True, on_delete = models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    status = models.CharField(max_length = 120, default = 'created', choices = ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default = 2.99, max_digits = 20, decimal_places = 2)
    total = models.DecimalField(default = 0.00, max_digits = 20, decimal_places = 2)
    active = models.BooleanField(default = True)
    timestamp = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.order_id

    def get_absolute_url(self):
        return reverse('orders:single-order', kwargs={'order_id': self.order_id})

    def get_shipping_status(self):
        if self.status == 'refunded':
            return 'Returned'
        elif self.status == 'shipped':
            return 'Shipped'
        return 'Shipping Soon'

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([cart_total, shipping_total])
        formatted_total = format(new_total, '.2f')
        self.total = formatted_total
        self.save()
        return new_total

    def check_done(self):
        shipping_address_required = not self.cart.is_digital
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True

        billing_profile = self.billing_profile
        # shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if billing_profile and shipping_done and billing_address and total > 0:
            return True
        return False

    def update_purchases(self):
        for product in self.cart.products.all():
            obj, created = ProductPurchase.objects.get_or_create(
                order_id = self.order_id,
                product = product,
                billing_profile = self.billing_profile
            )
            # obj.refunded = False
            # obj.save()
        return ProductPurchase.objects.filter(order_id = self.order_id).count()

    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = 'paid'
                self.save()
                self.update_purchases()
        return self.status

    def send_confirmation(self, request):
        email_recipient = None
        guest_email_id = request.session.get('guest_email_id')
        if request.user.is_authenticated:
            email_recipient = self.billing_profile.user.email
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id = guest_email_id)
            email_recipient = guest_email_obj.email
        base_url = getattr(settings, 'BASE_URL', '127.0.0.1:8000')
        context = {
            'order_id': self.order_id
        }
        txt_ = get_template('registration/emails/order_confirmation.txt').render(context)
        html_ = get_template('registration/emails/order_confirmation.html').render(context)
        subject = 'Order confirmation'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email_recipient]

        sent_mail = send_mail(
            subject = subject,
            message = txt_,
            from_email = from_email,
            recipient_list = recipient_list,
            html_message = html_,
            fail_silently = False 
        )
        if sent_mail:
            return sent_mail
        return False

def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart = instance.cart).exclude(billing_profile = instance.billing_profile)
    if qs.exists():
        qs.update(active = False)

pre_save.connect(pre_save_create_order_id, sender = Order)

def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart__id = cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total, sender = Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order, sender = Order)

class ProductPurchaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(refunded = False)

    def digital(self):
        return self.filter(product__is_digital = True)

    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile = billing_profile)

class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using = self._db)

    def all(self):
        return self.get_queryset().active()

    def digital(self):
        return self.get_queryset().active().digital()

    def by_billing_profile(self, request):
        return self.get_queryset().by_billing_profile(request)

    def products_by_id(self, request):
        qs = self.by_billing_profile(request).digital()
        product_ids = [obj.product.id for obj in qs]
        return product_ids

    def products_by_request(self, request):
        ids_ = self.products_by_id(request)
        product_qs = Product.objects.filter(id__in = ids_).distinct()
        return product_qs

class ProductPurchase(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete = models.CASCADE)
    order_id = models.CharField(max_length = 120)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    refunded = models.BooleanField(default = False)
    updated = models.DateTimeField(auto_now = True)
    timestamp = models.DateTimeField(auto_now_add = True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title