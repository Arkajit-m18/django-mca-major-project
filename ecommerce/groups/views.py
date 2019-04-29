from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views import generic

from braces.views import SelectRelatedMixin

from .models import Group, GroupMember

# Create your views here.
class CreateGroup(LoginRequiredMixin, generic.CreateView):
    fields = ('name', 'description')
    model = Group

class UpdateGroup(LoginRequiredMixin, generic.UpdateView):
    fields = ('name', 'description')
    model = Group

    def form_valid(self, form):
        self.object = form.save(commit = False)
        GroupMember.objects.filter(group = self.object).delete()
        membership = GroupMember()
        membership.group = self.object
        membership.user = self.request.user
        membership.save()
        return super().form_valid(form)

class SingleGroup(generic.DetailView):
    model = Group

class ListGroup(generic.ListView):
    model = Group

class JoinGroup(LoginRequiredMixin,  generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs = {'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug = self.kwargs.get('slug'))
        try:
            GroupMember.objects.create(user = self.request.user, group = group)
        except:
            messages.warning(self.request, 'Warning! already a member')
        else:
            messages.success(self.request, 'You are now a member!')
        return super().get(request, *args, **kwargs)

class LeaveGroup(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs = {'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        try:
            membership = GroupMember.objects.filter(user = self.request.user, group__slug = self.kwargs.get('slug')).get()
        except GroupMember.DoesNotExist:
            messages.warning(self.request, 'Sorry you are not in this group!')
        else:
            membership.delete()
            messages.success(self.request, 'You have left the group!')
        return super().get(request, *args, **kwargs)

class DeleteGroup(LoginRequiredMixin, generic.DeleteView):
    model = Group
    success_url = reverse_lazy('groups:all')