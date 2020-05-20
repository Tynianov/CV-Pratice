from django.db import models

from iris.models import PersonIrisCompare


class PersonManager(models.Manager):
    def iris(self, *args, **kwargs):
        kwargs['iris__isnull'] = False
        return super().filter(*args, **kwargs).distinct()

    def face(self, *args, **kwargs):
        kwargs['images__isnull'] = False
        return super().filter(*args, **kwargs).distinct()


class Person(models.Model):
    first_name = models.CharField(
        max_length=128
    )
    last_name = models.CharField(
        max_length=128
    )
    email = models.EmailField(
        default='', blank=True
    )
    birthday = models.DateTimeField(
        default='', null=True
    )

    objects = PersonManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def compare_iris(self, image, code, mask):
        for iris in self.iris.all():
            iris.compare_iris(image, code, mask)

        PersonIrisCompare.objects.filter(person=self).delete()

        return PersonIrisCompare.objects.filter(person=self).first()


class PersonImage(models.Model):
    image = models.ImageField(
        upload_to='images'
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='images'
    )
    encoding = models.CharField(
        max_length=2048,
        default='',
        null=True,
        blank=True
    )
