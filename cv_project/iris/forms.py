import os

import cv2

from django import forms

from .models import PersonIris, Person


class PersonIrisForm(forms.ModelForm):
    class Meta:
        model = PersonIris
        fields = "__all__"

    def clean_image(self):
        file = self.cleaned_data['image']
        filename, ext = os.path.splitext(file.name)

        # TODO test with png, jpg
        if ext != '.bmp':
            raise forms.ValidationError('Only .bmp image allowed')

        return file

    def save(self, commit=True):
        instance = super().save(commit)
        try:
            image = cv2.imread(instance.image.path)
            self.instance.encoding = image.dumps()
        except Exception as e:
            print(e)
        finally:
            return super().save(commit)
