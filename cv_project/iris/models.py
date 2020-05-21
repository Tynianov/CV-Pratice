import base64
import os
import pickle

import numpy as np

from django.conf import settings
from django.db import models

from iris.iris_recognition.recognition import encode_photo, compare_codes
from person.models import Person


def handler_upload(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "iris/%s%s" % (name, '.bmp')
    real_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.isfile(real_path):
        os.unlink(real_path)
    return filename


class PersonIris(models.Model):
    image = models.ImageField(upload_to=handler_upload)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='iris')
    encoding = models.BinaryField(null=True, blank=True)
    mask = models.BinaryField(null=True, blank=True)

    def decode_np_array(self, bytes):
        np_bytes = base64.b64decode(bytes)
        np_array = pickle.loads(np_bytes)
        return np_array

    def compare_iris(self, code, mask):
        try:
            person_code = self.decode_np_array(self.encoding)
            person_mask = self.decode_np_array(self.mask)

            percentage = 1 - compare_codes(person_code, code, person_mask, mask)
            return {'percentage': percentage, 'person': {
                'first_name': self.person.first_name,
                'last_name': self.person.last_name

            }}
        except Exception as e:
            print(e)


def handler_compare_path(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "iris/compare/%s_%s%s" % (instance.person.pk, name, settings.IRIS_EXTENSION)
    real_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.isfile(real_path):
        os.unlink(real_path)
    return filename
