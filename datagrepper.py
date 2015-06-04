import copy
import datetime
import collections
import urllib.parse as urlparse

import requests


def _filter_arg(name, multiple=True):
    if multiple:
        def filter_on_arg(self, arg):
            g = copy.deepcopy(self)
            g._args[name] = arg

            return g

        return filter_on_arg
    else:
        def filter_on_arg_mult(self, *args):
            g = copy.deepcopy(self)
            g._args.setdefault(name, [])
            g._args[name].extend(args)

            return g

        return filter_on_arg_mult


class Entry(collections.Mapping):
    __slots__ = ('certificate', 'signature', 'meta',
                 'index', 'timestamp', 'topic', '_msg')


    def __init__(self, json):
        self.certificate = json['certificate']
        self.signature = json['signature']
        self.meta = json.get('meta', {})
        self.index = json['i']
        self.timestamp = datetime.datetime.fromtimestamp(
            int(float(json['timestamp'])))
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
        yield from self._parse_json(json)
        total_pages = json['pages']
        if self._page_limit is not None and total_pages > self._page_limit:
            total_pages = self._page_limit

        pg += 1

        while pg < total_pages:
            g._args['page'] = pg
            json = r.json()
            yield from self._parse_json(json)
            pg += 1

    # formatting
    def with_meta(self, *args):
        g = copy.deepcopy(self)
        g._args.setdefault('meta', [])
        g._args['meta'].extend(args)
        return g

    def grouped(self):
        g = copy.deepcopy(self)
        g._args['grouped'] = 'true'
        return g

    def take(self, pages=None):
        if pages is None:
            raise ValueError("You must specify a number of pages.")

        g = copy.deepcopy(self)
        g._page_limit = pages

        return g

    # TODO(directxman12): with_chrome? with_size?

    # pagination
    def paginate(self, rows=None, order=None, page=None):
        g = copy.deepcopy(self)

        if page is not None:
            g._args['page'] = page

        if rows is not None:
            g._args['rows_per_page'] = rows

        if order is not None:
            g._args['order'] = order

        return g

    # query
    by_user = _filter_arg('user', multiple=False)
    by_package = _filter_arg('package')
    by_category = _filter_arg('category')
    by_topic = _filter_arg('topic')

    containing = _filter_arg('contains')

    without_user = _filter_arg('not_user')
    without_package = _filter_arg('not_package')
    without_category = _filter_arg('not_category')
    without_topic = _filter_arg('not_topic')
