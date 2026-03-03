from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('@vite/client', views.vite_client_stub, name='vite_client_stub'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('campaign/new/', views.campaign_new, name='campaign_new'),
    path('campaign/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
]
