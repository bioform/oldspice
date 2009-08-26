from django.contrib import admin
from symantec.machines.models import *
from django.contrib.auth.models import User

class MachineAdmin(admin.ModelAdmin):
    list_display = ('address', 'name', 'user')

admin.site.register(Machine, MachineAdmin)
