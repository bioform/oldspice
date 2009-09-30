from django import forms
from datetime import datetime
import ldap

class GeneralForm(forms.Form):
    textWidget=forms.TextInput(attrs={'class':'text ui-widget-content ui-corner-all'})
    textWidgetReadonly=forms.TextInput(attrs={'class':'text ui-widget-content ui-corner-all','readonly':'readonly'})

    name = forms.CharField(label='Configuration Name:', required=True, widget=textWidgetReadonly)
    desc = forms.CharField(label='Description:', required=False, widget=textWidget)
    updated_at = forms.CharField(label='Last Modified On:', required=False, widget=textWidgetReadonly)
    configDN = forms.CharField(widget=forms.HiddenInput())


def update_config(l, config, form):
    time_str = datetime.now().strftime('%Y%m%d%H%M%S')
    mod_attrs = [( ldap.MOD_REPLACE, 'dlmName', form.data['name'].encode("utf-8") ),
                 ( ldap.MOD_REPLACE, 'dlmDescription', form.data['desc'].encode("utf-8") ),
                 ( ldap.MOD_REPLACE, 'symcSequenceRevision', time_str )
                ]
    l.modify_s(config.dn, mod_attrs)