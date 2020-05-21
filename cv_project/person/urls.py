from django.urls import path

from . import views

urlpatterns = [
    path('find-match', views.CompareFacesView.as_view(), name='find-match'),
]