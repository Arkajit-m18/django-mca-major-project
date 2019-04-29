from django.conf import settings

import requests, json, hashlib, re

MAILCHIMP_API_KEY = getattr(settings, 'MAILCHIMP_API_KEY', None)
MAILCHIMP_DATA_CENTER = getattr(settings, 'MAILCHIMP_DATA_CENTER', None)
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, 'MAILCHIMP_EMAIL_LIST_ID', None)

def get_subscriber_hash(member_email):
    # check email
    member_email = member_email.lower().encode()
    m = hashlib.md5(member_email)
    return m.hexdigest()

def check_email(email):
    if not re.match(r'.+.@.+\..+', email):
        raise ValueError("Email is not valid")
    return email

class Mailchimp(object):
    def __init__(self, *args, **kwargs):
        super(Mailchimp, self).__init__(*args, **kwargs)
        self.key = MAILCHIMP_API_KEY
        self.api_url = f'https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0'
        self.list_id = MAILCHIMP_EMAIL_LIST_ID
        self.list_endpoint = f'{self.api_url}/lists/{self.list_id}/members'

    def get_members_endpoint(self):
        return self.list_endpoint

    def change_subscription_status(self, email, status = 'unsubscribed', check_status = False):
        check_email(email)
        hashed_email = get_subscriber_hash(email)
        endpoint = self.get_members_endpoint() + f'/{hashed_email}'
        data = {
            'status': self.check_valid_status(status)
        }
        # if check_status:
        #     return requests.get(endpoint, auth = ("", self.key)).json()
        r = requests.put(endpoint, auth = ("", self.key), data = json.dumps(data))
        return r.status_code, r.json()

    def check_subscription_status(self, email):
        hashed_email = get_subscriber_hash(email)
        endpoint = self.get_members_endpoint() + f'/{hashed_email}'
        r = requests.get(endpoint, auth = ("", self.key))
        return r.status_code, r.json()

    def check_valid_status(self, status):
        choices = ['subscribed', 'unsubscribed', 'cleaned', 'pending']
        if status not in choices:
            raise ValueError("Not a valid choice for email status")
        return status

    def add_email(self, email):
        # status = 'subscribed'
        # self.check_valid_status(status)
        # endpoint = self.get_members_endpoint()
        # data = {
        #     'email_address': email,
        #     'status': status
        # }
        # r = requests.post(endpoint, auth = ("", self.key), data = json.dumps(data))
        # return r.json()
        return self.change_subscription_status(email, status = 'subscribed')

    def unsubscribe(self, email):
        return self.change_subscription_status(email, status = 'unsubscribed')

    def subscribe(self, email):
        return self.change_subscription_status(email, status = 'subscribed')

    def pending(self, email):
        return self.change_subscription_status(email, status = 'pending')
