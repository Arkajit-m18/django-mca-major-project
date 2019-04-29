from django.shortcuts import render, redirect
from django.views.generic import UpdateView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from django.http import HttpResponse

from .forms import MarketingPreferenceForm
from .models import MarketingPreference
from .utils import Mailchimp
from .mixins import CsrfExemptMixin

MAILCHIMP_EMAIL_LIST_ID = getattr(settings, 'MAILCHIMP_EMAIL_LIST_ID', None)

# Create your views here.
class MarketingPreferenceView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    template_name = 'base/forms.html'
    success_url = '/settings/email'
    success_message = "Your email preferences have been successfully updated!"

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return redirect('/login/?next=/settings/email/')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user = user)
        return obj

    def get_context_data(self, **kwargs):
        context = super(MarketingPreferenceView, self).get_context_data(**kwargs)
        context['title'] = 'Update Email Preferences'
        return context

"""
POST METHOD
"root":
"type": "subscribe"
"fired_at": "2019-04-20 18:36:12"
"data":
"id": "8368e04cb3"
"email": "arkajit.18@gmail.com"
"email_type": "html"
"ip_opt": "103.242.188.239"
"web_id": "30367205"
"merges":
"EMAIL": "arkajit.18@gmail.com"
"FNAME": "Arkajit"
"LNAME": "Mondal"
"ADDRESS": ""
"PHONE": ""
"BIRTHDAY": ""
"list_id": "51e172c9dc"
"""

class MailchimpWebhookView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            hook_type = data.get('type')
            email = data.get('data[email]')
            response_status, response_data = Mailchimp().check_subscription_status(email)
            sub_status = response_data['status']
            is_subbed, is_mailchimp_subbed = None, None
            if sub_status == "subscribed":
                is_subbed, is_mailchimp_subbed = True, True
            elif sub_status == "unsubscribed":
                is_subbed, is_mailchimp_subbed = False, False
            if is_subbed is not None and is_mailchimp_subbed is not None:
                qs = MarketingPreference.objects.filter(user__email__iexact = email)
                if qs.exists():
                    qs.update(subscribed = is_subbed, mailchimp_subscribed = is_mailchimp_subbed, malchimp_msg = str(data))
        return HttpResponse("Thank you!", status = 200)  