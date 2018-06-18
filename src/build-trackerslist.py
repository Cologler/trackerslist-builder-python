# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

'''
Generate e-book from website.

Usage:
    build-trackerslist CONF DEST [options]

Options:
    --all                       #
    --http                      #
    --https                     #
    --udp                       #
    --ws                        #
'''

import sys
import traceback

import docopt
import requests
import fsoopify

class IServerSource:
    def __init__(self, name, items):
        self._name = name
        self._items = items

class WebServerSource(IServerSource):
    def __init__(self, name, items):
        super().__init__(name, items)
        self._serverlist = None

    def __iter__(self):
        if self._serverlist is None:
            self._serverlist = set()
            for url in self._items:
                response = requests.get(url)
                for line in response.text.splitlines():
                    if line:
                        self._serverlist.add(line)
        for server in self._serverlist:
            yield server

class UserServerSource(IServerSource):
    def __iter__(self):
        for item in self._items:
            yield item

class ServerUrlFilter:
    def __init__(self, opt, srcs):
        self._opt = opt
        self._srcs = srcs

    def get_list(self):
        urls = set()
        opt = self._opt

        for src in self._srcs:
            for url in src:
                if opt['--all']:
                    urls.add(url)
                elif opt['--http'] and url.startswith('http://'):
                    urls.add(url)
                elif opt['--https'] and url.startswith('https://'):
                    urls.add(url)
                elif opt['--udp'] and url.startswith('udp://'):
                    urls.add(url)
                elif opt['--ws'] and url.startswith('ws://'):
                    urls.add(url)

        urllist = list(urls)
        urllist.sort()
        return urllist

def load_conf(opt):
    file = fsoopify.FileInfo(opt['CONF'])
    if not file.is_exists():
        print('')
        exit()
    return file.load()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opt = docopt.docopt(__doc__)
        conf = load_conf(opt)
        srcs = []
        for k, v in conf.get('web', {}).items():
            srcs.append(WebServerSource(k, v))
        for k, v in conf.get('user', {}).items():
            srcs.append(UserServerSource(k, v))
        filter = ServerUrlFilter(opt, srcs)
        result = '\n'.join(filter.get_list())
        fsoopify.FileInfo(opt['DEST']).write_text(result, append=False)
    except Exception: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()
