import unittest
from unittest import mock
import datetime
import json
import copy

import requests

import datanozzle as dg

# TODO(directxman12): do we need to explicity convert timezone info
# for datetimes

class GrepperTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(GrepperTestCase, cls).setUpClass()
        with open('./test-data.json') as f:
            cls._SAMPLE_DATA = json.load(f)

    def setUp(self):
        super(GrepperTestCase, self).setUp()

        self._sample_pages = self._SAMPLE_DATA['with_meta']
        self._called_with_params = []

        def return_json(url, params):
            res = mock.Mock()
            res.json.return_value = (
                self._sample_pages[params.get('page', 1) - 1])
            # copy the params since we change it to increment pages
            self._called_with_params.append(copy.deepcopy(params))
            return res

        requests.get = mock.Mock(side_effect=return_json)
        dg.requests = requests

    # TODO(directxman12): test reset

    def test_iteration(self):
        q = dg.Grepper().by_user('sross').ascending
        q = q.with_meta('title', 'objects').take(2).paginate(5)

        q_iter = iter(q)
        entry1 = next(q_iter)

        requests.get.assert_called_once()
        self.assertIsInstance(entry1, dg.Entry)

        requests.get.reset_mock()
        res = list(q)
        self.assertEqual(len(res), 10)
        self.assertEqual(requests.get.call_count, 2)
        self.assertEqual(self._called_with_params[1].get('page', 1), 1)
        self.assertEqual(self._called_with_params[2].get('page'), 2)
        self.assertNotEqual(res[0], res[5])

    def test_chaining(self):
        q1 = dg.Grepper().take(1)
        q2 = q1.by_user('some_user')
        q3 = q2.by_topic('some_topic')
        q4 = q3.by_user('other_user')

        list(q1)
        self.assertEqual(requests.get.call_args[1]['params'], {})

        requests.get.reset_mock()
        list(q2)
        self.assertEqual(requests.get.call_args[1]['params'],
                         {'user': ['some_user']})

        requests.get.reset_mock()
        list(q3)
        self.assertEqual(requests.get.call_args[1]['params'],
                         {'user': ['some_user'], 'topic': ['some_topic']})

        requests.get.reset_mock()
        list(q4)
        self.assertEqual(requests.get.call_args[1]['params'],
                         {'user': ['some_user', 'other_user'],
                          'topic': ['some_topic']})

    def test_take(self):
        g = dg.Grepper().paginate(5).take(1)
        self.assertEqual(len(list(g)), 5)

    def test_by_user(self):
        g = dg.Grepper().by_user('user1', 'user2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['user'],
                         ['user1', 'user2'])

    def test_by_package(self):
        g = dg.Grepper().by_package('package1', 'package2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['package'],
                         ['package1', 'package2'])

    def test_by_category(self):
        g = dg.Grepper().by_category('category1', 'category2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['category'],
                         ['category1', 'category2'])

    def test_by_topic(self):
        g = dg.Grepper().by_topic('topic1', 'topic2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['topic'],
                         ['topic1', 'topic2'])

    def test_containing(self):
        g = dg.Grepper().containing('kw1', 'kw2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['contains'],
                         ['kw1', 'kw2'])

    def test_without_user(self):
        g = dg.Grepper().without_user('user1', 'user2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['not_user'],
                         ['user1', 'user2'])

    def test_without_package(self):
        g = dg.Grepper().without_package('package1', 'package2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['not_package'],
                         ['package1', 'package2'])

    def test_without_category(self):
        g = dg.Grepper().without_category('category1', 'category2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['not_category'],
                         ['category1', 'category2'])

    def test_without_topic(self):
        g = dg.Grepper().without_topic('topic1', 'topic2')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['not_topic'],
                         ['topic1', 'topic2'])

    def test_with_meta(self):
        g = dg.Grepper().with_meta('title', 'packages')
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['meta'],
                         ['title', 'packages'])

    def test_ascending(self):
        g = dg.Grepper().ascending
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['order'], 'asc')

    def test_descending(self):
        g = dg.Grepper().descending
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['order'], 'desc')

    def test_grouped(self):
        g = dg.Grepper().grouped
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['grouped'],
                         'true')

    def test_skip(self):
        g = dg.Grepper().skip(1)
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['page'], 2)

    def test_paginate(self):
        g = dg.Grepper().paginate(5)
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['rows_per_page'],
                         5)

    def test_starting_at(self):
        now = datetime.datetime.now()
        g = dg.Grepper().starting_at(now)
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['start'],
                         now.timestamp())

    def test_ending_at(self):
        now = datetime.datetime.now()
        g = dg.Grepper().ending_at(now)
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['end'],
                         now.timestamp())

    def test_delta_seconds(self):
        g = dg.Grepper().delta_seconds(10)
        list(g)
        self.assertEqual(requests.get.call_args[1]['params']['delta'],
                         10)

class EntryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(EntryTestCase, cls).setUpClass()
        with open('./test-data.json') as f:
            cls._SAMPLE_DATA = json.load(f)

    def setUp(self):
        super(EntryTestCase, self).setUp()
        self._json_blob = (
            self._SAMPLE_DATA['without_meta'][0]['raw_messages'][0])
        self._json_blob_with_meta = (
            self._SAMPLE_DATA['with_meta'][0]['raw_messages'][0])

    def test_basic_data_parsing(self):
        e = dg.Entry(self._json_blob)

        self.assertEqual(e.certificate, 'some_certificate')
        self.assertEqual(e.signature, 'some_signature')
        self.assertEqual(e.meta, {})
        self.assertEqual(e.index, 1)
        self.assertEqual(e.timestamp,
                         datetime.datetime(2013, 6, 13, 17, 24, 11))
        self.assertEqual(e.topic, 'org.fedoraproject.prod.fas.user.create')

    def test_message_access(self):
        e = dg.Entry(self._json_blob)
        self.assertEqual(e['user'], 'sross')

    def test_meta_added_when_present(self):
        e = dg.Entry(self._json_blob_with_meta)
        self.assertEqual(e.meta['title'], 'fas.user.create')
