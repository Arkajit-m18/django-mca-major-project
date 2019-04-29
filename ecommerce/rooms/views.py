from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy

from .models import Room, Membership

# Create your views here.
class RoomList(generic.ListView):
    model = Room

class RoomDetail(generic.DetailView):
    model = Room

class CreateRoom(LoginRequiredMixin, generic.CreateView):
    fields = ('name', 'description')
    model = Room

class UpdateRoom(LoginRequiredMixin, generic.UpdateView):
    fields = ('name', 'description')
    model = Room

    def form_valid(self, form):
        self.object = form.save(commit = False)
        Membership.objects.filter(room = self.object).delete()
        membership = Membership()
        membership.room = self.object
        membership.user = self.request.user
        membership.save()
        return super().form_valid(form)

class DeleteRoom(LoginRequiredMixin, generic.DeleteView):
    model = Room
    success_url = reverse_lazy('rooms:all')

class JoinRoom(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('rooms:single', kwargs = {'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        room = get_object_or_404(Room, slug = self.kwargs.get('slug'))
        try:
            Membership.objects.create(user = self.request.user, room = room)
        except:
            messages.warning(self.request, 'You are already a member!')
        else:
            messages.success(self.request, 'You are now a member!')
        return super().get(request, *args, **kwargs)

class LeaveRoom(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('rooms:single', kwargs = {'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        try:
            membership = Membership.objects.filter(user = self.request.user, room__slug = self.kwargs.get('slug'))
        except Membership.DoesNotExist:
            messages.warning(self.request, 'You are not a member of the room!')
        else:
            membership.delete()
            messages.success(self.request, 'You have left the room!')
        return super().get(request, *args, **kwargs)