from django.urls import path

from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.RoomList.as_view(extra_context = {'site_path': 'rooms'}), name = 'all'),
    path('room/<slug:slug>/', views.RoomDetail.as_view(), name = 'single'),
    path('new/', views.CreateRoom.as_view(extra_context = {'site_path': 'new'}), name = 'new'),
    path('room/edit/<slug:slug>/', views.UpdateRoom.as_view(), name = 'edit'),
    path('room/delete/<slug:slug>/', views.DeleteRoom.as_view(), name = 'delete'),
    path('room/join/<slug:slug>/', views.JoinRoom.as_view(), name = 'join'),
    path('room/leave/<slug:slug>/', views.LeaveRoom.as_view(), name = 'leave')
]