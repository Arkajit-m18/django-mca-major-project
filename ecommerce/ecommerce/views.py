from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from . import forms


def home_page(request):
    context = {
        'title': 'Easy Commerce',
        'content': 'Welcome to Easy Commerce!',
        'tag': 'Buying products were never easier!'
    }
    return render(request, 'home_page.html', context)

def about_page(request):
    context = {
        'title': 'About',
        'content': '',
        'tag': '''
            Never doubt before buying products again.
            Discuss & Chat with your peers.
            Post about any queries or ask someone of help.
            Never regret again!
        '''
    }
    return render(request, 'home_page.html', context)

def contacts_page(request):
    form = forms.ContactForm(request.POST or None)
    context = {
        'title': 'Contacts',
        'form': form
    }
    if form.is_valid():
        print(form.cleaned_data.get('fullname'))
        print(form.cleaned_data.get('email'))
        print(form.cleaned_data.get('content'))
        if request.is_ajax():
            return JsonResponse({'message': 'Thank you for your submission'})
    if form.errors:
        errorData = form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errorData, status = 400, content_type = 'application/json')

    return render(request, 'contact/view.html', context)

