import face_recognition
import cv2
import numpy as np

from django import forms

from .models import PersonImage, Person


class PersonImageForm(forms.ModelForm):
    class Meta:
        model = PersonImage
        fields = "__all__"
