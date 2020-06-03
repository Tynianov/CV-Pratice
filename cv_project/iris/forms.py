import base64
import pickle

import cv2

from django import forms

from iris.iris_recognition.recognition import encode_photo
from .models import PersonIris


class PersonIrisForm(forms.ModelForm):
    class Meta:
        model = PersonIris
        fields = "__all__"

    def encode_np_array(self, array):
        np_bytes = pickle.dumps(array)
        np_base64 = base64.b64encode(np_bytes)
        return np_base64

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image.name.endswhit('.bmp'):
            raise forms.ValidationError('Bmp image required')

        return image

    def save(self, commit=True):
        instance = super().save(commit)
        try:
            image = cv2.imread(instance.image.path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            code, mask = encode_photo(rgb)

            self.instance.encoding = self.encode_np_array(code)
            self.instance.mask = self.encode_np_array(mask)
        except Exception as e:
            print(e)
        finally:
            return super().save(commit)
