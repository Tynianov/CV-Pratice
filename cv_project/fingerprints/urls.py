from django.urls import path

from . import views

urlpatterns = [
    path('find-match', views.FingerPrintRecognitionView.as_view(), name='find-fingerprint-match'),
]
