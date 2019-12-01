from django.urls import path
from . import views


urlpatterns = [
   path('', views.homepage, name="home-page"),
   path('search/', views.search, name="make-schedule"),
]