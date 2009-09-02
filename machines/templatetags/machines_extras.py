from django import template

register = template.Library()


@register.filter
def my(item, user):
    return item.user_id == user.id

@register.filter
def html(text):
    if text == None:
        return ""
    return text.replace("\n", "<br/>")

@register.filter
def take(item, user):
    if item.user_id == user.id:
        return "no_take"
    else:
        return "take"
