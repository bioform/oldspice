from django import forms

class GeneralForm(forms.Form):
    textWidget=forms.TextInput(attrs={'class':'text ui-widget-content ui-corner-all'})
    textWidgetReadonly=forms.TextInput(attrs={'class':'text ui-widget-content ui-corner-all','readonly':'readonly'})

    name = forms.CharField(label='Configuration Name:', required=True, widget=textWidgetReadonly)
    desc = forms.CharField(label='Description:', required=False, widget=textWidget)
    updated_at = forms.CharField(label='Last Modified On:', required=False, widget=textWidgetReadonly)
    configDN = forms.CharField(widget=forms.HiddenInput())
