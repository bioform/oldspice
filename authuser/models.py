from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _

class UserProfile(models.Model):
    phone_numer = PhoneNumberField()
    user = models.ForeignKey(User, unique=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    class Admin:
        pass

    def __unicode__(self):
        return "%s, %s" % (self.user.last_name, self.user.first_name)



def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)

models.signals.post_save.connect(user_post_save, sender=User)
