from django.db import models
from django.contrib.auth.models import User

class Machine(models.Model):
    address = models.IPAddressField('Host Address', unique=True)
    name = models.CharField('Host Name', max_length=200, unique=True)
    os_name = models.CharField('OS', max_length=200)
    location = models.CharField('Location', max_length=1024, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    info = models.CharField('Information', max_length=8192, null=True, blank=True)
    comments = models.CharField('Comments', max_length=1024, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

	#...
    def __unicode__(self):
        return self.name


	
