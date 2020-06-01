from django.contrib import admin

# Register your models here.
from iris.forms import PersonIrisForm
from iris.models import PersonIris


class PersonIrisInline(admin.TabularInline):
    model = PersonIris
    form = PersonIrisForm
    extra = 1
