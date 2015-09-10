# -*- coding: utf-8 -*-
import re
import requests
import argparse

from flask import Flask, request, render_template

from jinja2 import Markup
from jinja2.filters import do_striptags

from BeautifulSoup import BeautifulSoup

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['HOST'] = 'localhost'
app.config['PORT'] = 5000
app.config['HOMEPAGE'] = 'http://habrahabr.ru/'


@app.route('/')
def hello_world():
    website_url = request.args.get('q', None)

    if not website_url:
        website_url = app.config['HOMEPAGE']

    try:
        res = requests.get(website_url)
        content = res.text
        words = get_six_symbol_words(content)

        for word in words:
            replace_with = u'%s™' % word
            content = re.sub(r'%s' % word, replace_with, content)
    except requests.exceptions.RequestException:
        content = 'Malformed URL, please give valid one.'
        print('{} failed'.format(website_url))

    return render_template('index.html', content=Markup(content))


def get_six_symbol_words(content):
    chunks = do_striptags(get_contents(content)).split(' ')
    return {x for x in chunks if len(x) == 6}


def get_contents(content):
    soup = BeautifulSoup(content)
    to_extract = soup.findAll('body')

    for script in soup.findAll('script'):
        script.extract()

    for script in soup.findAll('style'):
        script.extract()

    for body in to_extract:
        return body.getText()

    return ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup defaults')

    parser.add_argument('--host', dest='host',
                        default=app.config['HOST'],
                        help='Default hostname')

    parser.add_argument('--port', dest='port',
                        type=int,
                        default=app.config['PORT'],
                        help='Default port')

    arguments = parser.parse_args()

    app.run(host=arguments.host, port=arguments.port)
