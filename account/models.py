from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True,on_delete=True)
    birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, null=False)
    weixin = models.CharField(max_length=50, null=False)
    company = models.CharField(max_length=50, null=False)
    title = models.CharField(max_length=50, null=True)

    def __str__(self):
        return 'user{}'.format(self.user.username)
