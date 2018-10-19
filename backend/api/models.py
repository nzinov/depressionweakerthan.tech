from django.db import models

# Create your models here.
class User(models.Model):
    activated = models.BooleanField(default=False)
    username = models.TextField(primary_key=True)
    trusted = models.ManyToManyField("User")
    
class Url(models.Model):
    url = models.TextField()
    ts = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)