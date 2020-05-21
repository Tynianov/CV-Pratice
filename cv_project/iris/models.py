import os

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

    def compare_iris(self, image, code, mask):
        person_code = np.frombuffer(self.encoding, dtype=np.int8)
        person_mask = np.frombuffer(self.mask, dtype=np.int8)
        percentage = 1 - compare_codes(person_code, code, person_mask, mask)

        if percentage >= 0.5:
            PersonIrisCompare.objects.create(person=self.person, compare_with=image, percentage=percentage)


def handler_compare_path(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "iris/compare/%s%s" % (instance.person.username + name, settings.IRIS_EXTENSION)
    real_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.isfile(real_path):
        os.unlink(real_path)
    return filename


class PersonIrisCompare(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='iris_stat')
    compare_with = models.ImageField(upload_to=handler_compare_path)
    percentage = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['percentage']
