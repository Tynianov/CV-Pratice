import numpy as np
from io import BytesIO
from PIL import Image

from django.db import models

from person.models import Person


class PersonFingerprint(models.Model):
    fingerprint = models.ImageField(upload_to="fingerprints")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="fingerprints")
    encoding = models.BinaryField(null=True, blank=True)

    __original_fingerprint = None

    def __init__(self, *args, **kwargs):
        super(PersonFingerprint, self).__init__(*args, **kwargs)
        self.__original_fingerprint = self.fingerprint

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.fingerprint and not self.encoding or self.fingerprint != self.__original_fingerprint:
            image = Image.open(self.fingerprint.path)
            image_array = np.array(image)
            io = BytesIO()
            np.save(io, image_array)
            io.seek(0)
            self.encoding = io.read()
            super().save(*args, **kwargs)
            self.__original_fingerprint = self.fingerprint
