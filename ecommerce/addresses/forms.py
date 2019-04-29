from django import forms

from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('billing_profile', 'address_type')

class AddressEditForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('billing_profile',)