
# coding: utf-8

# In[430]:


import requests
import re
from requests_html import HTMLSession, HTML
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

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
    
    alpha = 2.3
    
    payload = ''
    if req_type == 'url':
        payload = "key=3b210fccaba3ae0b6fd61e0164b204e0&lang=auto&txtf=plain&url="
    if req_type == 'txt':
        payload = "key=3b210fccaba3ae0b6fd61e0164b204e0&lang=auto&txtf=plain&txt="
    payload += content

    response = requests.request("POST", url, data=payload, headers=headers)
    resp = response.json()
    score = descr.get(resp.get('score_tag'))
    if resp.get('confidence'):
        conf = (int(resp.get('confidence')) / 100) ** alpha
        score *= conf
    if resp.get('irony') and resp.get('irony') == 'IRONIC':
        score = 0
    return score


def get_tweets(user, pages=25):
    """Gets tweets for a given user, via the Twitter frontend API."""
    
    session = HTMLSession()

    url = f'https://twitter.com/i/profiles/show/{user}/timeline/tweets?include_available_features=1&include_entities=1&include_new_items_bar=true'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': f'https://twitter.com/{user}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'X-Twitter-Active-User': 'yes',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def gen_tweets(pages):
        r = session.get(url, headers=headers)

        while pages > 0:
            try:
                html = HTML(html=r.json()['items_html'],
                            url='bunk', default_encoding='utf-8')
            except KeyError:
                raise ValueError(
                    f'Oops! Either "{user}" does not exist or is private.')

            comma = ","
            dot = "."
            tweets = []
            for tweet in html.find('.stream-item'):
                try:
                    text = tweet.find('.tweet-text')[0].full_text
                    tweetId = tweet.find(
                        '.js-permalink')[0].attrs['data-conversation-id']
                    time = datetime.fromtimestamp(
                        int(tweet.find('._timestamp')[0].attrs['data-time-ms'])/1000.0)
                    interactions = [x.text for x in tweet.find(
                        '.ProfileTweet-actionCount')]
                    replies = int(interactions[0].split(" ")[0].replace(comma, "").replace(dot,""))
                    retweets = int(interactions[1].split(" ")[
                                   0].replace(comma, "").replace(dot,""))
                    likes = int(interactions[2].split(" ")[0].replace(comma, "").replace(dot,""))
                    hashtags = [hashtag_node.full_text for hashtag_node in tweet.find('.twitter-hashtag')]
                    urls = [url_node.attrs['data-expanded-url'] for url_node in tweet.find('a.twitter-timeline-link:not(.u-hidden)')]
                    photos = [photo_node.attrs['data-image-url'] for photo_node in tweet.find('.AdaptiveMedia-photoContainer')]

                    videos = []
                    video_nodes = tweet.find(".PlayableMedia-player")
                    for node in video_nodes:
                        styles = node.attrs['style'].split()
                        for style in styles:
                            if style.startswith('background'):
                                tmp = style.split('/')[-1]
                                video_id = tmp[:tmp.index('.jpg')]
                                videos.append({'id': video_id})
                    tweets.append({'tweetId': tweetId, 'time': time, 'text': text,
                                   'replies': replies, 'retweets': retweets, 'likes': likes, 
                                   'entries': {
                                        'hashtags': hashtags, 'urls': urls,
                                        'photos': photos, 'videos': videos
                                    }
                                   })
                except:
                    continue

            last_tweet = html.find('.stream-item')[-1].attrs['data-item-id']

            for tweet in tweets:
                if tweet:
                    tweet['text'] = re.sub('http', ' http', tweet['text'], 1)
                    yield tweet

            r = session.get(
                url, params = {'max_position': last_tweet}, headers = headers)
            pages += -1

    yield from gen_tweets(pages)


def window(size):
    return np.ones(size) / float(size)


def twitter_score_info(user_name, deep_days=30):
    twitter_scores = []
    twitter_times = []
    
    last_tweet_id = 0

    today_date = datetime.now()
    check_date = today_date - timedelta(deep_days=30)
    for ind, tweet in enumerate(get_tweets(user_name, pages=20)):
        if tweet and tweet['time'] > check_date and ind > 0:
            if ind == 1:
                last_tweet_id = tweet['tweetId']
            msg = tweet['text']
            #print(msg)
            cur_score = api_sentiment_detection('txt', re.sub(r'[^A-Za-z0-9\,\?\!\#\$\%\&\'\*\+\-\.\^\_\`\|\~\:]', ' ', msg))
            if cur_score and tweet['time']:
                twitter_scores.append(cur_score)
                twitter_times.append(tweet['time'])
    
    avg_scores = np.mean(twitter_scores)
    
    ser_scores = pd.Series(twitter_scores)
    ser_scores.index = twitter_times
    avg_day_score = ser_scores.groupby(ser_scores.index.day).mean()
    
    avg_week_score = np.convolve(avg_day_score, window(7))
    
    res = {}
    res['avg_month_score'] = avg_scores
    res['avg_week_score'] = avg_week_score
    res['avg_day_score'] = avg_day_score.values
    res['last_tweet_id'] = last_tweet_id
    return res


def browser_history_score_info(history, deep_days=30):
    br_hist = json.loads(history)
    urls = [br_hist[i].get('url') for i in range(len(br_hist))]
    times = [datetime.fromtimestamp(float(br_hist[i].get('ts')) / 1000) for i in range(len(br_hist))]
    
    br_hist_scores = []
    br_hist_times = []
    
    last_ts = 0

    today_date = datetime.now()
    check_date = today_date - timedelta(deep_days=30)
    
    for ind, url in enumerate(urls[:100]):
        if times[ind] > check_date:
            cur_score = api_sentiment_detection('url', url)
        if cur_score:
            br_hist_scores.append(cur_score)
            br_hist_times.append(times[ind])
    
    avg_scores = np.mean(br_hist_scores)
    
    ser_scores = pd.Series(br_hist_scores)
    ser_scores.index = br_hist_times
    avg_day_score = ser_scores.groupby(ser_scores.index.day).mean()
    
    avg_week_score = np.convolve(avg_day_score, window(7))
    
    res = {}
    res['avg_month_score'] = avg_scores
    res['avg_week_score'] = avg_week_score
    res['avg_day_score'] = avg_day_score.values
    res['last_url_ts'] = last_ts
    return res


def is_depressed(scores):
    last_week_avg_score = np.mean(scores[-7:])
    all_avg_score = np.mean(scores)
    if last_week_avg_score < -0.25:
        return True
    else:
        if last_week_avg_score < -0.1 and all_avg_score > 0:
            return True
        else:
            return False


# In[317]:


#user_name = 'HackneyAbbott'
#score_info = twitter_score_info(user_name)


# In[318]:


#score_info


# In[319]:


#print('average score:', score_info.get('avg_month_score'))
#plt.plot(score_info.get('avg_week_score'))

