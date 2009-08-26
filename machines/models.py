from django.db import models
from django.contrib.auth.models import User

class Machine(models.Model):
    address = models.IPAddressField('Host Address')
    name = models.CharField('Host Name', max_length=200)
    os_name = models.CharField('OS', max_length=200)
    location = models.CharField('Location', max_length=1024)
    user = models.ForeignKey(User, blank=True)
	#...
    def __unicode__(self):
        return self.name

	
