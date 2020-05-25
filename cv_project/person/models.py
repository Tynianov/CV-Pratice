import cv2
import numpy as np
import face_recognition
from io import BytesIO

from django.db import models


class Person(models.Model):

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(default="", blank=True)
    birthday = models.DateTimeField(default="", null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PersonImage(models.Model):
    image = models.ImageField(upload_to="images")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="images")
    encoding = models.BinaryField(null=True, blank=True)

    __original_image = None

    def __init__(self, *args, **kwargs):
        super(PersonImage, self).__init__(*args, **kwargs)
        self.__original_image = self.image

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.encoding or self.image != self.__original_image:
            image = cv2.imread(self.image.path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)
            io = BytesIO()
            np.save(io, encodings)
            io.seek(0)
            self.encoding = io.read()
            super().save(*args, **kwargs)
            self.__original_image = self.image
