from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from . import forms


def home_page(request):
    context = {
        'title': 'T H E B O O K S H O P',
        'content': 'Welcome to The Bookshop!',
        'tag': 'Buying books were never easier!'
    }
    return render(request, 'home_page.html', context)

def about_page(request):
    context = {
        'title': 'About',
        'content': 'Get reading!!',
        'tag': '''
            Never doubt before buying books again.
            Discuss & Chat with your peers.
            Post about any queries or ask someone of help.
            Never be in doubt again!
        '''
    }
    return render(request, 'about_page.html', context)

def contacts_page(request):
    form = forms.ContactForm(request.POST or None)
    context = {
        'title': 'Contacts',
        'form': form
    }
    if form.is_valid():
        if request.is_ajax():
            return JsonResponse({'message': 'Thank you for your submission'})
    if form.errors:
        errorData = form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errorData, status = 400, content_type = 'application/json')

    return render(request, 'contact/view.html', context)

