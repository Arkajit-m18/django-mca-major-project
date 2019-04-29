from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.http import Http404
from django.contrib.auth import get_user_model
from django.conf import settings

from braces.views import SelectRelatedMixin

from . import models, forms

User = get_user_model()

# Create your views here.
class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ('user', 'group')

class UserPosts(generic.ListView):
    model = models.Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(email__iexact = self.kwargs.get('email'))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context
    
class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ('user', 'group')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__email__iexact = self.kwargs.get('email'))

class PostCommentDetails(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    template_name = 'posts/post_comment_detail.html'
    select_related = ('user', 'group')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__email__iexact = self.kwargs.get('email'))

class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('message', 'group')
    model = models.Post

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

class UpdatePost(LoginRequiredMixin,SelectRelatedMixin, generic.UpdateView):
    model = models.Post
    select_related = ('user', 'group')
    fields = ('message', 'group')

class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ('user', 'group')
    success_url = reverse_lazy('posts:all')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__id = self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Post Deleted')
        return super().delete(*args, **kwargs)

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(models.Post, pk = pk)
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit = False)
            comment.post = post
            comment.author = request.user.email
            comment.save()
            return redirect('posts:single_comments', email = post.user.email, pk = post.pk)
        else:
            print(form.errors)
    else:
        form = forms.CommentForm()
    return render(request, 'posts/comment_form.html', {'form': form})

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(models.Comment, pk = pk)
    form = forms.CommentForm(instance = comment)
    if request.method == 'POST':
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            # comment.author = form.cleaned_data['author']
            comment.text = form.cleaned_data['text']
            comment.save()
            return redirect('posts:single_comments', email = comment.post.user.email, pk = comment.post.pk)
        else:
            print(form.errors)
    return render(request, 'posts/comment_form.html', {'form': form})

@login_required
def approve_comment(request, pk):
    comment = get_object_or_404(models.Comment, pk = pk)
    comment.approve()
    return redirect('posts:single_comments', email = comment.post.user.email, pk = comment.post.pk)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(models.Comment, pk = pk)
    post_pk = comment.post.pk
    post_username = comment.post.user.email
    comment.delete()
    return redirect('posts:single_comments', email = post_username, pk = post_pk)
