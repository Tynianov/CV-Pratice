import os

import cv2

from django import forms
from django.conf import settings

from iris.iris_recognition.recognition import encode_photo
from .models import PersonIris, Person


class PersonIrisForm(forms.ModelForm):
    class Meta:
        model = PersonIris
        fields = "__all__"

    def clean_image(self):
        file = self.cleaned_data['image']
        filename, ext = os.path.splitext(file.name)

        # TODO test with png, jpg
        if ext != settings.IRIS_EXTENSION:
            raise forms.ValidationError('Only {} image allowed'.format(settings.IRIS_EXTENSION))

        return file

    def save(self, commit=True):
        instance = super().save(commit)
        try:
            image = cv2.imread(instance.image.path)
            code, mask = encode_photo(image)
            self.instance.encoding = code.dumps()
            self.instance.mask = mask.dumps()
        except Exception as e:
            print(e)
        finally:
            return super().save(commit)
