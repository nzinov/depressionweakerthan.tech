from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
from .models import User, Url
import json

# Create your views here.
def visit(request):
    data = json.loads(request.body.decode("utf8"))
    user = User.objects.get(pk=data["user"])
    for entry in data["entries"]:
        Url(url=entry["url"], ts=entry["ts"], user=user).save()
    return HttpResponse()

def last_ts(request):
    data = json.loads(request.body.decode("utf8"))
    user = User.objects.get(pk=data["user"])
    ts = user.url_set.order_by("-ts")[0].ts
    print(ts)
    return JsonResponse(dict(ts=ts))