from django.http import HttpResponse
from django.urls import path, include
from . import views, chatbot_views
urlpatterns = [
    path('', views.index, name='index'),
    path('chatbot-api/', chatbot_views.chatbot_api, name='chatbot_api'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]

