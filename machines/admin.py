from django.contrib import admin
from symantec.machines.models import *
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

class ReadOnlyTextWidget(forms.Widget):
    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            value = self.initial
        return mark_safe("<textarea class=\"vLargeTextField\" rows=\"10\" readonly=\"readonly\" %s>%s</textarea>" % (flatatt(final_attrs), value or ''))

    def _has_changed(self, initial, data):
        return False

class ReadOnlyTextField(forms.FileField):
    widget = ReadOnlyTextWidget
    def __init__(self, widget=None, label=None, initial=None, help_text=None):
        forms.Field.__init__(self, label=label, initial=initial,
            help_text=help_text, widget=widget)

    def clean(self, value, initial):
        self.widget.initial = initial
        return initial

class MachineModelForm( forms.ModelForm ):
    info = ReadOnlyTextField()
    class Meta:
        model = Machine

class MachineAdmin(admin.ModelAdmin):
    list_display = ('address', 'name', 'user')
    form = MachineModelForm

admin.site.register(Machine, MachineAdmin)
