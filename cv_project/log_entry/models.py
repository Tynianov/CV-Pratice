from django.db import models

from person.models import Person


class LogEntry(models.Model):
    FACE = 'face'
    FINGERPRINT = 'fingerprint'
    IRIS = 'iris'

    AUTHORIZATION_TYPES_CHOICES = (
        (FACE, 'Face'),
        (FINGERPRINT, 'Fingerprint'),
        (IRIS, 'Iris')
    )

    authorization_type = models.CharField(max_length=11, choices=AUTHORIZATION_TYPES_CHOICES, default=FACE)
    timestamp = models.DateTimeField(auto_now_add=True)
    result = models.BooleanField(default=False)
    image = models.ImageField(upload_to='log_entries')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    percentage = models.FloatField(blank=True, null=True)
