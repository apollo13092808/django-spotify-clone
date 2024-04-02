from django.urls import path

from music import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.sign_in, name='login'),
    path('register/', views.sign_up, name='register'),
    path('logout/', views.sign_out, name='logout'),
    path('music/<str:pk>/', views.music, name='music'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
]
