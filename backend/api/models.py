from django.db import models

# Create your models here.
class User(models.Model):
    activated = models.BooleanField(default=False)
    username = models.TextField()
    user_id = models.IntegerField(null=True)
    trusted = models.ManyToManyField("User")
    
class Url(models.Model):
    url = models.TextField()
    ts = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
