from flask import Flask
from flask import Response

from flask import request
from flask import redirect
from flask import render_template

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import config
import random
import json
import pymongo

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

dictionary = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4',
    '5', '6', '7', '8', '9', '0'
]
dictionary_length = len(dictionary)

mongo_client = pymongo.MongoClient(config.mongo_uri)
collection = mongo_client.get_database('url-shortener').get_collection('urls')


@app.route('/')
def main_route():
    return render_template('index.html')


@app.route('/create', methods=['POST'])
@limiter.limit("2/minute")
def create_route():
    data = request.get_json(force=True)
    shortened_url = ""

    if not data['url']:
        return Response(status=400)

    url = data['url']
    db_url = collection.find_one({
        'url': url
    })

    if db_url is not None:
        return json.dumps({
            'shortened_url': db_url['shortened_url']
        })

    for i in range(12):
        shortened_url += dictionary[random.randint(0, dictionary_length)]

    collection.insert_one({
            'shortened_url': shortened_url,
            'url': url
        })

    return json.dumps({
        'shortened_url': shortened_url
    })


@app.route('/url/<name>')
def shortened_url_route(name):
    data = collection.find_one({
        'shortened_url': name
    })

    if data is None:
        return '<h2>Error</h2>\n Unable to find any URL with that identifier.'
    return redirect(data['url'])


if __name__ == '__main__':
    app.run(host=config.hostname, port=config.port, debug=False)
