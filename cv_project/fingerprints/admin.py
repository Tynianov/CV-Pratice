from django.contrib import admin

from .models import PersonFingerprint


class PersonFingerprintsInline(admin.TabularInline):
    model = PersonFingerprint
