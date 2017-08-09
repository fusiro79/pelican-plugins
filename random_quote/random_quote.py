#!/usr/bin/env python
# coding=utf-8
'''random_quote plugin insert a random quote on each page of a website

This plugin is designed for Pelican 3.4 and later
'''


import random
import sqlite3
from copy import deepcopy
from pelican import signals
from pelican.contents import Article, Page

# Global vars
_QUOTES = {}


def organize_quotes(list):
    '''populate the global variable _QUOTES with the records from SQLite DB'''
    global _QUOTES
    for quote in list:
        lang = quote[2].lower()
        if lang not in _QUOTES:
            _QUOTES[lang] = []  # append the language label
        _QUOTES[lang].append({
                'author': quote[0],
                'web' : quote[1],
                'source' : quote[3],
                'content' : quote[4]
            }
        )


def read_quotes(settings):
    '''connect to the SQLite DB file and read the records'''
    con = sqlite3.connect(settings['RANDOM_QUOTE']['sqlite_db_file'])
    cur = con.cursor()
    cur.execute('SELECT Author.name, Author.web, Quote.lang, ' \
        + 'Quote.source, Quote.content ' \
        + 'FROM Author LEFT JOIN Quote ON Quote.author=Author.id')
    organize_quotes(deepcopy(cur.fetchall()))
    con.close()


def init_data(pelican):
    '''initialize the settings and load a default record for the index pages'''
    if not ('RANDOM_QUOTE' in pelican.settings):
        pelican.settings.setdefault('RANDOM_QUOTE', {
            'sqlite_db_file': 'db\\quotes.sqlite',
            'default_quote' : {
                'author' : 'Tim Berners-Lee',
                'web' : 'https://en.wikipedia.org/wiki/Tim_Berners-Lee',
                'content' : "Il Web è più un'innovazione sociale che " \
                    "un'innovazione tecnica. L'ho progettato perché avesse una " \
                    "ricaduta sociale, perché aiutasse le persone a collaborare, " \
                    "e non come un giocattolo tecnologico. " \
                    "Il fine ultimo del Web è migliorare la nostra esistenza " \
                    "reticolare nel mondo. Di solito noi ci agglutiniamo in " \
                    "famiglie, associazioni e aziende. Ci fidiamo a " \
                    "distanza e sospettiamo appena voltato l'angolo."
            },
        })
    read_quotes(pelican.settings)


def insert_random_quote(content):
    '''select a random quote from _QUOTES and insert it in an Article or Page'''
    global _QUOTES
    if isinstance(content, Article) or isinstance(content, Page):
        if not hasattr(content, 'quote'):
            lang = content.settings['DEFAULT_LANG'].lower()
            i = int(random.uniform(0,len(_QUOTES[lang])-1))
            content.quote = _QUOTES[lang][i]
            content._context['quote'] = content.quote


def register():
    '''inizialize the plugin and call it for each content initialized'''
    signals.initialized.connect(init_data)
    signals.content_object_init.connect(insert_random_quote)
