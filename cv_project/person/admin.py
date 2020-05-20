from django.contrib import admin

from iris.admin import PersonIrisInline
from .models import Person, PersonImage
from .froms import PersonImageForm


class PersonImageInline(admin.TabularInline):
    model = PersonImage
    form = PersonImageForm


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "birthday"]
    inlines = [PersonImageInline, PersonIrisInline]
