# chat/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.views import generic
import json

from rooms.models import Room

def home(request):
    return render(request, 'chat/home.html', {})

@login_required
def room(request, room_name):
    room = Room.objects.filter(name = room_name)[0]
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username': mark_safe(json.dumps(request.user.email)),
        'room_name': room_name,
        'user_author': request.user.email,
        'room': room
    })