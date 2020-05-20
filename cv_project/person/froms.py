import face_recognition
import cv2
import numpy as np

from django import forms

from .models import PersonImage, Person


class PersonImageForm(forms.ModelForm):
    class Meta:
        model = PersonImage
        fields = "__all__"

    def clean(self):
        clean_data = super().clean()
        if 'image' in self.changed_data:
            image = cv2.imread(clean_data['image'], 1)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            print(image)
            print(rgb)
            # image = clean_data['image'].read()
            # np_arr = np.fromstring(image, np.uint8)
            # img_np = cv2.imdecode(np_arr, cv2.CV_LOAD_IMAGE_COLOR)
            # print('hello')
            # print(clean_data)

        return clean_data
