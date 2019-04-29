from django.db import models

from billing.models import BillingProfile

ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)

# Create your models here.
class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete = models.CASCADE)
    address_type = models.CharField(max_length = 50, choices = ADDRESS_TYPES)
    address_line_1 = models.CharField(max_length = 256)
    address_line_2 = models.CharField(max_length = 256, null = True, blank = True)
    city = models.CharField(max_length = 90)
    state = models.CharField(max_length = 90)
    country = models.CharField(max_length = 90, default = 'India')
    postal_code = models.CharField(max_length = 20)

    def __str__(self):
        return str(self.billing_profile)

    def get_address(self):
        return "{line1}\n{line2}\n{city}\n{state} {postal}\n{country}".format(
            line1 = self.address_line_1,
            line2 = self.address_line_2 or '',
            city = self.city,
            state = self.state,
            postal = self.postal_code,
            country = self.country
            )