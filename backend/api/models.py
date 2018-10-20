from django.db import models


# Create your models here.
class User(models.Model):
    activated = models.BooleanField(default=False)
    username = models.TextField()
    user_id = models.IntegerField(null=True)
    twitter_login = models.TextField(null=True)
    trusted = models.ManyToManyField("User")
    twitter_month_score = models.FloatField(null=True)
    twitter_week_score = models.FloatField(null=True)
    url_month_score = models.FloatField(null=True)
    url_week_score = models.FloatField(null=True)


class Url(models.Model):
    url = models.TextField()
    ts = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
