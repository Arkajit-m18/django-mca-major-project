from django. urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostList.as_view(), name = 'all'),
    path('new/', views.CreatePost.as_view(), name = 'create'),
    path('by/<str:email>/', views.UserPosts.as_view(), name = 'for_user'),
    path('by/<str:email>/<int:pk>/', views.PostDetail.as_view(), name = 'single'),
    path('by/<str:email>/<int:pk>/comments/', views.PostCommentDetails.as_view(), name = 'single_comments'),
    path('delete/<int:pk>/', views.DeletePost.as_view(), name = 'delete'),
    path('edit/<int:pk>/', views.UpdatePost.as_view(), name = 'edit'),
    path('comment/to/post/<int:pk>/', views.add_comment_to_post, name = 'comment'),
    path('comment/edit/<int:pk>/', views.edit_comment, name = 'edit_comment'),
    path('comment/approve/<int:pk>/', views.approve_comment, name = 'approve_comment'),
    path('comment/delete/<int:pk>', views.delete_comment, name = 'delete_comment'),
]