from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from slugify import slugify
from django.urls import reverse

class Objects(models.Model):
    NAME = models.CharField(max_length=100,null=False,)
    CREATER = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='Objects')
    CREATE_DT = models.DateField(null=False)

    def __str__(self):
        return self.NAME

class UserObject(models.Model):
    USER = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='UserObject')
    OBJECT = models.ForeignKey(Objects,on_delete=models.CASCADE)

    def __str__(self):
        return  '{}'.format(self.OBJECT)

class Apps(models.Model):
    APP_ID = models.IntegerField(verbose_name='ID',primary_key=True,max_length=10,unique=True,auto_created=True)
    APP_NAME = models.CharField(verbose_name='app名称',max_length=50,null=False)
    START_DT = models.DateField(verbose_name='上线日期',null=False)
    REQUIER_DT = models.DateField(verbose_name='提出需求日期',null=True)
    AUTHOR = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='Apps')

    def __str__(self):
        return 'APP{0}(ID:{1})'.format(self.APP_NAME,self.APP_ID)

class Report(models.Model):
    AUTHOR = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='report')
    TITLE = models.CharField(max_length=200)
    SLUG = models.SlugField(max_length=500)
    OBJECT = models.ForeignKey(Objects,on_delete=models.DO_NOTHING)
    BODY = models.TextField()
    CREATE_DT = models.DateTimeField(default=timezone.now())
    LAST_DT = models.DateTimeField(auto_now=True)
    USER_LIKE = models.ManyToManyField(User, related_name='report_like',blank=True)

    class Meta:
        ordering = ('TITLE',)
        index_together = (('id','SLUG'),)

    def __str__(self):
        return "{}".format(self.TITLE)

    def save(self, *args, **kargs):
        self.SLUG = slugify(self.TITLE)
        super(Report, self).save(*args, **kargs)

    def get_absolute_url(self):
        return reverse('object:report', args=[self.id,self.SLUG])