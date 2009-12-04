from django import template
import django

register = template.Library()

@register.filter
def status(item):
    if item.enabled == True or item.enabled == 'true':
        return 'enabled'
    else:
        return 'disabled'

@register.filter
def get(item, key, default = '&nbsp;'):
    if item.has_key(key):
        return item[key]
    else:
        return django.utils.safestring.mark_safe(default)
    

