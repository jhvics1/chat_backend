from django.urls import path

from . import views

urlpatterns = [
    path('chats/', views.ChatSessionView.as_view()),
    path('chats/<uri>/', views.ChatSessionJoinView.as_view()),
    path('chats/<uri>/messages/', views.ChatSessionMessageView.as_view()),
]