from django.contrib import admin

from .models import Person, PersonImage


class PersonImageInline(admin.TabularInline):
    model = PersonImage


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "birthday"]
    inlines = [PersonImageInline]
