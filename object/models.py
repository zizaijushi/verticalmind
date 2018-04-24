from django.db import models
from django.contrib.auth.models import User

class Objects(models.Model):
    NAME = models.CharField(max_length=100,null=False,)
    CREATER = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    CREATE_DT = models.DateField(null=False)

    def __str__(self):
        return self.NAME

class UserObject(models.Model):
    USER = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    OBJECT = models.ForeignKey(Objects,on_delete=models.CASCADE)

    def __str__(self):
        return  self.OBJECT

class Apps(models.Model):
    APP_ID = models.IntegerField(verbose_name='ID',primary_key=True,max_length=10,unique=True,auto_created=True)
    APP_NAME = models.CharField(verbose_name='app名称',max_length=50,null=False)
    START_DT = models.DateField(verbose_name='上线日期',null=False)
    REQUIER_DT = models.DateField(verbose_name='提出需求日期',null=True)
    AUTHOR = models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name='作者')

    def __str__(self):
        return 'APP{0}(ID:{1})'.format(self.APP_NAME,self.APP_ID)
