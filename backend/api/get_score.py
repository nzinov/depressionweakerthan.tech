
# coding: utf-8

# In[50]:


import requests

descr = {
    'P+': 2,
    'P': 1,
    'NEU': 0,
    'N': -1,
    'N+': -2,
    'NONE': 0
}

def api_sentiment_detection(req_type, content):
    url = "https://api.meaningcloud.com/sentiment-2.1"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    payload = ''
    if req_type == 'url':
        payload = "key=3b210fccaba3ae0b6fd61e0164b204e0&lang=auto&txtf=plain&url="
    if req_type == 'txt':
        payload = "key=3b210fccaba3ae0b6fd61e0164b204e0&lang=auto&txtf=plain&txt="
    payload += content

    response = requests.request("POST", url, data=payload, headers=headers)
    resp = response.json()
    score = descr.get(resp.get('score_tag'))
    return score

