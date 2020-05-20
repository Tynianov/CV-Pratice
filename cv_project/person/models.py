from django.db import models


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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


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
