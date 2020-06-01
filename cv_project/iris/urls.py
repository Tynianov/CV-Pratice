from django.urls import path

from iris.views import IrisRecognizeAPIView

urlpatterns = [
    path('recognize/', IrisRecognizeAPIView.as_view()),
]
