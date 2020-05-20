import os

from django.conf import settings
from django.db import models

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


class PersonIrisCompare(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='iris_stat')
    compare_with = models.ForeignKey(PersonIris, on_delete=models.CASCADE, related_name='iris_stat')
    percentage = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['percentage']
