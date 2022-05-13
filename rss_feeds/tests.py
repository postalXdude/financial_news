from django.test import SimpleTestCase
import json
from unittest import mock
from core.celery import app

from rss_feeds.tasks import fetch_rss_from_source_for_symbol
from rss_feeds.exceptions import YahooRSSFeedError


class MockResponse:
    def __init__(self, status_code=200, use_empty=False):
        self.status_code = status_code
        self.text = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <rss version="2.0">
            <channel>
                <copyright>Copyright (c) 2022 Yahoo Inc. All rights reserved.</copyright>
                <description>Latest Financial News for AAPL</description>
                <item>
                    <description>(Bloomberg) -- Baidu Inc. and other Chinese...</description>
                    <guid isPermaLink="false">5cb7c50b-49d3-35c5-ae77-7172824828e0</guid>
                    <link>https://finance.yahoo.com/news/baidu-bulls.html.</link>
                    <pubDate>Fri, 13 May 2022 01:39:29 +0000</pubDate>
                    <title>Baidu Bulls See Index Revamp Curbing 59% Stock Slump</title>
                </item>
                <item>
                    <description>(Bloomberg) -- Apple Inc., confronting...</description>
                    <guid isPermaLink="false">9efd45d3-4c6b-3065-8ab2-cd7fc65b7837</guid>
                    <link>https://finance.yahoo.com/news/apple-extols.html</link>
                    <pubDate>Fri, 13 May 2022 00:42:09 +0000</pubDate>
                    <title>Apple Extols Its Benefits to Retail Staff as It Faces Union Push</title>
                </item>
                <language>en-US</language>
                <lastBuildDate>Fri, 13 May 2022 02:09:38 +0000</lastBuildDate>
                <link>http://finance.yahoo.com/q/h?s=AAPL</link>
                <title>Yahoo! Finance: AAPL News</title>
            </channel>
        </rss>'''
        if use_empty:
            self.text = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <rss version="2.0">
                <channel>
                    <copyright>Copyright (c) 2022 Yahoo Inc. All rights reserved.</copyright>
                    <description>Latest Financial News for AAPL</description>
                    <language>en-US</language>
                    <lastBuildDate>Fri, 13 May 2022 02:09:38 +0000</lastBuildDate>
                    <link>http://finance.yahoo.com/q/h?s=AAPL</link>
                    <title>Yahoo! Finance: AAPL News</title>
                </channel>
            </rss>'''


class TestFetchRSSFeed(SimpleTestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    @mock.patch('rss_feeds.tasks.NewsSerializer')
    @mock.patch('requests.get', return_value=MockResponse())
    def test_fetch_rss_from_source_for_symbol(self, mock_response, mock_serializer):
        # Run task.
        fetch_rss_from_source_for_symbol('AAPL')
        self.assertEqual(mock_response.call_count, 1)
        # Check args.
        args = mock_response.call_args.args
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0], 'https://feeds.finance.yahoo.com/rss/2.0/headline')
        # Check kwargs.
        kwargs = mock_response.call_args.kwargs
        self.assertListEqual(list(kwargs.keys()), ['params', 'headers'])
        self.assertDictEqual(kwargs['params'], {'s': 'AAPL'})
        # User agent is dynamic.
        self.assertListEqual(list(kwargs['headers'].keys()), ['user-agent'])
        # Check parsed data.
        self.assertEqual(mock_serializer.call_count, 1)
        parsed_data = mock_serializer.call_args.kwargs['data']
        actual = json.dumps(
            parsed_data,
            indent=4,
            sort_keys=True,
            default=str
        )
        expected = \
'''[
    {
        "description": "(Bloomberg) -- Baidu Inc. and other Chinese...",
        "guid": "5cb7c50b-49d3-35c5-ae77-7172824828e0",
        "link": "https://finance.yahoo.com/news/baidu-bulls.html.",
        "published_on": "2022-05-13 01:39:29+00:00",
        "symbol": "AAPL",
        "title": "Baidu Bulls See Index Revamp Curbing 59% Stock Slump"
    },
    {
        "description": "(Bloomberg) -- Apple Inc., confronting...",
        "guid": "9efd45d3-4c6b-3065-8ab2-cd7fc65b7837",
        "link": "https://finance.yahoo.com/news/apple-extols.html",
        "published_on": "2022-05-13 00:42:09+00:00",
        "symbol": "AAPL",
        "title": "Apple Extols Its Benefits to Retail Staff as It Faces Union Push"
    }
]'''
        self.assertEqual(actual, expected)

    @mock.patch('rss_feeds.tasks.NewsSerializer')
    @mock.patch('requests.get', return_value=MockResponse(use_empty=True))
    def test_fetch_rss_from_source_for_symbol_no_items(self, _, mock_serializer):
        # Run task.
        fetch_rss_from_source_for_symbol('AAPL')
        self.assertEqual(mock_serializer.call_count, 0)

    @mock.patch('requests.get', return_value=MockResponse(status_code=666))
    def test_fetch_rss_from_source_for_symbol_yahoo_error(self, _):
        self.assertRaises(YahooRSSFeedError, fetch_rss_from_source_for_symbol, 'AAPL')
