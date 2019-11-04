from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(max_length=32, unique=True)
    email = models.CharField(max_length=32, unique=True)
    nid = models.AutoField(primary_key=True)
    password = models.CharField(max_length=32)
    ctime =models.DateTimeField()


class SendMsg(models.Model):
    nid = models.AutoField(primary_key=True)
    email = models.CharField(max_length=32, db_index=True)
    times = models.IntegerField(default=0)
    ctime = models.DateTimeField()
    email_code = models.CharField(max_length=6, default='')


