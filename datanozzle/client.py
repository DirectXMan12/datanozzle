# datagrepper-client -- A Python client for datagrepper
# Copyright (C) 2015 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import copy
import datetime
import collections
import urllib.parse as urlparse

import requests


def _filter_arg(name, multiple=True):
    if multiple:
        def filter_on_arg_mult(self, *args):
            g = copy.deepcopy(self)
            g._args.setdefault(name, [])
            g._args[name].extend(args)

            return g

        return filter_on_arg_mult
    else:
        def filter_on_arg(self, arg):
            g = copy.deepcopy(self)
            g._args[name] = arg

            return g

        return filter_on_arg


class Entry(collections.Mapping):
    __slots__ = ('certificate', 'signature', 'meta',
                 'index', 'timestamp', 'topic', '_msg')

    def __init__(self, json):
        self.certificate = json['certificate']
        self.signature = json['signature']
        self.meta = json.get('meta', {})
        self.index = json['i']
        self.timestamp = datetime.datetime.fromtimestamp(
            float(json['timestamp']))
        self.topic = json['topic']

        self._msg = json['msg']

    def __getitem__(self, key):
        return self._msg[key]

    def __iter__(self):
        return iter(self._msg)

    def __len__(self):
        return len(self)

    def __repr__(self):
        return ('<Entry[{topic} -- {ind} @ {ts}] {msg}>').format(
            topic=self.topic, ind=self.index,
            cert=self.certificate, sig=self.signature,
            ts=self.timestamp, msg=self._msg)

    # TODO(directxman12): write from_id


class Grepper(object):
    def __init__(self, target='https://apps.fedoraproject.org/datagrepper/'):
        self._base = target
        if self._base[-1] != '/':
            self._base += '/'

        self._args = {}
        self._page_limit = None

    def _req(self):
        return requests.get(self._base + '/raw', params=self._args)

    def _parse_json(self, json):
        for msg in json['raw_messages']:
            yield Entry(msg)

    # TODO(directxman12): define a __repr__
    # def __repr__(self):

    def __iter__(self):
        g = copy.deepcopy(self)
        pg = g._args.get('page', 1)
        r = g._req()

        json = r.json()
        yield from g._parse_json(json)
        total_pages = json['pages']
        if g._page_limit is not None and total_pages > g._page_limit:
            total_pages = g._page_limit

        pg += 1

        max_pg = total_pages + 1
        while pg < max_pg:
            g._args['page'] = pg
            r = g._req()
            json = r.json()
            yield from g._parse_json(json)
            pg += 1

    # formatting
    def take(self, pages):
        if pages is None:
            raise ValueError("You must specify a number of pages.")

        g = copy.deepcopy(self)
        g._page_limit = pages

        return g

    def skip(self, pages):
        if pages is None:
            pages = 0

        g = copy.deepcopy(self)
        g._args['page'] = pages + 1

        return g

    # TODO(directxman12): with_chrome? with_size?

    @property
    def ascending(self):
        g = copy.deepcopy(self)
        g._args['order'] = 'asc'
        return g

    @property
    def descending(self):
        g = copy.deepcopy(self)
        g._args['order'] = 'desc'
        return g

    @property
    def grouped(self):
        g = copy.deepcopy(self)
        g._args['grouped'] = 'true'
        return g

    # pagination
    def paginate(self, rows):
        g = copy.deepcopy(self)
        g._args['rows_per_page'] = rows
        return g

    def starting_at(self, start):
        if isinstance(start, datetime.datetime):
            start = start.timestamp()

        g = copy.deepcopy(self)
        g._args['start'] = start
        return g

    def ending_at(self, end):
        if isinstance(end, datetime.datetime):
            end = end.timestamp()

        g = copy.deepcopy(self)
        g._args['end'] = end
        return g

    def delta_seconds(self, delta):
        g = copy.deepcopy(self)
        g._args['delta'] = delta
        return g

    _ALT_NAMES = {'containing': 'contains', 'rows': 'rows_per_page',
                  'paginate': 'rows_per_page', 'skip': 'page',
                  'starting_at': 'start', 'ending_at': 'end',
                  'delta_seconds': 'delta'}

    def reset(self, name):
        g = copy.deepcopy(self)
        if name == 'take':
            g._page_limit = None
        else:
            name = self._ALT_NAMES.get(name, name)
            del g._args[name]

        return g

    # query
    by_user = _filter_arg('user')
    by_package = _filter_arg('package')
    by_category = _filter_arg('category')
    by_topic = _filter_arg('topic')

    containing = _filter_arg('contains')

    without_user = _filter_arg('not_user')
    without_package = _filter_arg('not_package')
    without_category = _filter_arg('not_category')
    without_topic = _filter_arg('not_topic')

    with_meta = _filter_arg('meta')
