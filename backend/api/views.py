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
    print(request.body)
    data = json.loads(request.body.decode("utf8"))
    user = User.objects.get(pk=data["user"])
    urls = user.url_set.order_by("-ts")
    ts = 0
    if urls:
        ts = urls[0].ts
    print(ts)
    return JsonResponse(dict(ts=ts))
