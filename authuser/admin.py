from django.contrib.auth.admin import UserAdmin
from django import forms
from symantec.authuser.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext, ugettext_lazy as _

#admin.site.unregister(User)
admin.site.unregister(User)

# Set it up so we can edit a user's sprockets inline in the admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile

class MyUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

# re-register the User with the extended admin options
admin.site.register(User, MyUserAdmin)


