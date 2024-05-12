from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse
import os
from dotenv import load_dotenv, dotenv_values 
from supabase import create_client, Client
from time import strftime, gmtime
import feedparser

load_dotenv() 

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url=url, supabase_key=key)

app = Flask(__name__)
api = Api(app)

Podcasts = {
    'Oral Presentations': {'title': 'Oral Presentations',
        'updated_at': 'Thu, 09 May 2024 13:46:18 -0400',
        'rss_link': 'https://feeds.buzzsprout.com/758030.rss',
        'description': "A low pressure learning podcast. Hosted by a guy who sounds like he'd offer you whippets at a tailgate.",
        'website': 'https://www.buzzsprout.com/758030',
        'author': 'Chris Wood',
        'image': 'https://storage.buzzsprout.com/prficnvd2o68s9e3c1nxtjyuupxe?.jpg',
        # 'episode_list': []
        "user_id": "troll123"
        },
    "WAR MODE": {'title': 'WAR MODE',
        'updated_at': 'Tue, 07 May 2024 14:35:54 +0000',
        'rss_link': 'https://feeds.libsyn.com/263729/rss',
        'description': 'This is the official WAR MODE podcast please enjoy\n\nPatreon- https://www.patreon.com/WARMODE',
        'website': 'http://warmode.libsyn.com/website',
        'author': 'william mccusker',
        'image': 'https://static.libsyn.com/p/assets/3/b/1/b/3b1be5b6938e5582/WAR_MODE_REAL_BOY.jpg',
        # 'episode_list': []
        "user_id": "troll123"
        }
}

def abort_if_todo_doesnt_exist(podcast):
    if podcast not in Podcasts:
        abort(404, message="Podcast {} doesn't exist".format(podcast))

def ParseRSSFeed(rss: str):
    feed = feedparser.parse(rss)
    episodeList = []
    length = len(feed.entries)
    for x in range(length):
        episode = {}
        episode['title'] = feed.entries[x].title
        for i in range(len(feed.entries[x].enclosures)):
            if feed.entries[x].enclosures[i].type == "audio/mpeg":
                episode['link'] = feed.entries[x].enclosures[i].href
                episode['length'] = strftime("%H:%M:%S", gmtime(int(feed.entries[x].enclosures[i].length)))
            if "itunes_episode" in feed.entries[x]:
                episode['episode_number'] = int(feed.entries[x].itunes_episode)
        episodeList.append(episode)
    if "subtitle_detail" in feed.feed:
        podcast = {
            "title": feed.feed.title,
            "updated_at": feed.feed.updated,
            "rss_link": rss,
            "description": feed.feed.subtitle_detail['value'],
            "website": feed.feed.link,
            "author":  feed.feed.author,
            "image": feed.feed.image['href'],
            "episode_list": episodeList
        }
    elif "summary_detail" in feed.feed:
        podcast = {
            "title": feed.feed.title,
            "updated_at": feed.feed.updated,
            "rss_link": rss,
            "description": feed.feed.summary_detail['value'],
            "website": feed.feed.link,
            "author":  feed.feed.author,
            "image": feed.feed.image['href'],
            "episode_list": episodeList
        }
    return podcast

parser = reqparse.RequestParser()
parser.add_argument('user_id')
parser.add_argument('rss')

class Podcast(Resource):
    def post(self):
        args = parser.parse_args()
        podcast = ParseRSSFeed(args['rss'])
        podcast['user_id'] = args['user_id']
        data, count = supabase.table('podcast').insert(podcast).execute()
        return data[1][0], 201

class PodcastListForUser(Resource):
    def get(self, user_id):
        data, count = supabase.table('podcast').select('*').eq('user_id', user_id).execute()
        return data[1]


api.add_resource(Podcast, "/podcasts")
api.add_resource(PodcastListForUser, "/podcasts/<user_id>")

if __name__ == '__main__':
    app.run(debug=True, threaded=True)